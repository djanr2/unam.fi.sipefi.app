import unicodedata
import os
import re
import json

from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph




from sipefi_apps.tomo_ii.reporte.ConsultasPDF import ConsultasPDF

BLANCO = colors.white
NEGRO = colors.black
GRIS_SUAVE = colors.HexColor("#F3F4F6")
watermark_on = True  # o False para desactivarla

def generarPdf(request):
    obj = json.loads(request.POST.get("obj", ""))
    perfil= int(obj['idPerfil'])
    licenciatura= int(obj['idLic'])
    asignatura = int(obj['idSolicitud'])

    consultas = ConsultasPDF()
    '''
    [('Ingeniería en Computación', 'ASIGNATURA', 'CXXXXXX', 8, 4, 'Ingeniería Aplicada', 'Curso práctico', 'Práctico', 'Obligatoria', 
    'P+, P+', 1, 2, 16, 32, 'El alumno reforzará los conceptos de trigonometría para lograr una mejor comprensión del álgebra.')]
    '''
    id_licenciatura = licenciatura
    id_asignatura = asignatura
    id_perfil = perfil
    # LICENCIATURA
    asignatura_inf = consultas.get_informacion_asignatura(id_licenciatura, id_asignatura)
    licenciatura_pdf = asignatura_inf[0][0] if asignatura_inf and asignatura_inf[0][0] is not None else ""
    asignatura_pdf = asignatura_inf[0][1] if asignatura_inf and asignatura_inf[0][1] is not None else ""
    clave_pdf = asignatura_inf[0][2] if asignatura_inf and asignatura_inf[0][2] is not None else ""
    semestre_pdf = str(asignatura_inf[0][3] if asignatura_inf and asignatura_inf[0][3] is not None else "")
    creditos_pdf =  str(asignatura_inf[0][4] if asignatura_inf and asignatura_inf[0][4] is not None else "")
    area_conocimiento_pdf = asignatura_inf[0][5] if asignatura_inf and asignatura_inf[0][5] is not None else ""
    modalidad_pdf =  asignatura_inf[0][6] if asignatura_inf and asignatura_inf[0][6] is not None else ""
    tipo_pdf = asignatura_inf[0][7] if asignatura_inf and asignatura_inf[0][7] is not None else ""
    caracter_pdf = asignatura_inf[0][8] if asignatura_inf and asignatura_inf[0][8] is not None else ""
    valor_practico_pdf = asignatura_inf[0][9] if asignatura_inf and asignatura_inf[0][9] else ""
    horas_teoricas_semanales_pdf = asignatura_inf[0][10] if asignatura_inf and asignatura_inf[0][10] is not None else 0
    horas_practicas_semanales_pdf = asignatura_inf[0][11] if asignatura_inf and asignatura_inf[0][11] is not None else 0
    horas_teoricas_semestrales_pdf = asignatura_inf[0][12] if asignatura_inf and asignatura_inf[0][12] is not None else 0
    horas_practicas_semestrales_pdf = asignatura_inf[0][13] if asignatura_inf and asignatura_inf[0][13] is not None else 0
    objetivo_pdf =  asignatura_inf[0][14] if asignatura_inf and asignatura_inf[0][14] is not None else ""
    formacion_integral_pdf =  asignatura_inf[0][15] if asignatura_inf and asignatura_inf[0][15] is not None else ""
    perfil_profesiografico_pdf = asignatura_inf[0][16] if asignatura_inf and asignatura_inf[0][16] is not None else ""
    color_hex = asignatura_inf[0][17] if asignatura_inf and asignatura_inf[0][17] is not None else "#F3F4F6"

    color_pdf = colors.HexColor(color_hex)

    seriaciones_inf = consultas.get_seriaciones(id_licenciatura,id_asignatura)
    seriacion_antecedente_pdf = seriaciones_inf[0][0] if seriaciones_inf and seriaciones_inf[0][0] is not None else ""
    seriacion_consecuente_pdf = seriaciones_inf[0][1] if seriaciones_inf and seriaciones_inf[0][1] is not None else ""

    temario_inf = consultas.get_temario(id_asignatura)

    resumen_temario_inf = consultas.get_resumen_temario(id_asignatura)
    suma_horas_temario_pdf = resumen_temario_inf[0][0] if resumen_temario_inf and resumen_temario_inf[0][0] is not None else ""
    actividades_practicas_horas_pdf =resumen_temario_inf[0][1] if resumen_temario_inf and resumen_temario_inf[0][1] is not None else ""


    subtemas_inf = consultas.get_subtemas(id_asignatura)

    bibliografia_basica_inf = consultas.get_bibliografia_basica(id_asignatura)
    bibliografia_basica_pdf = []
    temas_bibliografia_basica_pdf = []

    for fila in bibliografia_basica_inf:
        _, _, _, _, _, _, _, _, temas = fila
        format_string = get_bibliografia_str(fila)
        bibliografia_basica_pdf.append(format_string)
        temas_bibliografia_basica_pdf.append(temas)

    bibliografia_complementaria_inf = consultas.get_bibliografia_complementaria(id_asignatura)
    bibliografia_complementaria_pdf = []
    temas_bibliografia_complementaria_pdf = []

    for fila in bibliografia_complementaria_inf:
        _, _, _, _, _, _, _, _, temas = fila
        format_string = get_bibliografia_str(fila)
        bibliografia_complementaria_pdf.append(format_string)
        temas_bibliografia_complementaria_pdf.append(temas)

    estrategias_didacticas_inf = consultas.get_estrategias_didacticas(id_asignatura)
    formas_evaluacion_diagnostica_inf = consultas.get_formas_evaluacion(id_asignatura, 'Diagnóstica')
    formas_evaluacion_formativa_inf = consultas.get_formas_evaluacion(id_asignatura, 'Formativa')
    formas_evaluacion_sumativa_inf = consultas.get_formas_evaluacion(id_asignatura, 'Sumativa')

    nombre_archivo_pdf = normalize_name(asignatura_pdf)

    is_documento_oficial_inf = consultas.get_is_documento_ofical_by_perfil(id_perfil)
    is_documento_oficial_pdf = is_documento_oficial_inf[0][0] if is_documento_oficial_inf and is_documento_oficial_inf[0][0] is not None else ""

    if valor_practico_pdf == '':
        valor_practico_pdf = 'Ninguno'
    if formacion_integral_pdf == '':
        formacion_integral_pdf = 'Ninguna'
    if actividades_practicas_horas_pdf == '':
        actividades_practicas_horas_pdf = 0
    if suma_horas_temario_pdf == '':
        suma_horas_temario_pdf = 0

    if is_documento_oficial_pdf == 1 :
        global watermark_on
        watermark_on= False

    subtemas_por_id = {}  # dict auxiliar para juntar las listas
    for r in subtemas_inf:
        id_bloque = r[0]
        sub_id = r[1]
        descripcion = r[2]
        # armar el "objeto" subtema como arreglo/tupla
        subtema = (sub_id, descripcion)
        if id_bloque in subtemas_por_id:
            subtemas_por_id[id_bloque].append(subtema)
        else:
            subtemas_por_id[id_bloque] = [subtema]

    temas_con_subtemas = []
    for t in temario_inf:
        id_bloque = t[0]
        nombre = t[1]
        objetivo = t[3]
        lista_subtemas = subtemas_por_id.get(id_bloque, [])
        temas_con_subtemas.append((id_bloque, nombre, objetivo, lista_subtemas))

    '''
    Se obtiene la informacion par agenerar el PDF
    '''

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    #  Ruta a los logos (ajusta según la ubicación real)
    logo_unam_izq = os.path.join(settings.BASE_DIR, 'estaticos', 'imagenes', 'escudounam_negro.jpg')
    logo_fi_der = os.path.join(settings.BASE_DIR, 'estaticos', 'imagenes', 'escudofi_negro.jpg')

    # Tamaño deseado para los logos
    logo_width = 60
    logo_height = 60
    top_y = height - 70


    # Insertar los logos
    if os.path.exists(logo_unam_izq):
        p.drawImage(ImageReader(logo_unam_izq), 50, top_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
    else:
        print("Logo izquierdo no encontrado")

    if os.path.exists(logo_fi_der):
        p.drawImage(ImageReader(logo_fi_der), width - 50 - logo_width, top_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
    else:
        print(" Logo derecho no encontrado")

    # Texto centrado entre los logos
    text_unam = f"UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO"
    text_fi = f"FACULTAD DE INGENIERÍA"
    p.setFont("Helvetica-Bold", 10)
    text_width = p.stringWidth(text_unam, "Helvetica-Bold", 10)
    p.drawString((width - text_width) / 2, top_y + (logo_height / 2), text_unam)
    text_width = p.stringWidth(text_fi, "Helvetica-Bold", 10)
    p.drawString((width - text_width) / 2, top_y + (logo_height / 2) - 12, text_fi)

    y_line = top_y + (logo_height / 2) - 40
    dibujar_linea_con_texto(p, y_line, "PROGRAMA DE ESTUDIO", width)

    x_inicio = 30
    y_actual = height - 130
    ancho_total = width - 2 * x_inicio

    y_actual = draw_header_table(
        p,
        x=x_inicio,
        y=y_actual,
        width=ancho_total,
        color=color_pdf,
        clave=clave_pdf,
        nombre=asignatura_pdf
    )

    y_actual = y_actual - 40

    ancho_total = width - 2 * x_inicio

    y_actual = draw_info_table(
        p,
        x=x_inicio,
        y=y_actual,
        width=ancho_total,
        color=color_pdf,
        semestre=semestre_pdf,
        creditos=creditos_pdf,
        fase="",
        licenciatura=licenciatura_pdf
    )

    ancho_total = width - 2 * x_inicio

    y_actual = tala_columnas(
        p, x_inicio, y_actual, ancho_total,
        color = color_pdf,
        area_conocimiento = area_conocimiento_pdf,
        modalidad=modalidad_pdf,
        tipo=tipo_pdf,
        caracter=caracter_pdf,
        valor=valor_practico_pdf,
        horas_t_semanales= horas_teoricas_semanales_pdf, horas_p_semanales=horas_practicas_semanales_pdf,
        horas_t_semestrales=horas_teoricas_semestrales_pdf, horas_p_semestrales=horas_practicas_semestrales_pdf,
        texto_derecha=""
    )

    y_actual = y_actual - 20

    y_actual = dibujar_seriacion_2x2(
        p, x=30, y=y_actual, w_total=width - 60,
        texto_antecedente=seriacion_antecedente_pdf,
        texto_consecuente=seriacion_consecuente_pdf,
        color=color_pdf,
        col_gap=16,
        radio=5,
        header_fs=10,
        header_gap=6,
        box_pad_x=10, box_pad_y=8,
        text_fs=10, text_leading=14
    )

    y_actual = y_actual - 5

    y_actual = dibujar_objetivo_general(
        p, x=30, y=y_actual, w_total=width - 60,
        texto_objetivo=(objetivo_pdf),
        color=color_pdf,
        radio=5, header_gap=8, box_pad_x=10, box_pad_y=10
    )

    # Encabezado de la sección
    y_actual = y_actual - 5
    y_actual = dibujar_titulo_temario(
        p, x=30, y=y_actual, w_total=width - 60,
        # align="left",         # opcional: "center" o "right"
        underline=None  # subrayado a lo ancho; usa "text" o None si no lo quieres
    )

    filas_temas = temario_inf

    y_actual = dibujar_tabla_temas(
        p, x=30, y=y_actual, w_total=width - 60,
        filas=filas_temas,
        draw_outer_border=True,  # contorno exterior del cuerpo
        draw_col_dividers=True,  #  solo líneas verticales internas
        outer_border_color=color_pdf,
        col_divider_color=color_pdf,
        gap_header_body=6
    )

    y_actual = dibujar_tabla_resumen_horas(
        p, x=30, y=y_actual, w_total=width - 60,
        valores=(suma_horas_temario_pdf, actividades_practicas_horas_pdf, (suma_horas_temario_pdf + actividades_practicas_horas_pdf)),
        labels=("Horas en el Semestre", "Actividades prácticas", "TOTAL"),
        fs=9, leading=12, pad_x=8, pad_y=4, row_min_h=18,  #  compacto
        border_color=color_pdf, fill_ultimo=GRIS_SUAVE, radio=0
    )

    y_actual = siguiente_pagina(p, width, height, top_margin=40)

    y_actual = height - 40

    # 3) Dibujar en bucle
    for t in temas_con_subtemas:
        y_actual = dibujar_bloque_temario(
            p, x=30, y=y_actual, w_total=width - 60,
            color = color_pdf,
            tema_titulo=str(t[0])+" "+t[1],
            objetivo_texto=t[2],
            contenidos=t[3],
            auto_paginacion=True,
            page_width=width, page_height=height,
            bottom_margin=40, top_margin=40,
            draw_header_fn=None  # o tu función de encabezado si la tienes
        )
        # espacio entre bloques
        y_actual -= 12

    y_actual = dibujar_bibliografia_temas(
        p, x=30, y=y_actual, w_total=width - 60,
        titulo_izq='Bibliografía básica',
        color=color_pdf,
        outline_color = color_pdf,
        bibliografias=bibliografia_basica_pdf, temas=temas_bibliografia_basica_pdf,
        col_gap=14,
        draw_column_outline=True, outline_radius=6, outline_over_header=False,
        #  auto-paginación
        auto_paginacion=True, page_width=width, page_height=height,
        top_margin=40, bottom_margin=40,
        draw_header_fn=None  # o None si no quieres redibujar nada
    )

    y_actual = y_actual - 10

    y_actual = dibujar_bibliografia_temas(
        p, x=30, y=y_actual, w_total=width - 60,
        titulo_izq='Bibliografía complementaria',
        color=color_pdf,
        outline_color=color_pdf,
        bibliografias=bibliografia_complementaria_pdf, temas=temas_bibliografia_complementaria_pdf,
        col_gap=14,
        draw_column_outline=True, outline_radius=6, outline_over_header=False,
        #  auto-paginación
        auto_paginacion=True, page_width=width, page_height=height,
        top_margin=40, bottom_margin=40,
        draw_header_fn=None  # o None si no quieres redibujar nada
    )

    y_actual = y_actual - 10

    y_actual = dibujar_estrategias_evaluacion(
        p, x=30, y=y_actual, w_total=width - 60,
        items=estrategias_didacticas_inf,
        # compactación (si quieres aún más compacto, baja fs/leading o chk_box_size)
        fs=9, leading=11, cell_pad_y=3, chk_box_size=11,
        # paginación por filas
        auto_paginar_filas=True, page_width=width, page_height=height,
        top_margin=40, bottom_margin=40,
        color=color_pdf,
        chk_border_color=color_pdf,
        # opcional: redibuja tu encabezado general en cada nueva página
        # draw_page_header_fn=mi_encabezado_general
    )

    y_actual = y_actual - 10

    y_actual = dibujar_formas_evaluacion(
        p, x=30, y=y_actual, w_total=width - 60,
        checks_c1=formas_evaluacion_diagnostica_inf, checks_c3=formas_evaluacion_formativa_inf, checks_c5=formas_evaluacion_sumativa_inf,
        auto_paginacion=True, page_width=width, page_height=height,
        bottom_margin=40, top_margin=40,
        chk_border_color=color_pdf,
        # compactación opcional:
        fs=9, leading=12, cell_pad_y=4, chk_box_size=12,
        color=color_pdf,
    )

    y_actual = y_actual - 10


    if formacion_integral_pdf != '':
        y_actual = dibujar_parrafo_with_title(
            p, x=30, y=y_actual, w_total=width - 60,
            texto=formacion_integral_pdf,
            # paginación
            titulo="Formación integral",
            auto_paginacion=True, page_width=width, page_height=height,
            top_margin=40, bottom_margin=40,
            draw_page_header_fn=None,  # pasa None si no quieres header general
            color = color_pdf,
        )

    y_actual = y_actual - 10

    if perfil_profesiografico_pdf != '':
        y_actual = dibujar_parrafo_with_title(
            p, x=30, y=y_actual, w_total=width - 60,
            texto=perfil_profesiografico_pdf,
            # paginación
            titulo="Perfil profesiográfico",
            auto_paginacion=True, page_width=width, page_height=height,
            top_margin=40, bottom_margin=40,
            draw_page_header_fn=None,  # pasa None si no quieres header general
            color=color_pdf,
        )


    dibujar_marca_agua(p, width, height, habilitada = watermark_on)
    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{nombre_archivo_pdf}.pdf"',
        }
    )

