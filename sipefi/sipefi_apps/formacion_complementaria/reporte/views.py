# -*- coding: utf-8 -*-
import logging
import os
import re
import unicodedata
from html import escape as html_escape
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from sipefi_apps.formacion_complementaria.reporte.ConsultasPDF import (
    ConsultasPDFFormacionComplementaria,
)
from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as ConsultasTomoII

logger = logging.getLogger(__name__)

BLANCO = colors.white
NEGRO = colors.black
GRIS_SUAVE = colors.HexColor("#F3F4F6")
GRIS_BORDE = colors.HexColor("#D1D5DB")
ROJO_TITULO = colors.red

COLORES_AREA = {
    1: "#FFD400",
    2: "#5DBE63",
    3: "#BDA982",
    4: "#4DC8E7",
    5: "#4F617C",
    6: "#AC92C5",
    7: "#F07B22",
}

FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"


def _registrar_fuentes():
    """Se reutilizan las fuentes del PDF de TOMO II"""
    global FONT_NORMAL, FONT_BOLD, FONT_ITALIC
    font_dir = Path(settings.BASE_DIR) / "sipefi_apps" / "tomo_ii" / "reporte" / "fonts"
    archivos = {
        "FCFreeSans": "FreeSans.ttf",
        "FCFreeSansBold": "FreeSansBold.ttf",
        "FCFreeSansOblique": "FreeSansOblique.ttf",
    }
    try:
        for nombre, archivo in archivos.items():
            ruta = font_dir / archivo
            if nombre not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(nombre, str(ruta)))
        FONT_NORMAL = "FCFreeSans"
        FONT_BOLD = "FCFreeSansBold"
        FONT_ITALIC = "FCFreeSansOblique"
    except Exception:
        # Helvetica cubre correctamente el flujo aun si en algún ambiente faltan las fuentes.
        logger.warning("No fue posible registrar FreeSans para el PDF de FC; se usará Helvetica.", exc_info=True)


_registrar_fuentes()


def _texto(valor):
    if valor is None:
        return ""
    return str(valor)


def _markup(valor):
    return html_escape(_texto(valor), quote=False).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")


def _normalizar_nombre_archivo(nombre):
    texto = unicodedata.normalize("NFKD", _texto(nombre)).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^A-Za-z0-9_-]+", "_", texto).strip("_")
    return texto[:100] or "formacion_complementaria"


def _entero_visual(valor):
    if valor in (None, ""):
        return ""
    try:
        return str(int(float(valor)))
    except (TypeError, ValueError):
        return _texto(valor)


def _nueva_pagina(p, height, top_margin=40):
    p.showPage()
    return height - top_margin


