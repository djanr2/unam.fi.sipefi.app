"use strict";

(() => {
    const FC = window.FormacionComplementaria;
    const {
        estado, post, renderBibliografias, ejecutar, limpiarFormulario,
        pintarAsignaturas, inicializarSelect2, mostrarFormulario,
        normalizarNumero, normalizarHoraBD, renderTemas, setSoloLectura, numero
    } = FC;

    const cargarBibliografias = async (idSolicitud, conservar = false) => {
        if (!idSolicitud) {
            estado.bibliografias = [];
            renderBibliografias();
            return;
        }
        const respuesta = await post("bibliografias/", {
            idSolicitudApoyo: Number(idSolicitud),
            idFormacion: conservar ? estado.idFormacion : null,
        });
        estado.bibliografias = (respuesta.bibliografias || []).map(item => ({...item, seleccionada: Boolean(item.seleccionada)}));
        renderBibliografias();
    };

    const nueva = async () => {
        await ejecutar(async () => {
            const respuesta = await post("asignaturas/", {});
            estado.asignaturas = respuesta.asignaturas || [];
            limpiarFormulario();
            pintarAsignaturas();
            inicializarSelect2();
            estado.cargaCompleta = true;
            mostrarFormulario();
        });
    };

    const abrir = async (idFormacion, usarEspera = true) => {
        const accion = async () => {
            estado.cargaCompleta = false;
            const [asignaturasResp, detalleResp] = await Promise.all([
                post("asignaturas/", {idFormacion}),
                post("detalle/", {idFormacion}),
            ]);
            const detalle = detalleResp.detalle;
            estado.asignaturas = asignaturasResp.asignaturas || [];
            estado.idFormacion = Number(detalle.id_formacion);
            estado.estatus = Number(detalle.id_estatus_fc);
            pintarAsignaturas(detalle.id_solicitud_apoyo);
            inicializarSelect2();

            $("#fcFolio").text(`FC-${estado.idFormacion}`);
            $("#fcEstatusBadge")
                .attr("class", estado.estatus === 2 ? "badge bg-success" : "badge bg-secondary")
                .text(estado.estatus === 2 ? "Completada" : "Borrador");
            $("#fcAsignaturaApoyo").val(String(detalle.id_solicitud_apoyo)).trigger("change.select2");
            $("#fcSubprograma").val(normalizarNumero(detalle.id_subprograma)).trigger("change.select2");
            $("#fcAreaConocimiento").val(normalizarNumero(detalle.id_area_conocimiento)).trigger("change.select2");
            $("#fcModalidad").val(normalizarNumero(detalle.id_modalidad_fc)).trigger("change.select2");
            $("#fcSemestre").val(normalizarNumero(detalle.semestre));
            $("#fcTipo").val("Práctico");
            $("#fcCaracter").val("Optativo");
            $("#fcNombre").val(detalle.nombre_asignatura || "");
            $("#fcClave").val(detalle.clave_asignatura || "");
            $("#fcHorasPraSemana").val(normalizarHoraBD(detalle.horas_pract_semana));
            $("#fcHorasPraSemestre").val(normalizarHoraBD(detalle.horas_pract_semestre));
            $("#fcObjetivo").val(detalle.objetivo_general || "");
            $("#fcJustificacion").val(detalle.justificacion_academica || "");
            $("#fcJustificacionContador").text(String($("#fcJustificacion").val() || "").length);
            $("#fcEstrategiasSelect").val((detalle.estrategias || []).map(String)).trigger("change");

            estado.temas = (detalle.temas || []).map((tema, indice) => ({
                id: indice + 1,
                numTema: Number(tema.num_tema) || indice + 1,
                tema: tema.tema || "",
                horas: normalizarHoraBD(tema.horas_tema),
            }));
            estado.bibliografias = (detalle.bibliografias_disponibles || []).map(item => ({...item, seleccionada: Boolean(item.seleccionada)}));
            renderTemas();
            renderBibliografias();
            setSoloLectura(Boolean(detalle.solo_lectura));
            estado.cargaCompleta = true;
            mostrarFormulario();
        };
        return usarEspera ? ejecutar(accion) : accion();
    };

    const construirPayload = () => ({
        idFormacion: estado.idFormacion,
        cargaCompleta: estado.cargaCompleta,
        datosGenerales: {
            idSolicitudApoyo: numero($("#fcAsignaturaApoyo").val()),
            idSubprograma: numero($("#fcSubprograma").val()),
            idAreaConocimiento: numero($("#fcAreaConocimiento").val()),
            idModalidad: numero($("#fcModalidad").val()),
            semestre: numero($("#fcSemestre").val()),
            horasPracticasSemana: numero($("#fcHorasPraSemana").val()),
            objetivoGeneral: $("#fcObjetivo").val(),
            justificacionAcademica: $("#fcJustificacion").val(),
        },
        temas: estado.temas.map(tema => ({
            numTema: tema.numTema,
            tema: tema.tema,
            horas: numero(tema.horas),
        })),
        bibliografias: estado.bibliografias.filter(item => item.seleccionada).map(item => ({
            idSolicitudOrigen: Number(item.id_solicitud_origen),
            idEstatusOrigen: Number(item.id_estatus_origen),
            idBibliografiaOrigen: Number(item.id_bibliografia_origen),
        })),
        estrategias: ($("#fcEstrategiasSelect").val() || []).map(Number),
        comentario: "",
    });

    Object.assign(FC, {
        cargarBibliografias,
        nueva,
        abrir,
        construirPayload,
    });
})();