def dibujar_linea_con_texto(p, y, texto, ancho_pagina, margen=50):
    p.setFont("Helvetica", 12)
    text_width = p.stringWidth(texto, "Helvetica", 12)

    # Línea izquierda
    x1_left = 0
    x2_left = (ancho_pagina - text_width) / 2 - 10  # 10 pts antes del texto

    p.setStrokeColor(colors.red)
    p.setLineWidth(1)
    p.line(x1_left, y, x2_left, y)

    # Texto
    p.setFillColor(colors.red)
    p.drawString((ancho_pagina - text_width) / 2, y - 5, texto)  # Ajuste vertical

    # Línea derecha
    x1_right = (ancho_pagina + text_width) / 2 + 10
    x2_right = ancho_pagina
    p.line(x1_right, y, x2_right, y)

    # Restaurar color negro para seguir dibujando
    p.setFillColor(colors.black)
    p.setStrokeColor(colors.black)

def dibujarNombreAsignaturaLicenciatura(p, x, y, ancho, alto, data):
    """
    Dibuja una tabla en el canvas 'p' en la posición (x, y),
    con ancho y alto dados, sin bordes, fondo azul marino y texto blanco.

    data: lista de listas con el contenido de la tabla, ej:
          [['Columna 1', 'Columna 2'],
           ['Dato 1', 'Dato 2']]
    """

    # Crear la tabla
    tabla = Table(data, colWidths=[ancho/2.0]*2, rowHeights=[alto]*len(data))

    # Estilo de la tabla
    estilo = TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.ReportLabBlueOLD),  # Fondo azul marino en todas las celdas
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),      # Texto blanco en todas las celdas
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),                # Texto centrado
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),             # Texto vertical centrado
        ('INNERGRID', (0,0), (-1,-1), 0, colors.white),   # Sin líneas internas
        ('BOX', (0,0), (-1,-1), 0, colors.white),         # Sin borde externo
    ])
    tabla.setStyle(estilo)

    # La tabla no se dibuja directamente en el canvas con .draw() sino con .wrapOn y .drawOn
    tabla.wrapOn(p, ancho, alto)
    tabla.drawOn(p, x, y - alto)  # y - alto porque en ReportLab la posición y es la esquina inferior izquierda de la tabla


def dibujarClaveSemestreCreaditos(
    p, x, y, ancho_total, alto, textos,
    margen_entre=10, padding=5,
    radio=6,                         # 👈 radio de las esquinas
    borde_color=colors.HexColor("#D1D5DB"),          # 👈 color del borde (gris)
    bg=colors.white,                 # fondo de la celda
    font="Helvetica", fs=12,         # tipografía y tamaño
    texto_color=colors.grey          # color del texto
):
    """
    Dibuja N celdas con borde redondeado y gris.
    x, y: esquina superior izquierda del bloque.
    """
    num_celdas = len(textos)
    ancho_celda = (ancho_total - (margen_entre * (num_celdas - 1))) / num_celdas

    p.setFont(font, fs)

    for i, texto in enumerate(textos):
        x_celda = x + i * (ancho_celda + margen_entre)
        y_base = y - alto

        # Fondo + borde redondeado (una sola llamada)
        p.setFillColor(bg)
        p.setStrokeColor(borde_color)
        p.setLineWidth(1)
        p.roundRect(x_celda, y_base, ancho_celda, alto, radius=radio, fill=1, stroke=1)

        # Texto alineado a la izquierda con padding, centrado verticalmente
        p.setFillColor(texto_color)
        text_x = x_celda + padding
        text_y = y_base + alto/2 - fs/2 + 2   # centrado vertical fino
        p.drawString(text_x, text_y, str(texto))


def dibujar_dos_celdas(p, x, y, ancho_total, alto, textos, margen_entre=10, padding=8,radio=2, color = colors.ReportLabBlueOLD, ):
    """
    Dibuja dos celdas separadas con fondo azul marino, texto blanco alineado a la izquierda,
    y sin bordes negros. El espacio entre celdas es del color del fondo (blanco).
    """

    num_celdas = 2
    ancho_celda = (ancho_total - margen_entre) / num_celdas

    p.setFont("Helvetica", 12)

    for i, texto in enumerate(textos):
        x_celda = x + i * (ancho_celda + margen_entre)
        y_base = y - alto

        # Dibujar fondo azul marino SIN bordes
        p.setFillColor(color)
        p.roundRect(x_celda, y_base, ancho_celda, alto, radius=radio, fill=1, stroke=0)

        # Escribir texto blanco, alineado a la izquierda con padding
        p.setFillColor(colors.white)
        text_x = x_celda + padding
        text_y = y_base + alto / 2 - 4  # Centrado vertical
        p.drawString(text_x, text_y, texto)

def dibujar_tabla_general_2c(p, x, y, w_total,
                             contenido_col1,  # callable: (p, x, y, w) -> altura_usada
                             contenido_col2=None,  # callable o None
                             ratio_col1=0.5, padding_col2=6,
                             font="Helvetica", fs=10, col_gap=12):
    """
    Dibuja una fila de la tabla general con 2 columnas.
    - contenido_col1: función que dibuja en la 1a columna y devuelve altura usada.
    - contenido_col2: opcional; si se da, también devuelve altura usada. Si None, se usa 0.
    - Ajusta alto de la fila como max(altos).
    - Devuelve nueva y (y - alto_fila).
    """
    w1 = w_total * ratio_col1
    w2 = w_total - w1 - col_gap

    # Dibuja col1 (obligatorio)
    alto1 = contenido_col1(p, x, y, w1)

    # Dibuja col2 (opcional)
    if contenido_col2:
        alto2 = contenido_col2(p, x + w1, y, w2)
    else:
        alto2 = 0

    alto_fila = max(alto1, alto2)

    # (Opcional) bordes del contenedor general: si los quieres, puedes activarlos
    # p.rect(x, y - alto_fila, w_total, alto_fila, fill=0, stroke=1)

    return y - alto_fila


def dibujar_tabla_interna_2c(p, x, y, w_total, titulo, filas,
                             ratio_izq=0.45, alto_min_fila=22,
                             font="Helvetica", font_b="Helvetica-Bold", fs=10,
                             header_bg="#4F617C", header_fg=BLANCO,
                             borde_color=colors.HexColor("#D1D5DB"), borde_grosor=1,
                             gap_y=6,          # 👈 separación vertical entre las cajitas de la col. derecha
                             gap_header=10,    # 👈 separación entre el encabezado y la primera fila
                             radio=2           # 👈 esquinas redondeadas para las cajitas
                             ):
    """
    Tabla interna 2 columnas con encabezado (span 2) y cajitas separadas en la columna derecha.
    - Columna izquierda: sin contorno.
    - Columna derecha: cada fila es una 'cajita' independiente con borde y separación (gap_y).
    - El encabezado queda separado de las filas (gap_header).
    Devuelve la altura total consumida.
    """
    w_izq = w_total * ratio_izq
    w_der = w_total - w_izq

    # -------- Encabezado (span 2 columnas) ----------
    y = y - 5
    p.setFillColor(NEGRO)
    p.setFont("Helvetica-Bold", 11)  # Font name and size
    p.drawString(x, y , "Área del conocimiento")
    y = y - 5
    estilo_hdr = ParagraphStyle(
        "hdr", fontName=font_b, fontSize=fs+1, leading=fs+3,
        textColor=header_fg, alignment=TA_CENTER)
    para_hdr = Paragraph(titulo, estilo_hdr)
    h_hdr = max(alto_min_fila, _text_height(para_hdr, w_total - 12) + 10)

    # Fondo encabezado
    p.setFillColor(header_bg)
    p.setStrokeColor(header_bg)
    p.roundRect(x, y - h_hdr, w_total, h_hdr, radius=radio, fill=1, stroke=1)
    # Texto encabezado (centrado)
    w_hdr, _ = para_hdr.wrap(w_total - 12, 10000)
    para_hdr.drawOn(p, x + (w_total - w_hdr)/2, y - h_hdr + (h_hdr - (fs+3))/2 - 1)

    y_cursor = y - h_hdr - gap_header   # separación debajo del header
    altura_total = h_hdr + gap_header

    # -------- Filas etiqueta-valor ----------
    estilo_etiq = ParagraphStyle(
        "etiq", fontName=font_b, fontSize=fs, leading=fs+2,
        textColor=colors.black, alignment=TA_RIGHT)
    estilo_val = ParagraphStyle(
        "val", fontName=font, fontSize=fs, leading=fs+2,
        textColor=colors.black, alignment=TA_LEFT)

    for idx, (etiq, val) in enumerate(filas):
        para_e = Paragraph(str(etiq), estilo_etiq)
        para_v = Paragraph(str(val), estilo_val)

        # Alturas calculadas con padding interno
        pad_x = 6
        pad_y = 5
        h_e = _text_height(para_e, w_izq - 2*pad_x)
        h_v = _text_height(para_v, w_der - 2*pad_x)
        h_fila = max(alto_min_fila, max(h_e, h_v) + 2*pad_y)

        # ----- Columna izquierda (sin contorno)
        p.setFillColor(BLANCO)
        p.rect(x, y_cursor - h_fila, w_izq, h_fila, fill=1, stroke=0)
        para_e.drawOn(p, x + pad_x, y_cursor - h_fila + pad_y)

        # ----- Columna derecha (cajita con borde y separación vertical)
        # para "separarla", reducimos la caja vertical con gap_y/2 arriba y abajo
        y_top_caja = y_cursor - (gap_y/2)
        caja_altura = h_fila - gap_y

        # fondo blanco
        p.setFillColor(BLANCO)
        p.rect(x + w_izq, y_top_caja - caja_altura, w_der, caja_altura, fill=1, stroke=0)

        # borde con esquinas redondeadas (simulado: 4 rects + líneas) o simple rect
        p.setStrokeColor(borde_color)
        p.setLineWidth(borde_grosor)

        # Si quieres un borde simple:
        # p.rect(x + w_izq, y_top_caja - caja_altura, w_der, caja_altura, fill=0, stroke=1)

        # Bordes con esquinas suavemente redondeadas (simple):
        try:
            # algunos backends tienen roundRect
            p.roundRect(x + w_izq, y_top_caja - caja_altura, w_der, caja_altura, radius=radio, stroke=1, fill=0)
        except Exception:
            # fallback a rect normal
            p.rect(x + w_izq, y_top_caja - caja_altura, w_der, caja_altura, fill=0, stroke=1)

        # valor dentro de la cajita
        para_v.drawOn(p, x + w_izq + pad_x, y_top_caja - caja_altura + pad_y)

        # avanzar
        y_cursor -= h_fila
        altura_total += h_fila

    return altura_total