def _dibujar_encabezado_institucional(p, width, height):
    logo_unam = Path(settings.BASE_DIR) / "estaticos" / "imagenes" / "escudounam_negro.jpg"
    logo_fi = Path(settings.BASE_DIR) / "estaticos" / "imagenes" / "escudofi_negro.jpg"

    logo_width = 60
    logo_height = 60
    top_y = height - 70

    if logo_unam.exists():
        p.drawImage(ImageReader(str(logo_unam)), 50, top_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
    else:
        logger.warning("Logo UNAM no encontrado para PDF FC: %s", logo_unam)

    if logo_fi.exists():
        p.drawImage(
            ImageReader(str(logo_fi)), width - 50 - logo_width, top_y,
            width=logo_width, height=logo_height, preserveAspectRatio=True,
        )
    else:
        logger.warning("Logo FI no encontrado para PDF FC: %s", logo_fi)

    p.setFillColor(NEGRO)
    p.setFont(FONT_BOLD, 10)
    textos = (
        "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO",
        "FACULTAD DE INGENIERÍA",
    )
    for indice, texto in enumerate(textos):
        tw = p.stringWidth(texto, FONT_BOLD, 10)
        p.drawString((width - tw) / 2, top_y + logo_height / 2 - (indice * 12), texto)

    y_line = top_y + logo_height / 2 - 40
    _dibujar_linea_titulo(p, y_line, "PROGRAMA DE FORMACIÓN COMPLEMENTARIA", width)
    return height - 130


def _dibujar_linea_titulo(p, y, texto, width):
    p.setFont(FONT_NORMAL, 12)
    text_width = p.stringWidth(texto, FONT_NORMAL, 12)
    p.setStrokeColor(ROJO_TITULO)
    p.setLineWidth(1)
    p.line(0, y, (width - text_width) / 2 - 10, y)
    p.line((width + text_width) / 2 + 10, y, width, y)
    p.setFillColor(ROJO_TITULO)
    p.drawString((width - text_width) / 2, y - 5, texto)
    p.setFillColor(NEGRO)
    p.setStrokeColor(NEGRO)


def _dibujar_clave_nombre(p, x, y, w_total, color, clave, nombre):
    gap = 10
    w_clave = max(76, w_total * 0.16)
    w_nombre = w_total - w_clave - gap
    pad_x = 8
    pad_y = 7

    p.setFillColor(NEGRO)
    p.setFont(FONT_BOLD, 11)
    p.drawString(x, y, "Clave")
    p.drawString(x + w_clave + gap, y, "Nombre")
    y_box_top = y - 8

    style_clave = ParagraphStyle(
        "fc_clave", fontName=FONT_NORMAL, fontSize=10, leading=12,
        textColor=NEGRO, alignment=TA_CENTER,
    )
    style_nombre = ParagraphStyle(
        "fc_nombre", fontName=FONT_NORMAL, fontSize=10, leading=12,
        textColor=BLANCO, alignment=TA_LEFT,
    )
    para_clave = Paragraph(_markup(clave), style_clave)
    para_nombre = Paragraph(_markup(nombre), style_nombre)
    _, h1 = para_clave.wrap(w_clave - 2 * pad_x, 10000)
    _, h2 = para_nombre.wrap(w_nombre - 2 * pad_x, 10000)
    box_h = max(28, max(h1, h2) + 2 * pad_y)

    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x, y_box_top - box_h, w_clave, box_h, 4, fill=1, stroke=1)

    p.setFillColor(color)
    p.setStrokeColor(color)
    p.roundRect(x + w_clave + gap, y_box_top - box_h, w_nombre, box_h, 4, fill=1, stroke=1)

    para_clave.drawOn(p, x + pad_x, y_box_top - pad_y - h1 - (box_h - h1 - 2 * pad_y) / 2)
    para_nombre.drawOn(p, x + w_clave + gap + pad_x, y_box_top - pad_y - h2 - (box_h - h2 - 2 * pad_y) / 2)
    return y_box_top - box_h - 18


def _dibujar_celda_info(p, x, y_top, width, etiqueta, valor, color, relleno=False, center=False):
    p.setFillColor(NEGRO)
    p.setFont(FONT_BOLD, 9.5)
    p.drawString(x, y_top, etiqueta)

    box_top = y_top - 7
    style = ParagraphStyle(
        f"fc_info_{etiqueta}_{x}",
        fontName=FONT_NORMAL,
        fontSize=9.5,
        leading=11.5,
        textColor=BLANCO if relleno else NEGRO,
        alignment=TA_CENTER if center else TA_LEFT,
    )
    para = Paragraph(_markup(valor), style)
    pad_x = 7
    pad_y = 6
    _, h = para.wrap(width - 2 * pad_x, 10000)
    box_h = max(27, h + 2 * pad_y)

    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.setFillColor(color if relleno else BLANCO)
    p.roundRect(x, box_top - box_h, width, box_h, 4, fill=1, stroke=1)
    para.drawOn(p, x + pad_x, box_top - pad_y - h - (box_h - h - 2 * pad_y) / 2)
    return box_h + 7


