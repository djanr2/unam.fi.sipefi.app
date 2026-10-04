/* global Cookies */
"use strict";

(() => {
    const FC = window.FormacionComplementaria;
    const {
        URL_BASE, estado, mostrarMensaje, construirPayload, validarMinimoBorrador,
        validarParaCompletar, ejecutar, post, escapeHtml, abrir, pintarAsignaturas,
        inicializarSelect2, numero, esHoraEntera, horasTotalesSemestre,
        TOLERANCIA_HORAS, horasTemasCapturadas, formatearHoras, limpiarTemaEditor,
        renderTemas, renderListado, mostrarEspera, mensajeError, ocultarEspera,
        renderBibliografiasNuevas, configuracionBibliografiaNueva,
        actualizarCamposBibliografiaNueva, limpiarBibliografiaNuevaEditor
    } = FC;

    const guardar = async (completar = false) => {
        if (estado.soloLectura || !estado.cargaCompleta) {
            mostrarMensaje("La solicitud no está lista para guardarse. Actualiza la pantalla.");
            return;
        }
        const payload = construirPayload();
        if (!validarMinimoBorrador(payload)) return;
        if (completar && !validarParaCompletar(payload)) return;
        await ejecutar(async () => {
            const respuesta = await post(completar ? "completar/" : "guardar/", payload);
            const resultado = respuesta.resultado;
            estado.idFormacion = Number(resultado.idFormacion);
            estado.estatus = Number(resultado.estatus);
            $("#fcBtnPdf")
                .prop("disabled", false)
                .attr("title", "Generar PDF con la \u00faltima informaci\u00f3n guardada");
            mostrarMensaje(escapeHtml(resultado.mensaje), completar ? "Solicitud completada" : "Borrador guardado");
            await recargarListado(false);
            if (completar) await abrir(estado.idFormacion, false);
            else {
                $("#fcFolio").text(`FC-${estado.idFormacion}`);
                $("#fcNombre").val(resultado.nombre || "");
                $("#fcClave").val(resultado.clave || "");
                const asigResp = await post("asignaturas/", {idFormacion: estado.idFormacion});
                estado.asignaturas = asigResp.asignaturas || [];
                pintarAsignaturas(payload.datosGenerales.idSolicitudApoyo);
                inicializarSelect2();
            }
        });
    };

    const recargarListado = async (mostrarEspera = true) => {
        const accion = async () => {
            const respuesta = await post("listar/", {});
            estado.solicitudes = respuesta.solicitudes || [];
            renderListado();
        };
        return mostrarEspera ? ejecutar(accion) : accion();
    };

    const agregarOActualizarTema = () => {
        if (estado.soloLectura) return;

        const tema = String($("#fcTemaNombre").val() || "").trim();
        const horas = numero($("#fcTemaHoras").val());

        if (!tema) {
            mostrarMensaje("Captura el nombre del tema.", "Información necesaria");
            return;
        }

        if (!esHoraEntera(horas, {permitirCero: false})) {
            $("#fcTemaHoras").addClass("is-invalid");
            mostrarMensaje(
                "Las horas prácticas del tema deben ser un número entero mayor a cero.",
                "Información necesaria"
            );
            return;
        }
        $("#fcTemaHoras").removeClass("is-invalid");

        const total = horasTotalesSemestre();
        if (total <= TOLERANCIA_HORAS) {
            mostrarMensaje(
                "Primero captura las horas totales en Datos generales.",
                "Horas del temario"
            );
            return;
        }

        const usadasSinActual = horasTemasCapturadas(estado.temaEditandoId);
        const disponibles = Math.max(0, total - usadasSinActual);

        if (horas > disponibles + TOLERANCIA_HORAS) {
            mostrarMensaje(
                `No puedes asignar ${formatearHoras(horas)} horas a este tema. ` +
                `Tienes ${formatearHoras(disponibles)} horas disponibles.`,
                "Horas del temario"
            );
            return;
        }

        if (estado.temaEditandoId !== null) {
            const actual = estado.temas.find(item => item.id === estado.temaEditandoId);
            if (actual) Object.assign(actual, {tema, horas});
        } else {
            const nuevoId = Math.max(0, ...estado.temas.map(item => item.id)) + 1;
            estado.temas.push({
                id: nuevoId,
                numTema: estado.temas.length + 1,
                tema,
                horas,
            });
        }

        limpiarTemaEditor();
        renderTemas();
    };

    const agregarOActualizarBibliografiaNueva = () => {
        if (estado.soloLectura) return;

        const {idTipo, depende, config} = configuracionBibliografiaNueva();
        const autor = String($("#fcAutorBibliografiaNueva").val() || "").trim();
        const anio = String($("#fcAnioBibliografiaNueva").val() || "").trim();
        const clasifBiblio = Number($("#fcClasificacionBibliografiaNueva").val()) === 1 ? 1 : 0;
        const titulo = String($("#fcTituloBibliografiaNueva").val() || "").trim();
        const extras = [1, 2, 3, 4].map(n => String($("#fcExtraBibliografiaNueva" + n).val() || "").trim());

        $("#fcBibliografia .is-invalid").removeClass("is-invalid");
        const invalido = (selector, mensaje) => {
            $(selector).addClass("is-invalid");
            mostrarMensaje(mensaje, "Bibliografía");
            return false;
        };

        if (!idTipo) return invalido("#fcTipoBibliografiaNueva", "Selecciona un tipo de bibliografía.");
        if (!depende && !autor) return invalido("#fcAutorBibliografiaNueva", "Captura el/los autores de la bibliografía.");
        if (!depende) {
            if (!/^\d{4}$/.test(anio) || Number(anio) < 1000 || Number(anio) > 2100) {
                return invalido("#fcAnioBibliografiaNueva", "Captura un año de publicación válido entre 1000 y 2100.");
            }
            if (!titulo) return invalido("#fcTituloBibliografiaNueva", "Captura el título de la bibliografía.");
        }
        for (let i = 0; i < 4; i += 1) {
            if (config.requeridos[i] && !extras[i]) {
                return invalido(
                    "#fcExtraBibliografiaNueva" + (i + 1),
                    `Captura el campo requerido: ${config.labels[i]}.`
                );
            }
        }

        const option = $("#fcTipoBibliografiaNueva option:selected")[0];
        const datos = {
            idTipo: Number(idTipo),
            tipo: option?.textContent?.trim() || "",
            autor: depende ? "" : autor,
            anio: depende ? "" : anio,
            clasifBiblio,
            titulo: depende ? "" : titulo,
            extra1: extras[0], extra2: extras[1], extra3: extras[2], extra4: extras[3],
        };

        if (estado.bibliografiaNuevaEditandoId !== null) {
            const actual = estado.bibliografiasNuevas.find(
                item => Number(item.idLocal) === Number(estado.bibliografiaNuevaEditandoId)
            );
            if (actual) Object.assign(actual, datos);
        } else {
            const idLocal = Math.max(0, ...estado.bibliografiasNuevas.map(item => Number(item.idLocal) || 0)) + 1;
            estado.bibliografiasNuevas.push({idLocal, ...datos});
        }

        limpiarBibliografiaNuevaEditor();
        renderBibliografiasNuevas();
        return true;
    };

    const editarBibliografiaNueva = (idLocal) => {
        if (estado.soloLectura) return;
        const item = estado.bibliografiasNuevas.find(b => Number(b.idLocal) === Number(idLocal));
        if (!item) return;
        estado.bibliografiaNuevaEditandoId = Number(idLocal);
        $("#fcTipoBibliografiaNueva").val(String(item.idTipo ?? ""));
        actualizarCamposBibliografiaNueva();
        $("#fcAutorBibliografiaNueva").val(item.autor || "");
        $("#fcAnioBibliografiaNueva").val(item.anio || "");
        $("#fcClasificacionBibliografiaNueva").val(String(Number(item.clasifBiblio) === 1 ? 1 : 0));
        $("#fcTituloBibliografiaNueva").val(item.titulo || "");
        $("#fcExtraBibliografiaNueva1").val(item.extra1 || "");
        $("#fcExtraBibliografiaNueva2").val(item.extra2 || "");
        $("#fcExtraBibliografiaNueva3").val(item.extra3 || "");
        $("#fcExtraBibliografiaNueva4").val(item.extra4 || "");
        $("#fcBtnAgregarBibliografiaNueva").html('<i class="fa-solid fa-floppy-disk me-1"></i> Guardar cambios');
        $("#fcBtnCancelarBibliografiaNueva").removeClass("d-none");
    };

    const eliminarBibliografiaNueva = (idLocal) => {
        if (estado.soloLectura) return;
        estado.bibliografiasNuevas = estado.bibliografiasNuevas.filter(
            item => Number(item.idLocal) !== Number(idLocal)
        );
        if (Number(estado.bibliografiaNuevaEditandoId) === Number(idLocal)) {
            limpiarBibliografiaNuevaEditor();
        }
        renderBibliografiasNuevas();
    };

    const descargarPdf = async (idFormacion = estado.idFormacion) => {
        const id = Number(idFormacion || 0);
        if (!Number.isInteger(id) || id <= 0) {
            mostrarMensaje("Guarda primero la solicitud para generar el PDF.", "PDF no disponible");
            return;
        }

        mostrarEspera();
        try {
            const formData = new FormData();
            formData.append("idFormacion", String(id));

            const respuesta = await fetch(`${URL_BASE}reporte/generarPdf/`, {
                method: "POST",
                headers: {"X-CSRFToken": Cookies.get("csrftoken") || ""},
                body: formData,
                cache: "no-store",
                credentials: "same-origin",
            });

            if (!respuesta.ok) {
                let detalle = {error: "No fue posible generar el PDF."};
                try {
                    detalle = await respuesta.json();
                } catch (_error) {}
                throw detalle;
            }

            const blob = await respuesta.blob();
            const disposition = respuesta.headers.get("Content-Disposition") || "";
            const match = disposition.match(/filename="?([^";]+)"?/i);
            const nombreArchivo = match?.[1] || `programa_estudios_FC_${id}.pdf`;
            const url = URL.createObjectURL(blob);
            const enlace = document.createElement("a");
            enlace.href = url;
            enlace.download = nombreArchivo;
            document.body.appendChild(enlace);
            enlace.click();
            enlace.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error) {
            mensajeError(error);
        } finally {
            ocultarEspera();
        }
    };

    Object.assign(FC, {
        guardar,
        recargarListado,
        agregarOActualizarTema,
        agregarOActualizarBibliografiaNueva,
        editarBibliografiaNueva,
        eliminarBibliografiaNueva,
        descargarPdf,
    });
})();
