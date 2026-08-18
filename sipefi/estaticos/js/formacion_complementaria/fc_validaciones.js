/* global bootstrap */
"use strict";

(() => {
    const FC = window.FormacionComplementaria;
    const {
        estado, mostrarMensaje, leerHoraEntera, marcarCampoHoraEntera,
        esHoraEntera, escapeHtml, actualizarHorasRestantes,
        TOLERANCIA_HORAS, formatearHoras
    } = FC;

    const validarMinimoBorrador = (payload) => {
        const datos = payload.datosGenerales;

        if (!datos.idSolicitudApoyo || !datos.idSubprograma || !datos.idAreaConocimiento || !datos.idModalidad) {
            mostrarMensaje(
                "Para crear el borrador debes seleccionar la asignatura de apoyo, el subprograma, el área del conocimiento y la modalidad.",
                "Información necesaria"
            );
            return false;
        }

        const pra = leerHoraEntera("#fcHorasPraSemana");
        if (!pra.valida) {
            marcarCampoHoraEntera("#fcHorasPraSemana", {permitirVacio: true, permitirCero: false});
            mostrarMensaje(
                "Las horas prácticas por semana deben capturarse únicamente con números enteros mayores a cero.",
                "Horas no válidas"
            );
            return false;
        }

        const temaNoEntero = estado.temas.find(tema => !esHoraEntera(tema.horas, {permitirCero: false}));
        if (temaNoEntero) {
            mostrarMensaje(
                `El tema "${escapeHtml(temaNoEntero.tema || "")}" tiene una cantidad de horas no válida. ` +
                "Las horas de cada tema deben ser números enteros mayores a cero.",
                "Horas no válidas"
            );
            return false;
        }

        return true;
    };

    const limpiarValidacionCompletar = () => {
        $("#fcSeccionFormulario .is-invalid").removeClass("is-invalid");
        $("#fcSeccionFormulario .fc-validation-invalid").removeClass("fc-validation-invalid");
        $("#fcEstrategiasSelect")
            .next(".select2")
            .find(".select2-selection")
            .removeClass("is-invalid");
    };

    const activarPestana = (objetivo) => {
        const boton = document.querySelector(`#fcTabs button[data-bs-target="${objetivo}"]`);
        if (boton) bootstrap.Tab.getOrCreateInstance(boton).show();
    };

    const validarParaCompletar = (payload) => {
        limpiarValidacionCompletar();

        const errores = [];
        let primeraPestana = null;
        let primerSelector = null;

        const registrar = (mensaje, selector, pestana) => {
            errores.push(mensaje);
            if (!primeraPestana) primeraPestana = pestana;
            if (!primerSelector && selector) primerSelector = selector;

            if (selector) {
                const $elemento = $(selector);
                if ($elemento.length) {
                    $elemento.addClass("is-invalid");
                    if ($elemento.hasClass("select2-hidden-accessible")) {
                        $elemento.next(".select2").find(".select2-selection").addClass("is-invalid");
                    }
                }
            }
        };

        const datos = payload.datosGenerales || {};

        // 1. Datos generales.
        if (!datos.idSolicitudApoyo) registrar("Selecciona la asignatura a la que apoya.", "#fcAsignaturaApoyo", "#fcDatos");
        if (!datos.idSubprograma) registrar("Selecciona el subprograma.", "#fcSubprograma", "#fcDatos");
        if (!datos.idAreaConocimiento) registrar("Selecciona el área del conocimiento.", "#fcAreaConocimiento", "#fcDatos");
        if (!datos.idModalidad) registrar("Selecciona la modalidad.", "#fcModalidad", "#fcDatos");
        if (!datos.semestre) registrar("Selecciona el semestre.", "#fcSemestre", "#fcDatos");

        const praCapturado = leerHoraEntera("#fcHorasPraSemana");
        if (praCapturado.vacia) {
            registrar(
                "Captura las horas prácticas por semana.",
                "#fcHorasPraSemana",
                "#fcDatos"
            );
        } else if (!praCapturado.valida || (praCapturado.valor ?? 0) <= 0) {
            registrar(
                "Las horas prácticas por semana deben ser un número entero mayor a cero.",
                "#fcHorasPraSemana",
                "#fcDatos"
            );
        }

        if (!String(datos.objetivoGeneral || "").trim()) {
            registrar("Captura el objetivo general.", "#fcObjetivo", "#fcDatos");
        }

        if (!String($("#fcNombre").val() || "").trim()) {
            registrar(
                "No fue posible generar el nombre de la formación complementaria.",
                "#fcNombre",
                "#fcDatos"
            );
        }

        if (!/^\d{8}$/.test(String($("#fcClave").val() || "").trim())) {
            registrar(
                "No fue posible generar una clave válida para la formación complementaria.",
                "#fcClave",
                "#fcDatos"
            );
        }

        // 2. Temario.
        if (estado.temaEditandoId !== null) {
            registrar(
                "Guarda primero la edición del tema que está abierta.",
                "#fcTemaNombre",
                "#fcTemario"
            );
        }

        if (!payload.temas.length) {
            registrar(
                "Agrega al menos un tema al temario.",
                "#fcTablaTemas",
                "#fcTemario"
            );
        } else {
            const temaIncompleto = payload.temas.some(tema =>
                !String(tema.tema || "").trim() ||
                !esHoraEntera(tema.horas, {permitirCero: false})
            );

            if (temaIncompleto) {
                registrar(
                    "Todos los temas deben tener nombre y horas prácticas enteras mayores a cero.",
                    "#fcTablaTemas",
                    "#fcTemario"
                );
            }
        }

        const {total, restantes} = actualizarHorasRestantes();
        if (total <= TOLERANCIA_HORAS) {
            registrar(
                "Define las horas prácticas del semestre desde Datos generales antes de completar el temario.",
                "#fcBoxHorasRestantes",
                "#fcTemario"
            );
        } else if (Math.abs(restantes) > TOLERANCIA_HORAS) {
            const detalle = restantes > 0
                ? `Faltan ${formatearHoras(restantes)} horas prácticas por asignar.`
                : `El temario excede el total por ${formatearHoras(Math.abs(restantes))} horas prácticas.`;

            registrar(
                `Debes utilizar exactamente las ${formatearHoras(total)} horas prácticas del semestre en el temario. ${detalle}`,
                "#fcBoxHorasRestantes",
                "#fcTemario"
            );
            $("#fcBoxHorasRestantes").addClass("fc-validation-invalid");
        }

        // 3. Bibliografía.
        if (!payload.bibliografias.length) {
            registrar(
                "Selecciona al menos una referencia bibliográfica.",
                "#fcTablaBibliografia",
                "#fcBibliografia"
            );
        }

        // 4. Estrategias didácticas.
        if (!payload.estrategias.length) {
            registrar(
                "Selecciona al menos una estrategia didáctica sugerida.",
                "#fcEstrategiasSelect",
                "#fcEstrategias"
            );
        }

        // 5. Justificación académica.
        if (!String(datos.justificacionAcademica || "").trim()) {
            registrar(
                "Captura la justificación académica.",
                "#fcJustificacion",
                "#fcJustificacionTab"
            );
        }

        if (!errores.length) return true;
        if (primeraPestana) activarPestana(primeraPestana);

        const cuerpo = `
            <p class="mb-2">Corrige lo siguiente antes de marcar la solicitud como completada:</p>
            <ul class="mb-0">
                ${errores.map(error => `<li>${escapeHtml(error)}</li>`).join("")}
            </ul>
        `;

        mostrarMensaje(cuerpo, "Solicitud incompleta");

        if (primerSelector) {
            window.setTimeout(() => {
                const $primero = $(primerSelector);
                if (!$primero.length) return;
                try {
                    $("html, body").animate({
                        scrollTop: Math.max(0, $primero.offset().top - 140)
                    }, 300);
                } catch (_error) {}
            }, 250);
        }

        return false;
    };

    Object.assign(FC, {
        validarMinimoBorrador,
        limpiarValidacionCompletar,
        activarPestana,
        validarParaCompletar,
    });
})();