def _dibujar_datos_generales(p, x, y, w_total, color, info):
    gap = 10

    # Fila 1: Área del conocimiento | Semestre | Modalidad
    ratios = (0.50, 0.14, 0.36)
    widths = [w_total * r for r in ratios]
    widths[-1] -= 2 * gap
    xs = [x, x + widths[0] + gap, x + widths[0] + widths[1] + 2 * gap]
    alturas = [
        _dibujar_celda_info(p, xs[0], y, widths[0], "Área del conocimiento", info.get("area_conocimiento"), color, relleno=True),
        _dibujar_celda_info(p, xs[1], y, widths[1], "Semestre", _entero_visual(info.get("semestre")), color, center=True),
        _dibujar_celda_info(p, xs[2], y, widths[2], "Modalidad", info.get("modalidad"), color),
    ]
    y -= max(alturas) + 14

    # Fila 2: Tipo | Carácter | Horas Semana | Horas Semestre
    ratios2 = (0.23, 0.23, 0.27, 0.27)
    widths2 = [w_total * r for r in ratios2]
    widths2[-1] -= 3 * gap
    xs2 = [x]
    for i in range(1, 4):
        xs2.append(xs2[-1] + widths2[i - 1] + gap)
    valores = [
        ("Tipo", info.get("tipo_modalidad")),
        ("Carácter", info.get("caracter_asignatura")),
        ("Horas Semana", _entero_visual(info.get("horas_pract_semana"))),
        ("Horas Semestre", _entero_visual(info.get("horas_pract_semestre"))),
    ]
    alturas2 = [
        _dibujar_celda_info(p, xs2[i], y, widths2[i], etiqueta, valor, color, center=i >= 2)
        for i, (etiqueta, valor) in enumerate(valores)
    ]
    return y - max(alturas2) - 6


def _dibujar_objetivo(p, x, y, w_total, texto, color, width, height, bottom_margin=40):
    titulo = "Objetivo general de la asignatura:"
    hdr_style = ParagraphStyle(
        "fc_obj_hdr", fontName=FONT_BOLD, fontSize=10, leading=12,
        textColor=NEGRO, alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "fc_obj_body", fontName=FONT_NORMAL, fontSize=10, leading=14,
        textColor=NEGRO, alignment=TA_JUSTIFY,
    )
    hdr = Paragraph(titulo, hdr_style)
    _, h_hdr = hdr.wrap(w_total, 10000)
    para = Paragraph(_markup(texto), body_style)
    avail_w = w_total - 20
    _, h_txt = para.wrap(avail_w, 10000)
    box_h = max(30, h_txt + 20)
    total_h = h_hdr + 6 + box_h
    if y - total_h < bottom_margin:
        y = _nueva_pagina(p, height)

    hdr.drawOn(p, x, y - h_hdr)
    box_top = y - h_hdr - 6
    p.setFillColor(BLANCO)
    p.setStrokeColor(color)
    p.setLineWidth(1)
    p.roundRect(x, box_top - box_h, w_total, box_h, 5, fill=1, stroke=1)
    para.drawOn(p, x + 10, box_top - 10 - h_txt)
    return box_top - box_h


def _dibujar_titulo_temario(p, x, y, w_total):
    titulo = "Temario"
    p.setFont(FONT_BOLD, 11)
    p.setFillColor(NEGRO)
    p.drawString(x, y - 11, titulo)
    ly = y - 15
    p.setStrokeColor(GRIS_BORDE)
    p.setLineWidth(1)
    p.line(x, ly, x + w_total, ly)
    return ly - 7