def _text_height(p: Paragraph, avail_w: float) -> float:
    w, h = p.wrap(avail_w, 10000)
    return h

def tala_columnas(p, x_inicio, y_inicio, ancho_total,
                  color,
                  area_conocimiento,
                  modalidad, tipo, caracter, valor,
                  horas_t_semanales, horas_p_semanales,
                  horas_t_semestrales, horas_p_semestrales,
                  texto_derecha=""):
    """
    Dibuja una fila de la tabla general:
    - Columna 1: tabla interna con encabezado y 4 filas.
    - Columna 2: párrafo (opcional).
    Devuelve la nueva coordenada y.
    """
    # Construimos el "contenido_col1" como un closure que llama a la tabla interna:
    def col1_drawer(p, x, y, w):
        filas = [
            ("Modalidad", modalidad),
            ("Tipo", tipo),
            ("Caracter", caracter),
            ("Valor práctico", valor),
        ]
        return dibujar_tabla_interna_2c(
            p, x, y, w_total=w,
            titulo= area_conocimiento,
            header_bg = color,
            borde_color=color,
            filas=filas,
            ratio_izq=0.45,
            alto_min_fila=22
        )

    # Contenido de la columna 2 (opcional)
    col2_drawer = None
    if texto_derecha:
        col2_drawer = contenido_parrafo(texto_derecha)

    # Dibuja la "tabla general" (una fila con 2 columnas)
    y_nueva = dibujar_tabla_general_2c(
        p, x_inicio, y_inicio, ancho_total,
        contenido_col1=col1_drawer,
        contenido_col2=contenido_col2_horas_semana(
            valores1=(horas_t_semanales, horas_p_semanales, horas_t_semanales+horas_p_semanales),
            valores2=(horas_t_semestrales, horas_p_semestrales, horas_t_semestrales+horas_p_semestrales),
            color = color
        ),
        ratio_col1=0.52
    )
    return y_nueva

def contenido_parrafo(col_texto, font="Helvetica", fs=10, leading=14, color=colors.black, padding=6):
    """
    Devuelve un callable para usar en contenido_col2 que dibuja un párrafo con wrap.
    """
    def _drawer(p, x, y, w):
        estilo = ParagraphStyle("c2", fontName=font, fontSize=fs, leading=leading,
                                textColor=color, alignment=TA_LEFT)
        para = Paragraph(col_texto, estilo)
        w_, h_ = para.wrap(w - 2*padding, 10000)
        para.drawOn(p, x + padding, y - h_ - padding)
        return h_ + 2*padding
    return _drawer

def dibujar_panel_horas_semana(
    p: canvas.Canvas,
    x: float, y: float, w: float,
    valores=(0.0, 0.0, 0.0),                # (teóricas, práct, totales)
    titulo="Horas/Semana",
    color = colors.HexColor("#D1D5DB"),
    radio=6,
    panel_pad=50,                            # padding interno del panel
    hdr_row_h=20,                            # alto encabezados ("teóricas", "práct", "totales")
    val_row_h=20,                            # alto fila de valores
    gap_filas=6,                             # espacio entre header-row y value-row
    gap_legend=2,                            # offset sutil vertical de la leyenda respecto al borde
    font="Helvetica",
    font_b="Helvetica-Bold",
    fs=10,
    # 👇 Nuevo: alineación de la leyenda
    legend_align="right",                    # "left" | "center" | "right"
    legend_margin=12,                        # margen lateral respecto al borde del panel
):
    """
    Cajita redondeada con 'leyenda' sobre el borde superior ("Horas/Semana").
    Dentro, tabla 3x2 con encabezados fijos y fila de valores en cajitas.
    Devuelve la altura total consumida por el panel.
    """
    # --- alto del contenido y del panel ---
    contenido_h = hdr_row_h + gap_filas + val_row_h
    h_panel = contenido_h + 2*panel_pad

    # --- dibujar panel (fondo + borde redondeado) ---
    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x, y - h_panel, w, h_panel, radius=radio, fill=1, stroke=1)

    # --- leyenda sobre el borde ---
    p.setFont(font_b, fs)
    titulo_w = p.stringWidth(titulo, font_b, fs)
    legend_pad_x = 8
    legend_pad_y = 2
    legend_w = titulo_w + 2*legend_pad_x
    legend_h = fs + 2*legend_pad_y

    # Calcular X según alineación solicitada
    if legend_align == "center":
        legend_x = x + (w - legend_w) / 2
    elif legend_align == "right":
        legend_x = x + w - legend_margin - legend_w
    else:  # "left"
        legend_x = x + legend_margin

    # Evitar colisión con esquinas redondeadas
    legend_x = max(x + radio, min(legend_x, x + w - radio - legend_w))

    # El borde superior del panel está en y; centramos verticalmente la leyenda sobre ese borde
    rect_y = y - (legend_h / 2) - gap_legend

    # Rect blanco para "cortar" el borde y apoyar la leyenda
    p.setFillColor(BLANCO)
    p.rect(legend_x, rect_y, legend_w, legend_h, fill=1, stroke=0)

    # Texto de la leyenda
    p.setFillColor(NEGRO)
    p.drawString(legend_x + legend_pad_x, rect_y + legend_pad_y, titulo)

    # --- contenido interno (tabla 3x2) ---
    cx = x + panel_pad
    cy = y - panel_pad  # top interno

    headers = ["Teóricas", "Prácticas", "Totales"]
    num_cols = 3
    col_w = (w - 2*panel_pad) / num_cols

    # Fila de encabezados
    p.setFont(font_b, fs)
    for i, htxt in enumerate(headers):
        cell_x = cx + i * col_w
        cell_y = cy - hdr_row_h
        p.setFillColor(GRIS_SUAVE) #EDITAR PANTONE
        p.rect(cell_x, cell_y, col_w, hdr_row_h, fill=1, stroke=0)
        p.setFillColor(NEGRO)
        tw = p.stringWidth(htxt, font_b, fs)
        tx = cell_x + (col_w - tw) / 2
        ty = cell_y + hdr_row_h / 2 - fs / 2 + 2
        p.drawString(tx, ty, htxt)

    # Fila de valores (cajitas)
    p.setFont(font_b, fs)
    val_y = cy - hdr_row_h - gap_filas
    for i, v in enumerate(valores):
        cell_x = cx + i * col_w
        cell_y = val_y - val_row_h

        box_pad_x = 10
        box_w = col_w - 2 * box_pad_x
        box_h = val_row_h - 6
        box_x = cell_x + box_pad_x
        box_y = cell_y + (val_row_h - box_h) / 2

        p.setFillColor(BLANCO)
        p.setStrokeColor(color)
        p.roundRect(box_x, box_y, box_w, box_h, radius=radio, fill=1, stroke=1)

        txt = f"{float(v):.1f}"
        tw = p.stringWidth(txt, font_b, fs)
        tx = box_x + (box_w - tw) / 2
        ty = box_y + box_h / 2 - fs / 2 + 2
        p.setFillColor(NEGRO)
        p.drawString(tx, ty, txt)

    return h_panel


def dibujar_col2_horas_semana_doble(
    p, x, y, w,
    valores_panel1=(0.0, 0.0, 0.0),
    valores_panel2=(0.0, 0.0, 0.0),
    gap_panels=10,
    align="right",
    inset_x=0,
    panel_w_ratio=0.7,
    panel_w_px=None,
    # 👇 nuevo: overrides por panel
    panel1_cfg=None,   # dict con overrides (ej. {"val_row_h": 16})
    panel2_cfg=None,   # dict con overrides (ej. {"val_row_h": 24})
    color = colors.HexColor("#D1D5DB"),
    **kwargs           # base kwargs comunes a ambos paneles
):
    y= y -5
    p.setFillColor(NEGRO)
    p.setFont("Helvetica-Bold", 11)  # Font name and size
    p.drawString(x, y, "")
    y = y - 5

    panel1_cfg = panel1_cfg or {}
    panel2_cfg = panel2_cfg or {}

    # ancho disponible
    w_avail = max(w - 2*inset_x, 10)
    if panel_w_px is not None:
        w_in = min(panel_w_px, w_avail)
    else:
        ratio = max(0.05, min(panel_w_ratio, 1.0))
        w_in = w_avail * ratio

    # x según alineación
    if align == "center":
        x_in = x + (w - w_in) / 2
    elif align == "right":
        x_in = x + w - w_in - inset_x
    else:
        x_in = x + inset_x

    # Panel 1
    cfg1 = {**kwargs, **panel1_cfg}
    h1 = dibujar_panel_horas_semana(
        p, x_in, y, w_in, valores=valores_panel1,titulo='Horas/Semana', color=color, **cfg1
    )

    # Panel 2
    y2 = y - h1 - gap_panels
    cfg2 = {**kwargs, **panel2_cfg}
    h2 = dibujar_panel_horas_semana(
        p, x_in, y2, w_in, valores=valores_panel2,titulo='Horas/Semestre', color=color, **cfg2
    )

    return h1 + gap_panels + h2

def contenido_col2_horas_semana(valores1=(0.0, 0.0, 0.0), valores2=(0.0, 0.0, 0.0), color  = colors.HexColor("#D1D5DB")):
    def _drawer(p, x, y, w):
        # Devuelve altura usada en esa columna
        return dibujar_col2_horas_semana_doble(
        p, x, y, w,
        valores_panel1=valores1,
        valores_panel2=valores2,
        color=color,
        align="right",
        panel_w_px=180,
        gap_panels=10,
        # estilo base para ambos
        radio=5, panel_pad=8, hdr_row_h=16, gap_filas=4, gap_legend=2,
        legend_align="right", font="Helvetica", font_b="Helvetica-Bold", fs=9,
        # 👇 alturas distintas por panel
        panel1_cfg={"val_row_h": 18},   # más bajito
        panel2_cfg={"val_row_h": 18},   # más alto
    )
    return _drawer

def _text_height(p: Paragraph, avail_w: float) -> float:
    w, h = p.wrap(avail_w, 10000)
    return h


