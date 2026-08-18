/* global bootstrap, Cookies */
"use strict";

(() => {
    const FC = window.FormacionComplementaria;
    const {
        estado, nueva, abrir, mostrarListado, recargarListado, guardar, descargarPdf,
        construirPayload, validarMinimoBorrador, validarParaCompletar, modalConfirmar,
        actualizarNombreClave, mostrarEspera, cargarBibliografias, mensajeError,
        ocultarEspera, recalcular, marcarCampoHoraEntera, actualizarHorasRestantes,
        agregarOActualizarTema, limpiarTemaEditor, renderTemas, renderBibliografias,
        renderListado, inicializarReloj, inicializarTablas, post, ejecutar, pintarCatalogos
    } = FC;

    const registrarEventos = () => {
        $("#fcBtnNuevo").on("click", nueva);
        $("#fcBtnRegresar").on("click", mostrarListado);
        $("#fcBtnActualizar").on("click", () => recargarListado(true));
        $("#fcBtnGuardar").on("click", () => guardar(false));
        $("#fcBtnPdf").on("click", () => descargarPdf());
        $("#fcBtnCompletar").on("click", () => {
            const payload = construirPayload();
            if (!validarMinimoBorrador(payload)) return;
            if (!validarParaCompletar(payload)) return;
            modalConfirmar().show();
        });
        $("#fcBtnConfirmarCompletar").on("click", () => {
            modalConfirmar().hide();
            guardar(true);
        });
        $("#fcAsignaturaApoyo").on("change", async function () {
            actualizarNombreClave();
            if (!estado.cargaCompleta || estado.soloLectura) return;
            try {
                mostrarEspera();
                await cargarBibliografias($(this).val(), false);
            } catch (error) {
                mensajeError(error);
            } finally {
                ocultarEspera();
            }
        });
        $("#fcSubprograma, #fcModalidad").on("change", actualizarNombreClave);
        const camposHorasEnteras = "#fcHorasPraSemana, #fcTemaHoras";

        $(camposHorasEnteras).on("keydown", event => {
            if ([".", ",", "e", "E", "+", "-"].includes(event.key)) {
                event.preventDefault();
            }
        });

        $("#fcHorasPraSemana").on("input", recalcular);

        $("#fcTemaHoras").on("input", () => {
            marcarCampoHoraEntera("#fcTemaHoras", {permitirVacio: true, permitirCero: false});
            actualizarHorasRestantes();
        });

        $("#fcBtnAgregarTema").on("click", agregarOActualizarTema);

        $("#fcTablaListado tbody").on("click", ".fc-abrir", function () { abrir(Number($(this).data("id"))); });
        $("#fcTablaListado tbody").on("click", ".fc-pdf", function () { descargarPdf(Number($(this).data("id"))); });
        $("#fcTablaTemas tbody").on("click", ".fc-editar-tema", function () {
            const id = Number($(this).data("id"));
            const tema = estado.temas.find(item => item.id === id);
            if (!tema) return;
            estado.temaEditandoId = id;
            $("#fcTemaNombre").val(tema.tema);
            $("#fcTemaHoras").val(tema.horas);
            $("#fcBtnAgregarTema").html('<i class="fa-solid fa-floppy-disk"></i>').attr("title", "Guardar cambios del tema");
            actualizarHorasRestantes();
        });
        $("#fcTablaTemas tbody").on("click", ".fc-eliminar-tema", function () {
            const id = Number($(this).data("id"));
            estado.temas = estado.temas.filter(item => item.id !== id);
            limpiarTemaEditor();
            renderTemas();
        });
        $("#fcTablaBibliografia tbody").on("change", ".fc-biblio-check", function () {
            const indice = Number($(this).data("index"));
            if (estado.bibliografias[indice]) estado.bibliografias[indice].seleccionada = this.checked;
        });
        $("#fcBtnSeleccionarTodas").on("click", () => {
            estado.bibliografias.forEach(item => { item.seleccionada = true; });
            renderBibliografias();
        });
        $("#fcBtnLimpiarBibliografia").on("click", () => {
            estado.bibliografias.forEach(item => { item.seleccionada = false; });
            renderBibliografias();
        });
        $("#fcJustificacion").on("input", function () {
            $("#fcJustificacionContador").text(String($(this).val() || "").length);
        });
    };

    const inicio = async () => {
        inicializarReloj();
        inicializarTablas();
        registrarEventos();
        $(document).ajaxComplete((_event, xhr) => {
            if (xhr.getResponseHeader("AccesoSistema") === "NOK") {
                window.location.href = "/SIPEFI/login/";
            }
        });
        $.ajaxSetup({
            beforeSend: (xhr, settings) => {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken") || "");
                }
            },
        });
        await ejecutar(async () => {
            const respuesta = await post("datos-iniciales/", {});
            estado.catalogos = respuesta.datos.catalogos || {};
            estado.asignaturas = respuesta.datos.asignaturas || [];
            estado.solicitudes = respuesta.datos.solicitudes || [];
            pintarCatalogos();
            renderListado();
            renderTemas();
            renderBibliografias();
        });
    };

    Object.assign(FC, {registrarEventos, inicio});
})();

$(document).ready(() => window.FormacionComplementaria.inicio());