def _dibujar_temario(p, x, y, w_total, temas, color, width, height, bottom_margin=40):
    y = _dibujar_titulo_temario(p, x, y, w_total)
    col_ratios = (0.08, 0.77, 0.15)
    col_w = [w_total * r for r in col_ratios]
    x_cols = [x, x + col_w[0], x + col_w[0] + col_w[1]]
    headers = ("Núm.", "Tema", "Horas")
    style_h = ParagraphStyle("fc_th", fontName=FONT_BOLD, fontSize=9.5, leading=11, alignment=TA_LEFT)
    styles = [
        ParagraphStyle("fc_t1", fontName=FONT_NORMAL, fontSize=9.5, leading=12, alignment=TA_CENTER),
        ParagraphStyle("fc_t2", fontName=FONT_NORMAL, fontSize=9.5, leading=12, alignment=TA_LEFT),
        ParagraphStyle("fc_t3", fontName=FONT_NORMAL, fontSize=9.5, leading=12, alignment=TA_CENTER),
    ]
    pad_x = 7
    pad_y = 5

    def dibujar_header(y_top):
        paras = [Paragraph(_markup(h), style_h) for h in headers]
        hs = [paras[i].wrap(col_w[i] - 2 * pad_x, 10000)[1] for i in range(3)]
        rh = max(hs) + 2 * pad_y
        p.setFillColor(GRIS_SUAVE)
        p.setStrokeColor(color)
        p.rect(x, y_top - rh, w_total, rh, fill=1, stroke=1)
        p.line(x_cols[1], y_top, x_cols[1], y_top - rh)
        p.line(x_cols[2], y_top, x_cols[2], y_top - rh)
        for i, para in enumerate(paras):
            para.drawOn(p, x_cols[i] + pad_x, y_top - pad_y - hs[i])
        return y_top - rh

    y = dibujar_header(y)
    total_horas = 0
    for tema in temas or []:
        valores = (
            _entero_visual(tema.get("num_tema")),
            tema.get("tema") or "",
            _entero_visual(tema.get("horas_tema")),
        )
        try:
            total_horas += int(float(tema.get("horas_tema") or 0))
        except (TypeError, ValueError):
            pass
        paras = [Paragraph(_markup(valores[i]), styles[i]) for i in range(3)]
        hs = [paras[i].wrap(col_w[i] - 2 * pad_x, 10000)[1] for i in range(3)]
        rh = max(24, max(hs) + 2 * pad_y)
        if y - rh < bottom_margin:
            y = _nueva_pagina(p, height)
            y = dibujar_header(y)
        p.setFillColor(BLANCO)
        p.setStrokeColor(color)
        p.rect(x, y - rh, w_total, rh, fill=1, stroke=1)
        p.line(x_cols[1], y, x_cols[1], y - rh)
        p.line(x_cols[2], y, x_cols[2], y - rh)
        for i, para in enumerate(paras):
            para.drawOn(p, x_cols[i] + pad_x, y - pad_y - hs[i] - (rh - hs[i] - 2 * pad_y) / 2)
        y -= rh

    # Resumen de horas del temario.
    summary_w = col_w[2]
    label_w = w_total - summary_w
    summary_h = 24
    if y - summary_h < bottom_margin:
        y = _nueva_pagina(p, height)
    p.setFont(FONT_BOLD, 9.5)
    p.setFillColor(NEGRO)
    label = "TOTAL HORAS"
    tw = p.stringWidth(label, FONT_BOLD, 9.5)
    p.drawString(x + label_w - tw - 8, y - 16, label)
    p.setFillColor(GRIS_SUAVE)
    p.setStrokeColor(color)
    p.rect(x + label_w, y - summary_h, summary_w, summary_h, fill=1, stroke=1)
    val = str(total_horas)
    p.setFillColor(NEGRO)
    twv = p.stringWidth(val, FONT_BOLD, 9.5)
    p.drawString(x + label_w + (summary_w - twv) / 2, y - 16, val)
    return y - summary_h


def _normalizar_tipo_biblio(tipo):
    texto = unicodedata.normalize("NFKD", _texto(tipo)).encode("ascii", "ignore").decode("ascii").upper().strip()
    return re.sub(r"\s+", " ", texto)


def _link_markup(url):
    url = _texto(url).strip()
    if not url:
        return ""
    limpio = html_escape(url, quote=True)
    return f"<a href='{limpio}' color='blue'>{html_escape(url, quote=False)}</a>"