def dibujar_seriacion_2x2(
    p, x, y, w_total,
    texto_antecedente="",
    texto_consecuente="",
    hdr_izq="Seriación obligatoria antecedente",
    hdr_der="Seriación obligatoria consecuente",
    color = colors.HexColor("#D1D5DB"),
    col_gap=14,
    radio=6,
    header_fs=10,
    header_font="Helvetica-Bold",
    header_color=NEGRO,
    header_gap=6,
    box_pad_x=10,
    box_pad_y=8,
    text_fs=10,
    text_leading=14,
    text_font="Helvetica",
):
    """
    Dos columnas: cada una con encabezado (izquierda) y cajita redondeada.
    Ambas cajitas usan la MISMA altura = altura requerida por el texto más alto.
    Devuelve nueva y.
    """
    col_w = (w_total - col_gap) / 2.0

    # Estilos
    hdr_style = ParagraphStyle(
        "hdr", fontName=header_font, fontSize=header_fs, leading=header_fs+2,
        textColor=header_color, alignment=TA_LEFT
    )
    box_style = ParagraphStyle(
        "box", fontName=text_font, fontSize=text_fs, leading=text_leading,
        textColor=NEGRO, alignment=TA_LEFT
    )

    # --- Medición encabezados ---
    hdr1 = Paragraph(hdr_izq, hdr_style);   w_, h_hdr1 = hdr1.wrap(col_w, 10**6)
    hdr2 = Paragraph(hdr_der, hdr_style);   w_, h_hdr2 = hdr2.wrap(col_w, 10**6)

    # --- Medición textos dentro de cajitas ---
    para1 = Paragraph(texto_antecedente or "", box_style)
    para2 = Paragraph(texto_consecuente  or "", box_style)
    avail_w = col_w - 2*box_pad_x
    w1, h_txt1 = para1.wrap(avail_w, 10**6)
    w2, h_txt2 = para2.wrap(avail_w, 10**6)

    # --- MISMA altura para ambas cajitas (en función del texto mayor) ---
    shared_box_h = max(h_txt1, h_txt2) + 2*box_pad_y
    # Altura total de la sección = header más alto + gap + caja compartida
    alto_total = max(h_hdr1, h_hdr2) + header_gap + shared_box_h

    # Coordenadas base
    x1 = x
    x2 = x + col_w + col_gap
    y_top = y

    # ---- Dibujo columna izquierda ----
    # Encabezado
    hdr1.drawOn(p, x1, y_top - h_hdr1)
    # Caja (altura compartida)
    y_box1_top = y_top - h_hdr1 - header_gap
    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x1, y_box1_top - shared_box_h, col_w, shared_box_h, radius=radio, fill=1, stroke=1)
    # Texto (alineado al tope interno)
    para1.drawOn(p, x1 + box_pad_x, y_box1_top - box_pad_y - h_txt1)

    # ---- Dibujo columna derecha ----
    hdr2.drawOn(p, x2, y_top - h_hdr2)
    y_box2_top = y_top - h_hdr2 - header_gap
    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x2, y_box2_top - shared_box_h, col_w, shared_box_h, radius=radio, fill=1, stroke=1)
    para2.drawOn(p, x2 + box_pad_x, y_box2_top - box_pad_y - h_txt2)

    # Nueva y al final de la sección
    return y - alto_total

def dibujar_objetivo_general(
    p, x, y, w_total,
    texto_objetivo="",
    titulo="Objetivo general de la asignatura:",
    color = colors.HexColor("#D1D5DB"),
    # layout
    radio=6,                # esquinas de la cajita
    header_fs=10,           # tamaño de fuente del encabezado
    header_font="Helvetica-Bold",
    header_color=NEGRO,
    header_gap=6,           # espacio entre encabezado y cajita
    box_pad_x=10,           # padding interno horizontal
    box_pad_y=8,            # padding interno vertical
    text_fs=10,             # tamaño de fuente del texto en la cajita
    text_leading=14,        # interlineado del texto en la cajita
    text_font="Helvetica",
    justificar_ultima_linea=True,  # intenta justificar también la última línea (si está soportado)
):
    """
    Sección de 2 filas (1 columna):
      1) Encabezado fijo (alineado a la izquierda)
      2) Cajita redondeada con texto multilínea JUSTIFICADO que crece según contenido
    Devuelve la nueva coordenada y (y - alto_consumido).
    """
    # Estilos
    hdr_style = ParagraphStyle(
        "hdr",
        fontName=header_font, fontSize=header_fs, leading=header_fs+2,
        textColor=header_color, alignment=TA_LEFT
    )
    box_style = ParagraphStyle(
        "box",
        fontName=text_font, fontSize=text_fs, leading=text_leading,
        textColor=NEGRO, alignment=TA_JUSTIFY
    )
    # Algunas versiones soportan estas banderas:
    if justificar_ultima_linea:
        # Evita crashear si la versión no las tiene
        try:
            box_style.justifyLastLine = 1         # intenta justificar la última línea
            box_style.justifyBreaks   = 1         # extiende justificado en saltos
        except Exception:
            pass

    # Medir encabezado
    hdr = Paragraph(titulo, hdr_style)
    _, h_hdr = hdr.wrap(w_total, 10**6)

    # Medir texto de la cajita (justificado)
    para = Paragraph(texto_objetivo or "", box_style)
    avail_w = max(0, w_total - 2 * box_pad_x)
    _, h_txt = para.wrap(avail_w, 10**6)
    box_h = max(h_txt + 2 * box_pad_y, text_fs + 2 * box_pad_y)

    # Altura total
    alto_total = h_hdr + header_gap + box_h

    # Dibujo
    y_top = y

    # Encabezado
    hdr.drawOn(p, x, y_top - h_hdr)

    # Cajita
    y_box_top = y_top - h_hdr - header_gap
    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x, y_box_top - box_h, w_total, box_h, radius=radio, fill=1, stroke=1)

    # Texto JUSTIFICADO dentro de la cajita
    para.drawOn(p, x + box_pad_x, y_box_top - box_pad_y - h_txt)

    # Nueva coordenada y
    return y - alto_total


def dibujar_tabla_temas(
    p, x, y, w_total, filas,
    header=("", "Tema", "Horas"),
    col_ratios=(0.05, 0.80, 0.15),
    font="Helvetica", font_b="Helvetica-Bold",
    fs=10, leading=14,
    col_align=("left", "left", "center"),
    pad_x=8, pad_y=6,
    # Contorno exterior del cuerpo
    draw_outer_border=True,
    outer_border_color=colors.HexColor("#D1D5DB"),
    outer_border_width=1,
    body_bg=BLANCO,
    # Divisiones verticales internas
    draw_col_dividers=True,
    col_divider_color=colors.HexColor("#D1D5DB"),
    col_divider_width=1,
    # Separación entre encabezado y cuerpo
    gap_header_body=4,
):
    """
    Tabla 3 columnas x N filas:
      • Encabezado SIN borde (solo texto).
      • Cuerpo con contorno exterior y SOLO líneas verticales internas.
      • Sin líneas horizontales. Filas autoajustan altura.
    Devuelve la nueva coordenada y.
    """
    # Anchos por proporción
    w1 = w_total * col_ratios[0]
    w2 = w_total * col_ratios[1]
    w3 = w_total * col_ratios[2]
    col_ws = (w1, w2, w3)
    x_cols = (x, x + w1, x + w1 + w2)  # inicio de cada columna

    # Estilos
    hdr_style = ParagraphStyle("hdr", fontName=font_b, fontSize=fs, leading=fs+2,
                               textColor=NEGRO, alignment=TA_LEFT)
    ta_map = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}
    body_styles = [
        ParagraphStyle("c1", fontName=font, fontSize=fs, leading=leading,
                       textColor=NEGRO, alignment=ta_map.get(col_align[0], TA_LEFT)),
        ParagraphStyle("c2", fontName=font, fontSize=fs, leading=leading,
                       textColor=NEGRO, alignment=ta_map.get(col_align[1], TA_LEFT)),
        ParagraphStyle("c3", fontName=font, fontSize=fs, leading=leading,
                       textColor=NEGRO, alignment=ta_map.get(col_align[2], TA_LEFT)),
    ]

    # ---------- Encabezado (solo texto, sin borde) ----------
    header_paras = [Paragraph(str(h or ""), hdr_style) for h in header]
    h_hdrs = []
    for i, para in enumerate(header_paras):
        avail_w = max(0, col_ws[i] - 2*pad_x)
        _, h = para.wrap(avail_w, 10**6)
        h_hdrs.append(h)
    h_hdr_row = max(h_hdrs) + 2*pad_y

    for i, para in enumerate(header_paras):
        para.drawOn(p, x_cols[i] + pad_x, y - pad_y - h_hdrs[i])

    # Top del cuerpo
    y_body_top = y - h_hdr_row - gap_header_body

    # ---------- Precalcular alturas de filas ----------
    rows = []
    body_total_h = 0
    for fila in filas:
        textos = [str(fila[0] or ""), str(fila[1] or ""), str(f"{fila[2]:.1f}" or "")]
        paras  = [Paragraph(textos[i], body_styles[i]) for i in range(3)]
        h_cells = []
        for i, para in enumerate(paras):
            avail_w = max(0, col_ws[i] - 2*pad_x)
            _, h = para.wrap(avail_w, 10**6)
            h_cells.append(h)
        row_h = max(h_cells) + 2*pad_y
        rows.append((paras, h_cells, row_h))
        body_total_h += row_h

    # ---------- Cuerpo: fondo + contorno exterior ----------
    if body_total_h > 0:
        # Fondo
        p.setFillColor(body_bg)
        p.rect(x, y_body_top - body_total_h, w_total, body_total_h, fill=1, stroke=0)

        # Contorno exterior
        if draw_outer_border:
            p.setStrokeColor(outer_border_color)
            p.setLineWidth(outer_border_width)
            p.rect(x, y_body_top - body_total_h, w_total, body_total_h, fill=0, stroke=1)

        # Líneas verticales internas (solo entre columnas)
        if draw_col_dividers:
            p.setStrokeColor(col_divider_color)
            p.setLineWidth(col_divider_width)
            # línea entre col 1 y 2
            p.line(x_cols[1], y_body_top, x_cols[1], y_body_top - body_total_h)
            # línea entre col 2 y 3
            p.line(x_cols[2], y_body_top, x_cols[2], y_body_top - body_total_h)

    # ---------- Dibujar textos (sin líneas de celda) ----------
    y_cursor = y_body_top
    for paras, h_cells, row_h in rows:
        for i in range(3):
            paras[i].drawOn(p, x_cols[i] + pad_x, y_cursor - pad_y - h_cells[i])
        y_cursor -= row_h

    return y_cursor

def dibujar_tabla_resumen_horas(
    p, x, y, w_total,
    valores=(0.0, 0.0, 0.0),
    labels=("Horas en el Semestre", "Actividades prácticas", "TOTAL"),
    col_ratios=(0.05, 0.80, 0.15),
    # tipografías y compactación
    font="Helvetica", font_b="Helvetica-Bold",
    fs=9, leading=12,           # 👈 más pequeño que antes
    pad_x=8, pad_y=4,           # 👈 menos padding = filas más bajas
    row_min_h=18,               # 👈 altura mínima por fila
    # cajitas col. 3
    border_color=colors.HexColor("#D1D5DB"), border_width=1,
    fill_ultimo=GRIS_SUAVE,
    radio=0,
):
    """
    Tabla 3 columnas sin encabezado:
      - Col1: vacía
      - Col2: labels (alineados a la DERECHA)
      - Col3: valores en cajitas (última sombreada)
    Devuelve la nueva y.
    """
    # anchos por proporción
    w1 = w_total * col_ratios[0]
    w2 = w_total * col_ratios[1]
    w3 = w_total * col_ratios[2]
    x1, x2, x3 = x, x + w1, x + w1 + w2

    style_label = ParagraphStyle(
        "lbl", fontName=font, fontSize=fs, leading=leading,
        textColor=NEGRO, alignment=TA_RIGHT   # 👈 derecha
    )
    style_val = ParagraphStyle(
        "val", fontName=font_b, fontSize=fs, leading=leading,
        textColor=NEGRO, alignment=TA_CENTER
    )

    y_cursor = y

    for idx in range(len(labels)):
        label_txt = str(labels[idx] or "")
        val_txt = f"{float(valores[idx]):.1f}" if idx < len(valores) and str(valores[idx]).strip() != '' else "0.0"

        para_label = Paragraph(label_txt, style_label)
        para_val   = Paragraph(val_txt,   style_val)

        # medir alturas
        _, h_lbl = para_label.wrap(max(0, w2 - 2*pad_x), 10**6)
        _, h_val = para_val.wrap(max(0, w3 - 2*pad_x),  10**6)

        row_h = max(row_min_h, max(h_lbl, h_val) + 2*pad_y)

        # col.2: texto (sin borde), centrado verticalmente dentro de la fila
        para_label.drawOn(
            p,
            x2 + pad_x,
            y_cursor - pad_y - h_lbl + (row_h - (h_lbl + 2*pad_y)) / 2
        )

        # col.3: cajita (contorno; última sombreada)
        p.setLineWidth(border_width)
        p.setStrokeColor(border_color)
        p.setFillColor(fill_ultimo if idx == len(labels) - 1 else BLANCO)
        if radio and radio > 0:
            p.roundRect(x3, y_cursor - row_h, w3, row_h, radius=radio, fill=1, stroke=1)
        else:
            p.rect(x3, y_cursor - row_h, w3, row_h, fill=1, stroke=1)

        # valor centrado verticalmente dentro de la cajita
        para_val.drawOn(
            p,
            x3 + pad_x,
            y_cursor - pad_y - h_val + (row_h - (h_val + 2*pad_y)) / 2
        )

        y_cursor -= row_h

    return y_cursor