def _formatear_bibliografia(item):
    tipo = _normalizar_tipo_biblio(item.get("tipo_bibliografia"))
    autor = _markup(item.get("autor"))
    anio_raw = item.get("publicacion")
    anio = "(s.f.)." if anio_raw in (None, "", 0, "0") else f"({_markup(anio_raw)})."
    titulo = _markup(item.get("titulo"))
    c1 = _markup(item.get("campo_1"))
    c2 = _markup(item.get("campo_2"))
    c3 = _texto(item.get("campo_3")).strip()
    c4 = _markup(item.get("campo_4"))

    partes = []
    if autor:
        partes.append(autor)
    if anio:
        partes.append(anio)

    es_articulo = "ARTICULO" in tipo
    if titulo:
        partes.append(f"{titulo}." if es_articulo else f"<i>{titulo}</i>.")

    if "LIBRO IMPRESO" in tipo:
        if c2 and c2 != "1":
            partes.append(f"({c2}.ª ed.)." if c2.isdigit() else f"({c2}).")
        if c1:
            partes.append(f"{c1}.")
    elif "LIBRO ELECTRONICO" in tipo:
        if c2 and c2 != "1":
            partes.append(f"({c2}.ª ed.)." if c2.isdigit() else f"({c2}).")
        if c1:
            partes.append(f"{c1}.")
        link = _link_markup(c3)
        if link:
            partes.append(link)
    elif "ARTICULO" in tipo:
        if c1:
            partes.append(f"<i>{c1}</i>,")
        if c2:
            partes.append(f"<i>{c2}</i>,")
        if c3:
            partes.append(f"{_markup(c3)}.")
        link = _link_markup(_texto(item.get("campo_4")))
        if link:
            partes.append(link)
    elif "NORMA" in tipo or "LEY" in tipo:
        if c1:
            partes.append(f"({c1}).")
        if c2:
            partes.append(f"{c2}.")
        link = _link_markup(c3)
        if link:
            partes.append(link)
        if c4:
            partes.append(f"Fecha: {c4}.")
    elif "APUNTES" in tipo:
        if c1:
            partes.append(f"[{c1}].")
        if c4:
            partes.append(f"{c4},")
        if c2:
            partes.append(f"{c2}.")
        link = _link_markup(c3)
        if link:
            partes.append(link)
    elif "AUDIOVISUAL" in tipo:
        if c1:
            partes.append(f"[{c1}].")
        if c2:
            partes.append(f"{c2}.")
        link = _link_markup(c3)
        if link:
            partes.append(link)
        if c4:
            partes.append(f"{c4}.")
    elif "TESIS" in tipo:
        extra = ", ".join(x for x in (c1, c2) if x)
        if extra:
            partes.append(f"({extra}).")
        link = _link_markup(c3)
        if link:
            partes.append(link)
    elif "INFORME" in tipo:
        if c1:
            partes.append(f"({c1}).")
        if c2:
            partes.append(f"{c2}.")
        link = _link_markup(c3)
        if link:
            partes.append(link)
    elif "PAGINA WEB" in tipo:
        if c1:
            partes.append(f"{c1}.")
        link = _link_markup(_texto(item.get("campo_2")))
        if link:
            partes.append(link)
        if c3:
            partes.append(f"(Consultado el {_markup(c3)}).")
    elif "DEPENDERA" in tipo:
        return "Dependerá de la temática a tratar."
    else:
        for extra in (c1, c2, _markup(c3), c4):
            if extra:
                partes.append(extra)

    return " ".join(parte for parte in partes if parte).strip()