def dibujar_titulo_temario(
    p, x, y, w_total,
    titulo="Temario con distribución de horas en el semestre",
    align="left",                 # "left" | "center" | "right"
    font="Helvetica-Bold", fs=11,
    color=NEGRO,
    underline="full",             # None | "text" | "full"
    underline_color=colors.HexColor("#D1D5DB"),
    gap_text_line=3,              # espacio entre texto y línea
    gap_bajo=6                    # espacio extra después del título
):
    """
    Escribe un título sencillo y opcionalmente subraya con una línea sutil.
    Devuelve la nueva coordenada y.
    """
    p.setFont(font, fs)
    p.setFillColor(color)

    tw = p.stringWidth(titulo, font, fs)
    if align == "center":
        tx = x + (w_total - tw) / 2
    elif align == "right":
        tx = x + (w_total - tw)
    else:
        tx = x

    # dibuja el texto
    p.drawString(tx, y - fs, titulo)

    # línea opcional
    if underline in ("text", "full"):
        p.setStrokeColor(underline_color)
        p.setLineWidth(1)
        ly = y - fs - gap_text_line
        if underline == "text":
            p.line(tx, ly, tx + tw, ly)
        else:  # "full"
            p.line(x, ly, x + w_total, ly)
        return ly - gap_bajo
    else:
        return y - fs - gap_bajo

def siguiente_pagina(p, width, height, draw_header_fn=None, top_margin=40):
    """
    Crea una nueva página y devuelve la coordenada y inicial para seguir dibujando.
    Si pasas draw_header_fn (una función que dibuje tu encabezado), esa función
    debe devolver el nuevo y desde donde continuar.
    """
    dibujar_marca_agua(p, width, height, habilitada = watermark_on)
    p.showPage()
    y = height - top_margin
    if callable(draw_header_fn):
        y = draw_header_fn(p, width, height)  # esta función debe devolver y
    return y

def dibujar_bloque_temario(
    p, x, y, w_total,
    tema_titulo: str,
    objetivo_texto: str,
    contenidos: list,  # lista de tuplas (id_num, texto_subtema) o lista de dicts con esas claves
    *,
    # Paginación automática
    auto_paginacion=True,
    page_width=None, page_height=None,
    bottom_margin=40, top_margin=40,
    draw_header_fn=None,  # función opcional que redibuja tu encabezado y devuelve nuevo y
    # Estilo/espaciado
    titulo_fs=11, titulo_leading=14, titulo_pad_x=10, titulo_pad_y=8, titulo_radio=6,
    objetivo_fs=10, objetivo_leading=14, gap_after_titulo=10, gap_after_obj=8,
    hdr_contenido_fs=10, gap_after_hdr=6,
    box_radio=6, box_pad=10, cell_pad_x=6, cell_pad_y=4,
    id_align="center",  # "left" | "center" | "right" para la col. ID
    color =  colors.ReportLabBlueOLD,
):
    """
    Dibuja un bloque de temario:
      1) Título en cajita azul redondeada.
      2) Objetivo ("Objetivo:" + texto).
      3) Tabla de contenido (2 columnas 10%/90%) dentro de cajita redondeada, filas autoajustables.
    Devuelve la nueva coordenada y.
    """

    # ----- Estilos -----
    style_titulo = ParagraphStyle(
        "titulo_tema", fontName="Helvetica-Bold", fontSize=titulo_fs,
        leading=titulo_leading, textColor=BLANCO, alignment=TA_LEFT
    )
    style_obj = ParagraphStyle(
        "objetivo", fontName="Helvetica", fontSize=objetivo_fs,
        leading=objetivo_leading, textColor=NEGRO, alignment=TA_JUSTIFY
    )
    style_hdr = ParagraphStyle(
        "hdr_contenido", fontName="Helvetica-Bold", fontSize=hdr_contenido_fs,
        leading=hdr_contenido_fs+2, textColor=NEGRO, alignment=TA_LEFT
    )
    ta_map = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}
    style_id  = ParagraphStyle(
        "contenido_id", fontName="Helvetica-Bold", fontSize=objetivo_fs,
        leading=objetivo_leading, textColor=NEGRO, alignment=ta_map.get(id_align, TA_CENTER)
    )
    style_txt = ParagraphStyle(
        "contenido_txt", fontName="Helvetica", fontSize=objetivo_fs,
        leading=objetivo_leading, textColor=NEGRO, alignment=TA_JUSTIFY
    )

    # ----- MEDICIÓN previa (para auto-paginación y layout) -----
    # 1) Título
    para_titulo = Paragraph(tema_titulo or "", style_titulo)
    avail_w = max(0, w_total - 2*titulo_pad_x)
    _, h_titulo_txt = para_titulo.wrap(avail_w, 10**6)
    h_titulo_box = max(h_titulo_txt + 2*titulo_pad_y, titulo_fs + 2*titulo_pad_y)

    # 2) Objetivo (texto con etiqueta en negritas)
    para_obj = Paragraph(f"<b>Objetivo:</b> {objetivo_texto or ''}", style_obj)
    _, h_obj = para_obj.wrap(w_total, 10**6)

    # 3) Encabezado "Contenido:"
    para_hdr = Paragraph("Contenido:", style_hdr)
    _, h_hdr = para_hdr.wrap(w_total, 10**6)

    # 4) Contenido (cajita con 2 columnas 10%/90%)
    inner_w = w_total
    body_pad = box_pad
    col1_w = (inner_w - 2*body_pad) * 0.10
    col2_w = (inner_w - 2*body_pad) * 0.90

    rows_info = []
    total_rows_h = 0
    if contenidos:
        for item in contenidos:
            # soporta tuple (id, texto) o dict {"id":..,"texto":..}
            if isinstance(item, dict):
                _id = item.get("id", "")
                _tx = item.get("texto", "")
            else:
                _id, _tx = item[0], item[1]

            para_id  = Paragraph(str(_id), style_id)
            para_txt = Paragraph(str(_tx or ""), style_txt)

            _, h_id  = para_id.wrap(max(0, col1_w - 2*cell_pad_x), 10**6)
            _, h_txt = para_txt.wrap(max(0, col2_w - 2*cell_pad_x), 10**6)

            row_h = max(h_id, h_txt) + 2*cell_pad_y
            rows_info.append((para_id, h_id, para_txt, h_txt, row_h))
            total_rows_h += row_h
    else:
        # al menos una fila mínima vacía
        para_id  = Paragraph("", style_id)
        para_txt = Paragraph("", style_txt)
        _, h_id  = para_id.wrap(max(0, col1_w - 2*cell_pad_x), 10**6)
        _, h_txt = para_txt.wrap(max(0, col2_w - 2*cell_pad_x), 10**6)
        row_h = max(h_id, h_txt) + 2*cell_pad_y
        rows_info.append((para_id, h_id, para_txt, h_txt, row_h))
        total_rows_h += row_h

    h_box_body = total_rows_h + 2*body_pad

    # Altura total del bloque
    alto_total = (
        h_titulo_box + gap_after_titulo +
        h_obj        + gap_after_obj     +
        h_hdr        + gap_after_hdr     +
        h_box_body
    )

    # ----- Paginación automática -----
    if auto_paginacion and page_width and page_height:
        if y - alto_total < bottom_margin:
            # salto de página
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            # re-dibujar encabezado si aplica
            if callable(draw_header_fn):
                y = draw_header_fn(p, page_width, page_height)
            else:
                y = page_height - top_margin

    # ----- DIBUJO -----
    y_cursor = y

    # 1) Título (cajita azul)
    p.setFillColor(color)
    p.setStrokeColor(color)
    p.roundRect(x, y_cursor - h_titulo_box, w_total, h_titulo_box, radius=titulo_radio, fill=1, stroke=0)
    para_titulo.drawOn(p, x + titulo_pad_x, y_cursor - titulo_pad_y - h_titulo_txt)
    y_cursor -= (h_titulo_box + gap_after_titulo)

    # 2) Objetivo (texto sin borde)
    para_obj.drawOn(p, x, y_cursor - h_obj)
    y_cursor -= (h_obj + gap_after_obj)

    # 3) Encabezado "Contenido:" (sin borde)
    para_hdr.drawOn(p, x, y_cursor - h_hdr)
    y_cursor -= (h_hdr + gap_after_hdr)

    # 4) Cajita cuerpo (redondeada) con filas autoajustables
    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x, y_cursor - h_box_body, w_total, h_box_body, radius=box_radio, fill=1, stroke=1)

    # área interna de la cajita
    x_in = x + body_pad
    y_rows = y_cursor - body_pad

    # Columnas internas (sin líneas internas)
    x_c1 = x_in
    x_c2 = x_in + col1_w

    for para_id, h_id, para_txt, h_txt, row_h in rows_info:
        # ID
        para_id.drawOn(
            p,
            x_c1 + cell_pad_x,
            y_rows - cell_pad_y - h_id
        )
        # Texto subtema
        para_txt.drawOn(
            p,
            x_c2 + cell_pad_x,
            y_rows - cell_pad_y - h_txt
        )
        y_rows -= row_h

    y_cursor -= h_box_body
    return y_cursor

def _fmt_biblio_item(item):
    """
    Acepta:
      - str listo (se usa tal cual)
      - dict con campos típicos: autores, año, titulo, editorial, edicion, isbn, doi, url
    Devuelve un string con markup de ReportLab (Paragraph).
    """
    if isinstance(item, str):
        return item

    # Campos
    autores   = item.get("autores", "")
    anio      = item.get("anio", "") or item.get("año", "")
    titulo    = item.get("titulo", "")
    editorial = item.get("editorial", "")
    edicion   = item.get("edicion", "")
    isbn      = item.get("isbn", "")
    doi       = item.get("doi", "")
    url       = item.get("url", "")

    partes = []
    if autores:   partes.append(f"{autores}")
    if anio:      partes.append(f"({anio})")
    if titulo:    partes.append(f"<i>{titulo}</i>")
    extra = []
    if edicion:   extra.append(f"{edicion}")
    if editorial: extra.append(f"{editorial}")
    if extra:     partes.append(", ".join(extra))
    if isbn:      partes.append(f"ISBN: {isbn}")
    if doi:       partes.append(f"doi:{doi}")
    if url:       partes.append(f"<a href='{url}' color='blue'>{url}</a>")

    return ". ".join([p for p in partes if p]).strip(". ") + "."

def _fmt_biblio_item(item):
    if isinstance(item, str):
        return item
    autores   = item.get("autores", "")
    anio      = item.get("anio", "") or item.get("año", "")
    titulo    = item.get("titulo", "")
    editorial = item.get("editorial", "")
    edicion   = item.get("edicion", "")
    isbn      = item.get("isbn", "")
    doi       = item.get("doi", "")
    url       = item.get("url", "")
    partes = []
    if autores:   partes.append(f"{autores}")
    if anio:      partes.append(f"({anio})")
    if titulo:    partes.append(f"<i>{titulo}</i>")
    extra = []
    if edicion:   extra.append(f"{edicion}")
    if editorial: extra.append(f"{editorial}")
    if extra:     partes.append(", ".join(extra))
    if isbn:      partes.append(f"ISBN: {isbn}")
    if doi:       partes.append(f"doi:{doi}")
    if url:       partes.append(f"<a href='{url}' color='blue'>{url}</a>")
    return ". ".join([p for p in partes if p]).strip(". ") + "."