def _dibujar_lista_bibliografia(p, x, y, w_total, titulo, items, color, width, height, bottom_margin=40):
    if not items:
        return y

    header_style = ParagraphStyle(
        f"fc_bib_hdr_{titulo}", fontName=FONT_BOLD, fontSize=10, leading=12,
        textColor=BLANCO, alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        f"fc_bib_body_{titulo}", fontName=FONT_NORMAL, fontSize=9, leading=11.5,
        textColor=NEGRO, alignment=TA_LEFT, leftIndent=12, firstLineIndent=-12,
    )
    header = Paragraph(_markup(titulo), header_style)
    _, h_header_text = header.wrap(w_total - 20, 10000)
    h_header = max(28, h_header_text + 14)


    filas = []
    for item in items:
        para = Paragraph(_formatear_bibliografia(item), body_style)
        _, h = para.wrap(w_total - 20, 10000)
        row_h = max(28, h + 14)
        filas.append((para, h, row_h))

    def pintar_header(y_top):
        p.setFillColor(color)
        p.setStrokeColor(color)
        p.roundRect(x, y_top - h_header, w_total, h_header, 5, fill=1, stroke=0)
        header.drawOn(p, x + 10, y_top - 7 - h_header_text)
        return y_top - h_header - 7

    min_body = filas[0][2] if filas else 28
    if y - h_header - 7 - min_body < bottom_margin:
        y = _nueva_pagina(p, height)
    y = pintar_header(y)

    idx = 0
    while idx < len(filas):
        disponible = y - bottom_margin
        usados = 0
        inicio = idx

        while idx < len(filas) and usados + filas[idx][2] <= disponible:
            usados += filas[idx][2]
            idx += 1

        if inicio == idx:
            usados = filas[idx][2]
            idx += 1

        p.setFillColor(BLANCO)
        p.setStrokeColor(color)
        p.setLineWidth(1)
        p.roundRect(x, y - usados, w_total, usados, 5, fill=1, stroke=1)

        y_fila = y
        for pos in range(inicio, idx):
            para, h, row_h = filas[pos]
            para.drawOn(p, x + 10, y_fila - 7 - h)
            y_fila -= row_h

            if pos < idx - 1:
                p.setStrokeColor(GRIS_BORDE)
                p.setLineWidth(0.6)
                p.line(x + 10, y_fila, x + w_total - 10, y_fila)

        y -= usados

        if idx < len(filas):
            y = _nueva_pagina(p, height)
            y = pintar_header(y)

    return y

def _dibujar_estrategias(p, x, y, w_total, items, color, width, height, bottom_margin=40):
    titulo = "Estrategias didácticas sugeridas"
    style_hdr = ParagraphStyle(
        "fc_est_hdr", fontName=FONT_BOLD, fontSize=11, leading=14,
        textColor=BLANCO, alignment=TA_LEFT,
    )
    style_txt = ParagraphStyle(
        "fc_est_txt", fontName=FONT_NORMAL, fontSize=9, leading=11,
        textColor=NEGRO, alignment=TA_LEFT,
    )
    hdr = Paragraph(titulo, style_hdr)
    _, h_hdr_txt = hdr.wrap(w_total - 20, 10000)
    h_hdr = max(30, h_hdr_txt + 16)
    gap_after = 8
    box_size = 11
    table_pad = 8
    cell_pad = 5

    normalizados = [
        (bool(int(item.get("seleccionada") or 0)), _texto(item.get("estrategia_didactica")))
        for item in (items or [])
    ]
    mid = (len(normalizados) + 1) // 2
    left = normalizados[:mid]
    right = normalizados[mid:]
    filas = max(len(left), len(right))

    inner_w = w_total - 2 * table_pad
    chk_w = 30
    text_w = (inner_w - (2 * chk_w)) / 2

    rows = []
    for i in range(filas):
        li = left[i] if i < len(left) else None
        ri = right[i] if i < len(right) else None
        lp = Paragraph(_markup(li[1]), style_txt) if li else Paragraph("", style_txt)
        rp = Paragraph(_markup(ri[1]), style_txt) if ri else Paragraph("", style_txt)
        lh = lp.wrap(text_w - 2 * cell_pad, 10000)[1]
        rh = rp.wrap(text_w - 2 * cell_pad, 10000)[1]
        rows.append((li, ri, lp, rp, lh, rh, max(box_size, lh, rh) + 8))

    def pintar_header(y_top):
        p.setFillColor(color)
        p.setStrokeColor(color)
        p.roundRect(x, y_top - h_hdr, w_total, h_hdr, 5, fill=1, stroke=0)
        hdr.drawOn(p, x + 10, y_top - 8 - h_hdr_txt)
        return y_top - h_hdr - gap_after

    min_needed = h_hdr + gap_after + 2 * table_pad + (rows[0][6] if rows else 24)
    if y - min_needed < bottom_margin:
        y = _nueva_pagina(p, height)
    y = pintar_header(y)

    idx = 0
    while idx < len(rows):
        available = y - bottom_margin
        used = 2 * table_pad
        start = idx
        while idx < len(rows) and used + rows[idx][6] <= available:
            used += rows[idx][6]
            idx += 1
        if start == idx and idx < len(rows):
            used += rows[idx][6]
            idx += 1

        p.setFillColor(BLANCO)
        p.setStrokeColor(color)
        p.setLineWidth(1)
        p.roundRect(x, y - used, w_total, used, 5, fill=1, stroke=1)
        x_in = x + table_pad
        y_row = y - table_pad
        for j in range(start, idx):
            li, ri, lp, rp, lh, rh, row_h = rows[j]
            for side, item, para, ph in (
                (0, li, lp, lh),
                (1, ri, rp, rh),
            ):
                if not item:
                    continue
                base_x = x_in + side * (chk_w + text_w)
                bx = base_x + (chk_w - box_size) / 2
                by = y_row - row_h / 2 - box_size / 2
                p.setFillColor(BLANCO)
                p.setStrokeColor(color)
                p.roundRect(bx, by, box_size, box_size, box_size / 4, fill=1, stroke=1)
                if item[0]:
                    p.setFillColor(NEGRO)
                    p.setFont(FONT_BOLD, 9)
                    tw = p.stringWidth("X", FONT_BOLD, 9)
                    p.drawString(bx + (box_size - tw) / 2, by + 2, "X")
                para.drawOn(p, base_x + chk_w + cell_pad, y_row - 4 - ph)
            y_row -= row_h
        y -= used

        if idx < len(rows):
            y = _nueva_pagina(p, height)
            y = pintar_header(y)
    return y