def dibujar_bibliografia_temas(
    p, x, y, w_total,
    bibliografias,           # lista de str o dicts
    temas,                   # lista de str (ej. "1, 2, 4 y 6")
    titulo_izq="Bibliografía",
    titulo_der="Temas",
    # proporciones (sobre el ancho útil después del gap):
    col_ratios=(0.85, 0.15),
    col_gap=12,                     # separación entre columnas
    # estilos
    font="Helvetica", font_b="Helvetica-Bold",
    fs_biblio=9, leading_biblio=11,
    fs_tema=9,   leading_tema=11,
    fs_hdr=10,
    # paddings y cajas
    hdr_pad_x=10, hdr_pad_y=8, hdr_radio=6,
    row_pad_x=8,  row_pad_y=6,
    gap_hdr_body=8,
    # contornos externos por columna (solo cuerpo)
    draw_column_outline=True,
    outline_color=colors.HexColor("#D1D5DB"),
    outline_width=1,
    outline_over_header=False,   # False => contorno no cubre el header
    outline_radius=6,
    # 👉 Auto-paginación (mueve el bloque completo a la siguiente página si no cabe)
    auto_paginacion=True,
    page_width=None, page_height=None,
    top_margin=40, bottom_margin=40,
    draw_header_fn=None,         # función opcional: def fn(p,width,height)->nuevo_y
    color = colors.ReportLabBlueOLD,
):
    """
    Dibuja el bloque de Bibliografía (85%) y Temas (15%) con encabezados en cajita azul,
    filas sincronizadas y contorno redondeado SOLO del cuerpo. Si no cabe, salta de página.
    Devuelve la nueva y.
    """

    # ancho útil descontando el gap
    w_eff = max(0, w_total - col_gap)
    w_left  = w_eff * col_ratios[0]
    w_right = w_eff * col_ratios[1]

    x_left  = x
    x_right = x + w_left + col_gap

    # estilos
    style_hdr_left  = ParagraphStyle("hdrL", fontName=font_b, fontSize=fs_hdr, leading=fs_hdr+2,
                                     textColor=BLANCO, alignment=TA_LEFT)
    style_hdr_right = ParagraphStyle("hdrR", fontName=font_b, fontSize=fs_hdr, leading=fs_hdr+2,
                                     textColor=BLANCO, alignment=TA_LEFT)
    style_biblio = ParagraphStyle("bib", fontName=font, fontSize=fs_biblio, leading=leading_biblio,
                                  textColor=NEGRO, alignment=TA_LEFT)
    style_tema   = ParagraphStyle("tema", fontName=font, fontSize=fs_tema,   leading=leading_tema,
                                  textColor=NEGRO, alignment=TA_LEFT)

    # normalizar longitudes
    n_left  = len(bibliografias or [])
    n_right = len(temas or [])
    n_rows  = max(n_left, n_right)

    # medir encabezados (altura compartida)
    para_hdrL = Paragraph(titulo_izq, style_hdr_left)
    para_hdrR = Paragraph(titulo_der, style_hdr_right)
    _, h_hdrL_txt = para_hdrL.wrap(max(0, w_left  - 2*hdr_pad_x),  10**6)
    _, h_hdrR_txt = para_hdrR.wrap(max(0, w_right - 2*hdr_pad_x), 10**6)
    hdr_h = max(h_hdrL_txt, h_hdrR_txt) + 2*hdr_pad_y

    # medir filas sincronizadas
    rows = []
    total_rows_h = 0
    for i in range(n_rows):
        bib_txt  = _fmt_biblio_item(bibliografias[i]) if i < n_left else ""
        tema_txt = temas[i] if i < n_right else ""

        para_bib  = Paragraph(bib_txt,  style_biblio)
        para_tema = Paragraph(str(tema_txt), style_tema)

        _, h_bib  = para_bib.wrap(max(0, w_left  - 2*row_pad_x),  10**6)
        _, h_tema = para_tema.wrap(max(0, w_right - 2*row_pad_x), 10**6)

        row_h = max(h_bib, h_tema) + 2*row_pad_y
        rows.append((para_bib, h_bib, para_tema, h_tema, row_h))
        total_rows_h += row_h

    # alturas
    col_body_h  = total_rows_h                     # solo el cuerpo (filas)
    col_total_h = hdr_h + gap_hdr_body + col_body_h

    # -------- Auto-paginación (mueve TODO el bloque) --------
    if auto_paginacion and page_width and page_height:
        if y - col_total_h < bottom_margin:
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            if callable(draw_header_fn):
                y = draw_header_fn(p, page_width, page_height)
            else:
                y = page_height - top_margin

    # Recalcular top del cuerpo después del posible salto
    y_cursor   = y
    y_body_top = y_cursor - hdr_h - gap_hdr_body

    # ----- Encabezados (cajitas) -----
    p.setFillColor(color); p.setStrokeColor(color)
    p.roundRect(x_left,  y_cursor - hdr_h, w_left,  hdr_h, radius=hdr_radio, fill=1, stroke=0)
    p.roundRect(x_right, y_cursor - hdr_h, w_right, hdr_h, radius=hdr_radio, fill=1, stroke=0)
    para_hdrL.drawOn(p, x_left  + hdr_pad_x,  y_cursor - hdr_pad_y - h_hdrL_txt)
    para_hdrR.drawOn(p, x_right + hdr_pad_x,  y_cursor - hdr_pad_y - h_hdrR_txt)

    # ----- Contorno del cuerpo (redondeado, sin tocar encabezado) -----
    if draw_column_outline and col_body_h > 0:
        p.setStrokeColor(outline_color); p.setLineWidth(outline_width)
        if outline_over_header:
            # (opcional) contorno incluyendo header
            if outline_radius and outline_radius > 0:
                p.roundRect(x_left,  y_cursor - col_total_h, w_left,  col_total_h, radius=outline_radius, fill=0, stroke=1)
                p.roundRect(x_right, y_cursor - col_total_h, w_right, col_total_h, radius=outline_radius, fill=0, stroke=1)
            else:
                p.rect(x_left,  y_cursor - col_total_h, w_left,  col_total_h, fill=0, stroke=1)
                p.rect(x_right, y_cursor - col_total_h, w_right, col_total_h, fill=0, stroke=1)
        else:
            # 👇 solo el cuerpo
            if outline_radius and outline_radius > 0:
                p.roundRect(x_left,  y_body_top - col_body_h, w_left,  col_body_h, radius=outline_radius, fill=0, stroke=1)
                p.roundRect(x_right, y_body_top - col_body_h, w_right, col_body_h, radius=outline_radius, fill=0, stroke=1)
            else:
                p.rect(x_left,  y_body_top - col_body_h, w_left,  col_body_h, fill=0, stroke=1)
                p.rect(x_right, y_body_top - col_body_h, w_right, col_body_h, fill=0, stroke=1)

    # ----- Cuerpo (sin líneas internas) -----
    y_rows = y_body_top
    for para_bib, h_bib, para_tema, h_tema, row_h in rows:
        para_bib.drawOn(p,  x_left  + row_pad_x,  y_rows - row_pad_y - h_bib)
        para_tema.drawOn(p, x_right + row_pad_x,  y_rows - row_pad_y - h_tema)
        y_rows -= row_h

    return y - col_total_h

def dibujar_estrategias_evaluacion(
    p, x, y, w_total,
    items,                                 # [(int_0_1, "texto"), ...] o [{"checked":0/1, "texto":str}, ...]
    # --- encabezado del componente ---
    titulo="Estrategias de evaluación",
    hdr_fs=11, hdr_leading=14, hdr_pad_x=10, hdr_pad_y=8, hdr_radio=6,
    gap_after_header=8,
    # --- tabla (SIN headers): 4 columnas = [cajita, texto] | [cajita, texto]
    table_col_ratios=(0.06, 0.44, 0.06, 0.44),
    table_pad=8, cell_pad_x=6, cell_pad_y=3,
    table_radius=6, draw_table_outline=True,
    # --- tipografías / compactación ---
    fs=9, leading=11, font="Helvetica", font_b="Helvetica-Bold",
    # --- cajitas de check (tamaño fijo) ---
    chk_border_color=colors.HexColor("#D1D5DB"), chk_border_width=1, chk_box_size=11, x_mark="X",
    # --- paginación por filas (continúa tabla en páginas siguientes) ---
    auto_paginar_filas=True, page_width=None, page_height=None,
    top_margin=40, bottom_margin=40,
    draw_page_header_fn=None, # función opcional para redibujar tu encabezado GENERAL de página
    color = colors.ReportLabBlueOLD,
):
    """
    Dibuja 'Estrategias de evaluación' con una tabla dinámica SIN headers:
      - Partimos 'items' en dos mitades: IZQ -> (cajita,texto), DER -> (cajita,texto).
      - 'checked' es ENTERO (1/0). Si falta un lado en una fila, NO se dibuja cajita ahí.
      - La tabla se parte por páginas si no cabe. El título del componente se dibuja SOLO una vez.
    Devuelve la nueva y en la última página usada.
    """

    # ---- Normalización de items: soporta (int,texto) y dict {"checked":1/0,"texto":"..."} ----
    def _normalize(it):
        if it is None:
            return None
        if isinstance(it, dict):
            ch = it.get("checked", 0)
            tx = it.get("texto", "") or ""
            return (1 if int(ch) == 1 else 0), str(tx)
        if isinstance(it, (tuple, list)) and len(it) >= 2:
            try:
                ch = 1 if int(it[0]) == 1 else 0
            except Exception:
                ch = 0
            return (ch, str(it[1] or ""))
        # si no cumple, lo ignoramos
        return None

    items = [ _normalize(it) for it in (items or []) if _normalize(it) is not None ]

    # Partimos en dos mitades (izquierda/derecha)
    mid = (len(items) + 1) // 2
    left_items  = items[:mid]
    right_items = items[mid:]

    # Estilos
    style_hdr = ParagraphStyle("hdr", fontName=font_b, fontSize=hdr_fs, leading=hdr_leading,
                               textColor=BLANCO, alignment=TA_LEFT)
    style_txt = ParagraphStyle("tx",  fontName=font,   fontSize=fs,     leading=leading,
                               textColor=NEGRO, alignment=TA_LEFT)

    # ---- Título (se dibuja UNA sola vez) ----
    para_hdr = Paragraph(titulo, style_hdr)
    _, h_hdr_txt = para_hdr.wrap(max(0, w_total - 2*hdr_pad_x), 10**6)
    h_hdr_box = max(hdr_fs + 2*hdr_pad_y, h_hdr_txt + 2*hdr_pad_y)

    p.setFillColor(color); p.setStrokeColor(color)
    p.roundRect(x, y - h_hdr_box, w_total, h_hdr_box, radius=hdr_radio, fill=1, stroke=0)
    para_hdr.drawOn(p, x + hdr_pad_x, y - hdr_pad_y - h_hdr_txt)
    y_cursor = y - (h_hdr_box + gap_after_header)

    # Geometría de columnas internas
    inner_w = max(0, w_total - 2*table_pad)
    cw = [inner_w * r for r in table_col_ratios]   # [c1,c2,c3,c4]
    x_cols = []
    acc = 0
    for w in cw:
        x_cols.append(acc)
        acc += w

    # Preparamos todas las filas (alto variable) para poder paginar
    n_rows_total = max(len(left_items), len(right_items))
    rows = []
    for i in range(n_rows_total):
        L = left_items[i]  if i < len(left_items)  else None
        R = right_items[i] if i < len(right_items) else None

        # Texto por lado
        pL = Paragraph(L[1], style_txt) if (L and L[1]) else Paragraph("", style_txt)
        pR = Paragraph(R[1], style_txt) if (R and R[1]) else Paragraph("", style_txt)

        _, hL = pL.wrap(max(0, cw[1] - 2*cell_pad_x), 10**6)
        _, hR = pR.wrap(max(0, cw[3] - 2*cell_pad_x), 10**6)

        need_box_L = L is not None            # hay registro; si no, NO dibujar cajita
        need_box_R = R is not None
        min_h_from_box = 0
        if need_box_L: min_h_from_box = max(min_h_from_box, chk_box_size)
        if need_box_R: min_h_from_box = max(min_h_from_box, chk_box_size)

        row_h = max(hL, hR, min_h_from_box) + 2*cell_pad_y

        rows.append(dict(
            pL=pL, hL=hL, need_box_L=need_box_L, is_checked_L=(L[0] == 1) if L else False,
            pR=pR, hR=hR, need_box_R=need_box_R, is_checked_R=(R[0] == 1) if R else False,
            row_h=row_h
        ))

    # Función para obtener y de inicio al cambiar de página (solo encabezado GENERAL si lo pasas)
    def _y_start_new_page():
        if callable(draw_page_header_fn) and page_width and page_height:
            return draw_page_header_fn(p, page_width, page_height)
        return (page_height or 842) - top_margin

    # ---- Paginación por filas: panel por página con su contorno ----
    idx = 0
    while idx < n_rows_total:
        # ¿Cabe al menos el panel vacío?
        avail_h = y_cursor - bottom_margin
        min_panel_h = 2*table_pad + (chk_box_size + 2*cell_pad_y)  # aprox min con 1 fila breve
        if avail_h < min_panel_h and auto_paginar_filas and page_width and page_height:
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            y_cursor = _y_start_new_page()
            # no re-dibujar el título del componente

        # Empaquetamos filas que caben en esta página
        used_h = 2*table_pad
        start_idx = idx
        while idx < n_rows_total:
            next_h = rows[idx]["row_h"]
            if used_h + next_h <= (y_cursor - bottom_margin):
                used_h += next_h
                idx += 1
            else:
                # si no cabe ninguna fila, forzamos al menos una
                if idx == start_idx:
                    used_h += next_h
                    idx += 1
                break

        # Dibuja panel (contorno) para este tramo
        table_h = used_h
        if draw_table_outline:
            p.setFillColor(BLANCO); p.setStrokeColor(color); p.setLineWidth(1)
            p.roundRect(x, y_cursor - table_h, w_total, table_h, radius=table_radius, fill=1, stroke=1)

        # Área interna de este panel
        x_in = x + table_pad
        y_rows = y_cursor - table_pad

        # Dibuja filas del tramo
        for j in range(start_idx, idx):
            Rj = rows[j]
            y_top_row = y_rows
            row_h = Rj["row_h"]

            # Cajita izquierda (si hay dato)
            if Rj["need_box_L"]:
                box = chk_box_size
                y_box = y_top_row - row_h/2 - box/2
                p.setStrokeColor(chk_border_color); p.setLineWidth(chk_border_width); p.setFillColor(BLANCO)
                p.roundRect(x_in + x_cols[0] + (cw[0] - box)/2, y_box, box, box, radius=box/4, fill=1, stroke=1)
                if Rj["is_checked_L"]:
                    p.setFillColor(NEGRO); p.setFont(font_b, fs)
                    tw = p.stringWidth(x_mark, font_b, fs)
                    p.drawString(x_in + x_cols[0] + (cw[0] - tw)/2, y_box + (box - fs)/2, x_mark)

            # Texto izquierdo
            Rj["pL"].drawOn(p, x_in + x_cols[1] + cell_pad_x, y_top_row - cell_pad_y - Rj["hL"])

            # Cajita derecha (si hay dato)
            if Rj["need_box_R"]:
                box = chk_box_size
                y_box = y_top_row - row_h/2 - box/2
                p.setStrokeColor(chk_border_color); p.setFillColor(BLANCO)
                p.roundRect(x_in + x_cols[2] + (cw[2] - box)/2, y_box, box, box, radius=box/4, fill=1, stroke=1)
                if Rj["is_checked_R"]:
                    p.setFillColor(NEGRO); p.setFont(font_b, fs)
                    tw = p.stringWidth(x_mark, font_b, fs)
                    p.drawString(x_in + x_cols[2] + (cw[2] - tw)/2, y_box + (box - fs)/2, x_mark)

            # Texto derecho
            Rj["pR"].drawOn(p, x_in + x_cols[3] + cell_pad_x, y_top_row - cell_pad_y - Rj["hR"])

            y_rows -= row_h

        # Avanza Y para siguientes paneles/filas
        y_cursor -= table_h

        # Si aún quedan filas, nueva página
        if idx < n_rows_total and auto_paginar_filas and page_width and page_height:
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            y_cursor = _y_start_new_page()
            # (no redibujamos el título del componente)

    return y_cursor