def _dibujar_parrafo_titulado(p, x, y, w_total, titulo, texto, color, width, height, bottom_margin=40):
    style_hdr = ParagraphStyle(
        f"fc_long_hdr_{titulo}", fontName=FONT_BOLD, fontSize=11, leading=14,
        textColor=BLANCO, alignment=TA_LEFT,
    )
    style_body = ParagraphStyle(
        f"fc_long_body_{titulo}", fontName=FONT_NORMAL, fontSize=10, leading=14,
        textColor=NEGRO, alignment=TA_JUSTIFY,
    )
    hdr = Paragraph(_markup(titulo), style_hdr)
    _, h_hdr_txt = hdr.wrap(w_total - 20, 10000)
    h_hdr = max(30, h_hdr_txt + 16)
    if y - h_hdr - 40 < bottom_margin:
        y = _nueva_pagina(p, height)

    p.setFillColor(color)
    p.setStrokeColor(color)
    p.roundRect(x, y - h_hdr, w_total, h_hdr, 5, fill=1, stroke=0)
    hdr.drawOn(p, x + 10, y - 8 - h_hdr_txt)
    y -= h_hdr + 8

    texto = _texto(texto).strip()
    if not texto:
        box_h = 30
        p.setStrokeColor(color)
        p.setFillColor(BLANCO)
        p.roundRect(x, y - box_h, w_total, box_h, 5, fill=1, stroke=1)
        return y - box_h

    remaining = Paragraph(_markup(texto), style_body)
    avail_w = w_total - 20
    while remaining:
        inner_h = y - bottom_margin - 20
        if inner_h < 42:
            y = _nueva_pagina(p, height)
            inner_h = y - bottom_margin - 20

        flows = remaining.split(avail_w, inner_h)
        if not flows:
            y = _nueva_pagina(p, height)
            continue
        actual = flows[0]
        restante = flows[1] if len(flows) > 1 else None
        _, h = actual.wrap(avail_w, inner_h)
        box_h = h + 20
        p.setFillColor(BLANCO)
        p.setStrokeColor(color)
        p.setLineWidth(1)
        p.roundRect(x, y - box_h, w_total, box_h, 5, fill=1, stroke=1)
        actual.drawOn(p, x + 10, y - 10 - h)
        y -= box_h
        if restante:
            y = _nueva_pagina(p, height)
            remaining = restante
        else:
            break
    return y