def dibujar_formas_evaluacion(
    p, x, y, w_total,
    # ✅ ahora los checks pueden venir como enteros o tuplas con 1 entero
    checks_c1=None, checks_c3=None, checks_c5=None,   # 6 filas
    # textos por columnas 2, 4 y 6 (6 filas)
    col2_textos=None, col4_textos=None, col6_textos=None,
    # --- encabezado del componente ---
    titulo="Formas de evaluación",
    hdr_fs=11, hdr_leading=14, hdr_pad_x=10, hdr_pad_y=8, hdr_radio=6,
    gap_after_header=10,
    # --- tabla 6x6 ---
    table_col_ratios=(0.06, 0.27, 0.06, 0.27, 0.06, 0.28),
    headers=("", "Diagnóstica", "", "Formativa", "", "Sumativa"),
    table_pad=10, cell_pad_x=8, cell_pad_y=6,
    table_radius=6, draw_table_outline=True,
    # --- estilo de textos ---
    fs=10, leading=14, font="Helvetica", font_b="Helvetica-Bold",
    # --- cajitas de check (tamaño FIJO) ---
    chk_border_color=colors.HexColor("#D1D5DB"), chk_border_width=1, chk_box_size=14, x_mark="X",
    # --- auto paginación (sin redibujar encabezado general) ---
    auto_paginacion=True, page_width=None, page_height=None,
    bottom_margin=40, top_margin=40,
    n_rows=6,
    color = colors.ReportLabBlueOLD,
):
    """
    Bloque:
      1) Encabezado azul redondeado.
      2) Tabla n_rows x 6 con encabezados, contorno exterior redondeado.
         - Col1: cajita + 'X' SOLO en filas 0..4 (fila 5 sin cajita).
         - Col3 y Col5: cajita + 'X' según checks.
         - Col2, Col4, Col6: textos (auto-wrap).
    """

    # ---------- Normalizadores ----------
    def _pad_list(lst, n, pad):
        lst = list(lst or [])
        if len(lst) < n: lst += [pad] * (n - len(lst))
        return lst[:n]

    def _normalize_checks(raw, n):
        """
        Convierte lista de valores (1/0, (1,), (0,), [1], True/False, None)
        en lista booleana de tamaño n donde True => marcar 'X'.
        """
        raw = list(raw or [])
        out = []
        for i in range(n):
            v = raw[i] if i < len(raw) else 0
            # si viene como (1,) o [1], toma el primer elemento
            if isinstance(v, (tuple, list)):
                v = v[0] if v else 0
            # intenta llevar a int 0/1; si falla, usa bool(v)
            try:
                v_int = int(v)
            except Exception:
                v_int = 1 if bool(v) else 0
            out.append(v_int == 1)
        return out

    # ---------- Datos por defecto ----------
    if col2_textos is None:
        col2_textos = [
            "Examen diagnóstico",
            "Cuestionarios",
            "Observación",
            "Entrevistas individuales o grupales",
            "Dinámica grupal",
            ""
        ]
    if col4_textos is None:
        col4_textos = [
            "Presentación de avances",
            "Trabajos y tareas",
            "Examen parcial",
            "Exposición del alumnado",
            "Participación en clase",
            "Prácticas escolares",
        ]
    if col6_textos is None:
        col6_textos = [
            "Portafolio de evidencias",
            "Proyecto (representación, diseño producto, etc.)",
            "Propuestas de intervención",
            "Examen final",
            "Autoevaluación",
            "Coevaluación",
        ]

    col2_textos = _pad_list(col2_textos, n_rows, "")
    col4_textos = _pad_list(col4_textos, n_rows, "")
    col6_textos = _pad_list(col6_textos, n_rows, "")

    # ✅ Normaliza arrays de checks que vengan como [(1,), (0,), ...] o [1,0,...]
    c1 = _normalize_checks(checks_c1, n_rows)
    c3 = _normalize_checks(checks_c3, n_rows)
    c5 = _normalize_checks(checks_c5, n_rows)

    # ---------- Estilos ----------
    style_hdr = ParagraphStyle("hdr", fontName=font_b, fontSize=hdr_fs, leading=hdr_leading,
                               textColor=BLANCO, alignment=TA_LEFT)
    style_th  = ParagraphStyle("th",  fontName=font_b, fontSize=fs,     leading=fs+2,
                               textColor=NEGRO, alignment=TA_LEFT)
    style_c2  = ParagraphStyle("c2",  fontName=font,   fontSize=fs,     leading=leading,
                               textColor=NEGRO, alignment=TA_LEFT)
    style_c4  = ParagraphStyle("c4",  fontName=font,   fontSize=fs,     leading=leading,
                               textColor=NEGRO, alignment=TA_LEFT)
    style_c6  = ParagraphStyle("c6",  fontName=font,   fontSize=fs,     leading=leading,
                               textColor=NEGRO, alignment=TA_LEFT)

    # ---------- Encabezado ----------
    para_hdr = Paragraph(titulo, style_hdr)
    _, h_hdr_txt = para_hdr.wrap(max(0, w_total - 2*hdr_pad_x), 10**6)
    h_hdr_box = max(hdr_fs + 2*hdr_pad_y, h_hdr_txt + 2*hdr_pad_y)

    # ---------- Medición tabla ----------
    inner_w = max(0, w_total - 2*table_pad)
    cw = [inner_w * r for r in table_col_ratios]
    x_cols = [0]*6; acc = 0
    for i in range(6):
        x_cols[i] = acc
        acc += cw[i]

    # Encabezados
    th_paras = [Paragraph(str(h or ""), style_th) for h in headers]
    th_heights = []
    for i in range(6):
        _, hh = th_paras[i].wrap(max(0, cw[i] - 2*cell_pad_x), 10**6)
        th_heights.append(hh)
    h_th_row = max(th_heights) + 2*cell_pad_y

    # Filas (n_rows)
    rows_info, total_rows_h = [], 0
    for i in range(n_rows):
        p2 = Paragraph(col2_textos[i], style_c2)
        p4 = Paragraph(col4_textos[i], style_c4)
        p6 = Paragraph(col6_textos[i], style_c6)
        _, h2 = p2.wrap(max(0, cw[1] - 2*cell_pad_x), 10**6)
        _, h4 = p4.wrap(max(0, cw[3] - 2*cell_pad_x), 10**6)
        _, h6 = p6.wrap(max(0, cw[5] - 2*cell_pad_x), 10**6)
        row_h = max(h2, h4, h6, chk_box_size) + 2*cell_pad_y
        rows_info.append((p2, h2, p4, h4, p6, h6, row_h))
        total_rows_h += row_h

    table_h = 2*table_pad + h_th_row + total_rows_h
    alto_total = h_hdr_box + gap_after_header + table_h

    # ---------- Auto-paginación ----------
    if auto_paginacion and page_width and page_height:
        if y - alto_total < bottom_margin:
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            y = page_height - top_margin

    # ---------- DIBUJO ----------
    y_cursor = y

    # Encabezado
    p.setFillColor(color); p.setStrokeColor(color)
    p.roundRect(x, y_cursor - h_hdr_box, w_total, h_hdr_box, radius=hdr_radio, fill=1, stroke=0)
    para_hdr.drawOn(p, x + hdr_pad_x, y_cursor - hdr_pad_y - h_hdr_txt)
    y_cursor -= (h_hdr_box + gap_after_header)

    # Contorno tabla
    if draw_table_outline:
        p.setFillColor(BLANCO); p.setStrokeColor(color); p.setLineWidth(1)
        p.roundRect(x, y_cursor - table_h, w_total, table_h, radius=table_radius, fill=1, stroke=1)

    # Área interna
    x_in = x + table_pad
    y_top = y_cursor - table_pad

    # Encabezados (texto simple)
    for i in range(6):
        th_paras[i].drawOn(p, x_in + x_cols[i] + cell_pad_x, y_top - cell_pad_y - th_heights[i])
    y_body_top = y_top - h_th_row

    # Filas del cuerpo
    y_rows = y_body_top
    for i in range(n_rows):
        p2, h2, p4, h4, p6, h6, row_h = rows_info[i]
        y_top_row = y_rows

        box_w = box_h = chk_box_size
        y_box = y_top_row - row_h/2 - box_h/2

        # Col 1: cajita solo filas 0..4
        if i < 5:
            p.setStrokeColor(chk_border_color); p.setLineWidth(chk_border_width); p.setFillColor(BLANCO)
            p.roundRect(x_in + x_cols[0] + (cw[0] - box_w)/2, y_box, box_w, box_h, radius=box_h/4, fill=1, stroke=1)
            if c1[i]:
                p.setFillColor(NEGRO); p.setFont(font_b, fs)
                tw = p.stringWidth(x_mark, font_b, fs)
                p.drawString(x_in + x_cols[0] + (cw[0] - tw)/2, y_box + (box_h - fs)/2, x_mark)

        # Col 2
        p2.drawOn(p, x_in + x_cols[1] + cell_pad_x, y_top_row - cell_pad_y - h2)

        # Col 3
        p.setStrokeColor(chk_border_color); p.setFillColor(BLANCO)
        p.roundRect(x_in + x_cols[2] + (cw[2] - box_w)/2, y_box, box_w, box_h, radius=box_h/4, fill=1, stroke=1)
        if c3[i]:
            p.setFillColor(NEGRO); p.setFont(font_b, fs)
            tw = p.stringWidth(x_mark, font_b, fs)
            p.drawString(x_in + x_cols[2] + (cw[2] - tw)/2, y_box + (box_h - fs)/2, x_mark)

        # Col 4
        p4.drawOn(p, x_in + x_cols[3] + cell_pad_x, y_top_row - cell_pad_y - h4)

        # Col 5
        p.setStrokeColor(chk_border_color); p.setFillColor(BLANCO)
        p.roundRect(x_in + x_cols[4] + (cw[4] - box_w)/2, y_box, box_w, box_h, radius=box_h/4, fill=1, stroke=1)
        if c5[i]:
            p.setFillColor(NEGRO); p.setFont(font_b, fs)
            tw = p.stringWidth(x_mark, font_b, fs)
            p.drawString(x_in + x_cols[4] + (cw[4] - tw)/2, y_box + (box_h - fs)/2, x_mark)

        # Col 6
        p6.drawOn(p, x_in + x_cols[5] + cell_pad_x, y_top_row - cell_pad_y - h6)

        y_rows -= row_h

    return y - alto_total