def generar_pdf_desde_datos(info, temas, bibliografia, estrategias):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 30
    w_total = width - 60
    bottom = 40

    color_hex = COLORES_AREA.get(int(info.get("id_area_conocimiento") or 0), "#4F617C")
    color = colors.HexColor(color_hex)

    y = _dibujar_encabezado_institucional(p, width, height)
    y = _dibujar_clave_nombre(
        p, x, y, w_total, color,
        info.get("clave_asignatura") or "",
        info.get("nombre_asignatura") or "",
    )
    y = _dibujar_datos_generales(p, x, y, w_total, color, info)
    y -= 8
    y = _dibujar_objetivo(
        p, x, y, w_total, info.get("objetivo_general") or "", color,
        width, height, bottom,
    )
    y -= 10
    if y < bottom + 90:
        y = _nueva_pagina(p, height)
    y = _dibujar_temario(p, x, y, w_total, temas, color, width, height, bottom)

    if bibliografia:
        y -= 14
        y = _dibujar_lista_bibliografia(
            p, x, y, w_total, "Bibliografía", bibliografia, color, width, height, bottom
        )

    y -= 12
    y = _dibujar_estrategias(p, x, y, w_total, estrategias, color, width, height, bottom)

    # La justificación académica siempre inicia en una página exclusiva.
    y = _nueva_pagina(p, height)
    _dibujar_parrafo_titulado(
        p, x, y, w_total, "Justificación académica",
        info.get("justificacion_academica") or "", color,
        width, height, bottom,
    )

    p.save()
    buffer.seek(0)
    return buffer


def generar_pdf_bytes(id_formacion, id_usuario):
    consultas = ConsultasPDFFormacionComplementaria()
    info = consultas.get_informacion(id_formacion, id_usuario)
    if not info:
        raise ValueError("La formación complementaria solicitada no existe o no pertenece al usuario.")
    temas = consultas.get_temario(id_formacion)
    bibliografia = consultas.get_bibliografia(id_formacion)
    estrategias = consultas.get_estrategias(id_formacion)
    return generar_pdf_desde_datos(info, temas, bibliografia, estrategias), info


def _usuario_coordinador_valido(request):
    id_usuario = request.session.get("sipefi_id_usuario")
    token = str(request.session.get("sipefi_token", "")).strip()
    usuario = str(request.session.get("sipefi_usuario", "")).strip()
    nombre_rol = str(request.session.get("sipefi_rol_activo_nombre", "")).strip().lower()

    if not id_usuario or not token or not usuario:
        return None
    if not nombre_rol.startswith("coordinador"):
        return None
    try:
        if ConsultasTomoII().validaSesionUsuario(token, 1) != "OK":
            return None
    except Exception:
        logger.exception("No fue posible validar la sesión para generar PDF de FC.")
        return None
    return int(id_usuario)


def generar_pdf(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    id_usuario = _usuario_coordinador_valido(request)
    if id_usuario is None:
        return JsonResponse({"error": "La sesión no es válida para generar el PDF."}, status=403)

    try:
        id_formacion = int(request.POST.get("idFormacion") or 0)
    except (TypeError, ValueError):
        id_formacion = 0
    if id_formacion <= 0:
        return JsonResponse({"error": "El folio de Formación complementaria no es válido."}, status=400)

    try:
        buffer, info = generar_pdf_bytes(id_formacion, id_usuario)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    except Exception:
        referencia = os.urandom(5).hex().upper()
        logger.exception("Error generando PDF de Formación complementaria. Referencia=%s", referencia)
        return JsonResponse(
            {"error": "No fue posible generar el PDF.", "referencia": referencia},
            status=500,
        )

    nombre = _normalizar_nombre_archivo(info.get("nombre_asignatura"))
    clave = _normalizar_nombre_archivo(info.get("clave_asignatura"))
    filename = f"{clave}_{nombre}.pdf" if clave else f"fc_{nombre}.pdf"

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