def dibujar_parrafo_with_title(
    p, x, y, w_total,
    texto,                                  # contenido largo (puede tener <b>, <i>, <br/>, etc.)
    titulo="Formación integral",
    # Encabezado del componente
    hdr_fs=11, hdr_leading=14, hdr_pad_x=10, hdr_pad_y=8, hdr_radio=6,
    gap_after_header=10,
    # Panel 1x1 (cajita) que fluye
    body_pad_x=10, body_pad_y=10, body_radius=6,
    fs=10, leading=14, font="Helvetica", font_b="Helvetica-Bold",
    # Auto-paginación
    auto_paginacion=True, page_width=None, page_height=None,
    top_margin=40, bottom_margin=40,
    draw_page_header_fn=None,   # función opcional para redibujar TU encabezado general por página
    color = colors.ReportLabBlueOLD,
):
    """
    Dibuja:
      1) Encabezado azul redondeado con 'Formación integral'.
      2) Un panel 1x1 (cajita redondeada) que contiene 'texto' y se parte en varias páginas si es necesario.
    Al continuar en páginas siguientes, NO repite el encabezado del componente.
    Devuelve la nueva y de la ÚLTIMA página usada.
    """
    # ----- Estilos -----
    style_hdr = ParagraphStyle(
        "hdr", fontName=font_b, fontSize=hdr_fs, leading=hdr_leading,
        textColor=BLANCO, alignment=TA_LEFT
    )
    style_body = ParagraphStyle(
        "body", fontName=font, fontSize=fs, leading=leading,
        textColor=NEGRO, alignment=TA_JUSTIFY
    )

    # ----- Medición del encabezado -----
    para_hdr = Paragraph(titulo, style_hdr)
    _, h_hdr_txt = para_hdr.wrap(max(0, w_total - 2*hdr_pad_x), 10**6)
    h_hdr_box = max(hdr_fs + 2*hdr_pad_y, h_hdr_txt + 2*hdr_pad_y)

    # ----- Dibujo del encabezado -----
    p.setFillColor(color); p.setStrokeColor(color)
    p.roundRect(x, y - h_hdr_box, w_total, h_hdr_box, radius=hdr_radio, fill=1, stroke=0)
    para_hdr.drawOn(p, x + hdr_pad_x, y - hdr_pad_y - h_hdr_txt)

    # Coordenada para empezar el panel 1x1
    y_cursor = y - (h_hdr_box + gap_after_header)

    # ----- Preparar el texto a fluir -----
    avail_w = max(0, w_total - 2*body_pad_x)
    remaining = Paragraph(texto or "", style_body)

    def _page_y_start():
        """Devuelve la y inicial al cambiar de página (sin repetir este encabezado de componente)."""
        if callable(draw_page_header_fn) and page_width and page_height:
            return draw_page_header_fn(p, page_width, page_height)
        # si no hay header general, usa margen superior
        return (page_height or 842) - top_margin  # 842 ≈ A4 alto por si no pasan page_height

    # ----- Loop de flujo en múltiples páginas -----
    while True:
        # ¿Hay espacio mínimo en esta página para dibujar una cajita?
        min_box_h = fs + 2*body_pad_y + 2
        if y_cursor - bottom_margin < min_box_h:
            # Salta de página y NO redibuja el encabezado de la sección
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            y_cursor = _page_y_start()

        # Altura disponible para el CONTENIDO interno del panel en esta página
        avail_h_panel = y_cursor - bottom_margin
        inner_h = max(0, avail_h_panel - 2*body_pad_y)

        # Si ni siquiera cabe el padding mínimo, salta página otra vez
        if inner_h <= 0:
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            y_cursor = _page_y_start()
            continue

        # Partir el párrafo para esta página
        parts = remaining.split(avail_w, inner_h)
        this_part = parts[0]
        _, h_part = this_part.wrap(avail_w, inner_h)

        # Altura real de la cajita para esta página
        box_h = h_part + 2*body_pad_y

        # Dibujo de cajita redondeada (panel 1x1 en esta página)
        p.setFillColor(BLANCO); p.setStrokeColor(color); p.setLineWidth(1)
        p.roundRect(x, y_cursor - box_h, w_total, box_h, radius=body_radius, fill=1, stroke=1)

        # Texto dentro
        this_part.drawOn(p, x + body_pad_x, y_cursor - body_pad_y - h_part)

        # Actualizar y
        y_cursor -= box_h

        # ¿Queda texto por dibujar?
        if len(parts) == 1:
            break  # ya terminamos
        else:
            # continuar con el resto en la siguiente página
            remaining = parts[1]
            dibujar_marca_agua(p, page_width, page_height, habilitada = watermark_on)
            p.showPage()
            y_cursor = _page_y_start()
            # IMPORTANTE: NO redibujar el encabezado del componente

    return y_cursor


def to_snake_case(texto: str) -> str:
    # Normalizar y eliminar acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')

    # Pasar a minúsculas
    texto = texto.lower()

    # Reemplazar caracteres no alfanuméricos por guiones bajos
    texto = re.sub(r'[^a-z0-9]+', '_', texto)

    # Quitar guiones bajos al inicio/fin y dobles
    texto = texto.strip('_')
    texto = re.sub(r'_+', '_', texto)

    return texto


def get_bibliografia_str(fila):
    id_, autor, anio, titulo, extra1, extra2, extra3, extra4, temas = fila
    anio
    if anio == 0:
        anio_ = 's.f.'
    else:
        anio_ = f"({anio})."
    # Libro impreso || Libro electronico || Apuntes de clase || Material Audiovisual || tesis || Informe || web
    if id_ == 1 or id_ == 2  or id_ == 6 or id_ == 7 or id_ == 8 or id_ == 9 or id_ == 10:
        titulo =  f"<i>{titulo}</i>"
    if id_ == 3 or 4:  #Articulo Impreso || Articulo electronico
        extra1 = f"<i>{extra1}</i>"
    partes = [
        autor,
        anio_,
        titulo,
        extra1,
        extra2,
        extra3,
        extra4
    ]
    biblio_format = " ".join(p for p in partes if p)
    return biblio_format


def dibujar_marca_agua(
    p, width, height,
    habilitada = watermark_on,
    texto="DOCUMENTO NO OFICIAL",
    angulo=45,                 # grados
    font="Helvetica-Bold",
    font_size=64,
    color=colors.HexColor("#FF000080", hasAlpha=True),         # gris claro
    opacidad=0.02,             # 0.0 transparente, 1.0 opaco
):
    """
    Dibuja una marca de agua diagonal centrada si 'habilitada' es True.
    Llama esta función en cada página (normalmente justo ANTES de p.showPage()).
    """
    if not habilitada:
        return

    p.saveState()
    try:
        # Opacidad (si tu versión de reportlab soporta setFillAlpha)
        if hasattr(p, "setFillAlpha"):
            p.setFillAlpha(opacidad)
    except Exception:
        pass  # si no hay soporte de alpha, seguimos sin transparencia

    p.setFillColor(color)
    p.setFont(font, font_size)

    # Mover al centro y rotar
    p.translate(width / 2.0, height / 2.0)
    p.rotate(angulo)

    # Centrar el texto
    tw = p.stringWidth(texto, font, font_size)
    p.drawString(-tw / 2.0, -font_size / 2.0, texto)

    p.restoreState()


def normalize_name(name: str) -> str:
    # Convert to lowercase
    name = name.lower()

    # Replace spaces with underscores
    name = name.replace(" ", "_")

    # Normalize accents (e.g., Á -> á)
    # The 'NFC' form ensures composed characters like á stay as one character
    name = unicodedata.normalize("NFC", name)

    return name


def draw_header_table(c: canvas.Canvas, x: float, y: float, width: float, color, clave: str, nombre: str):
    """
    Dibuja encabezados de texto ("Clave" y "Nombre") arriba,
    y debajo dos cajas con valores (clave y nombre):
      - Izquierda: solo contorno del color.
      - Derecha: relleno completo del mismo color.
      - Ambas con esquinas redondeadas y separación entre columnas.
      - Sin sobrepintado ni bordes blancos.

    Args:
        c (canvas.Canvas): lienzo de ReportLab.
        x, y (float): coordenadas inferiores izquierdas.
        width (float): ancho total.
        color: color de ReportLab (ej. colors.HexColor("#007ACC")).
        clave (str): valor de la columna "Clave".
        nombre (str): valor de la columna "Nombre".

    Returns:
        float: nueva coordenada y (para continuar dibujando debajo).
    """
    # ---- Dimensiones ----
    col_gap = 10
    col1_width = width * 0.1
    col2_width = width * 0.9 - col_gap
    height = 25
    radius = 4

    # ---- Encabezados (fuera de las cajas) ----
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    c.drawString(x, y + height + 8, "Clave")
    c.drawString(x + col1_width + col_gap, y + height + 8, "Nombre")

    # ---- Caja 1 (contorno solamente) ----
    c.setLineWidth(1)
    c.setStrokeColor(color)
    c.setFillColor(colors.white)
    c.roundRect(x, y, col1_width, height, radius, stroke=1, fill=0)

    # ---- Caja 2 (relleno completo) ----
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.roundRect(x + col1_width + col_gap, y, col2_width, height, radius, stroke=1, fill=1)

    # ---- Dibujar textos dentro de las cajas ----
    # Clave
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    text_y = y + height / 2 - 3  # centrado vertical aproximado
    c.drawString(x + 5, text_y, clave)

    # Nombre (texto blanco sobre fondo de color)
    c.setFillColor(colors.white)
    c.drawString(x + col1_width + col_gap + 5, text_y, nombre)

    # ---- Devolver nueva posición y ----
    return y - 12

def draw_info_table(c: canvas.Canvas, x: float, y: float, width: float, color,
                    semestre: str, creditos: str, fase: str, licenciatura: str):
    """
    Dibuja una fila de 4 columnas con encabezados arriba y valores dentro de cajas redondeadas:
      - Columnas: "Semestre", "Créditos", "Fase", "Licenciatura"
      - Distribución: 10%, 10%, 10%, 70%
      - Las tres primeras columnas tienen solo contorno del color.
      - La última columna tiene fondo completo del color.
      - Texto centrado verticalmente.
      - Devuelve la nueva posición y para continuar dibujando.

    Args:
        c (canvas.Canvas): lienzo de ReportLab.
        x, y (float): coordenadas inferiores izquierdas.
        width (float): ancho total de la fila.
        color: color de ReportLab (ej. colors.HexColor("#007ACC")).
        semestre (str): valor de la columna 1.
        creditos (str): valor de la columna 2.
        fase (str): valor de la columna 3.
        licenciatura (str): valor de la columna 4.

    Returns:
        float: nueva coordenada y (para continuar dibujando debajo).
    """
    # ---- Dimensiones ----
    col_gap = 10
    proportions = [0.10, 0.10, 0.10, 0.70]
    col_widths = [width * p for p in proportions]
    col_widths[3] -= col_gap * 3  # ajustar por espacios entre columnas
    height = 25
    radius = 4
    text_y = y + height / 2 - 3  # centrado vertical

    # ---- Encabezados ----
    headers = ["Semestre", "Créditos", "Fase", "Licenciatura"]
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)

    x_pos = x
    for i, header in enumerate(headers):
        c.drawString(x_pos, y + height + 8, header)
        if i < 3:
            x_pos += col_widths[i] + col_gap
        else:
            x_pos += col_widths[i]

    # ---- Dibujar cajas y valores ----
    values = [semestre, creditos, fase, licenciatura]
    x_pos = x

    for i, val in enumerate(values):
        if i < 3:
            # Contorno solamente
            c.setLineWidth(1)
            c.setStrokeColor(color)
            c.setFillColor(colors.white)
            c.roundRect(x_pos, y, col_widths[i], height, radius, stroke=1, fill=0)
            c.setFont("Helvetica", 11)
            c.setFillColor(colors.black)
        else:
            # Última columna: relleno completo
            c.setStrokeColor(color)
            c.setFillColor(color)
            c.roundRect(x_pos, y, col_widths[i], height, radius, stroke=1, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica", 12)

        # Texto dentro de la caja
        c.drawString(x_pos + 5, text_y, val)

        # Avanzar al siguiente bloque
        if i < 3:
            x_pos += col_widths[i] + col_gap
        else:
            x_pos += col_widths[i]

    # ---- Devolver nueva posición y ----
    return y - 12
