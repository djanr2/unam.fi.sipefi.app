/* global bootstrap, Cookies */
"use strict";

window.FormacionComplementaria = window.FormacionComplementaria || {};

(() => {
    const FC = window.FormacionComplementaria;
    const URL_BASE = "/SIPEFI/formacion-complementaria/";
    const estado = {
        catalogos: {},
        asignaturas: [],
        solicitudes: [],
        idFormacion: null,
        estatus: 1,
        soloLectura: false,
        cargaCompleta: false,
        temas: [],
        bibliografias: [],
        temaEditandoId: null,
        tablas: {},
    };

    const escapeHtml = (valor) => $("<div>").text(valor ?? "").html();
    const normalizarNumero = (valor) => valor === null || valor === undefined || valor === "" ? "" : String(valor);

    const normalizarHoraBD = (valor) => {
        if (valor === null || valor === undefined || valor === "") return "";

        const texto = String(valor).trim();
        if (texto === "") return "";

        const numeroValor = Number(texto);
        if (!Number.isFinite(numeroValor)) return texto;

        return String(numeroValor);
    };

    const numero = (valor) => {
        if (valor === null || valor === undefined || valor === "") return null;
        const parsed = Number(valor);
        return Number.isFinite(parsed) ? parsed : null;
    };

    const leerHoraEntera = (selector) => {
        const valor = String($(selector).val() ?? "").trim();
        if (valor === "") {
            return {vacia: true, valida: true, valor: null};
        }
        if (!/^\d+$/.test(valor)) {
            return {vacia: false, valida: false, valor: null};
        }
        const entero = Number(valor);
        return {
            vacia: false,
            valida: Number.isSafeInteger(entero) && entero >= 0,
            valor: entero,
        };
    };

    const esHoraEntera = (valor, {permitirCero = true} = {}) => {
        if (valor === null || valor === undefined || valor === "") return false;
        const numeroValor = Number(valor);
        if (!Number.isSafeInteger(numeroValor)) return false;
        return permitirCero ? numeroValor >= 0 : numeroValor > 0;
    };

    const marcarCampoHoraEntera = (selector, {permitirVacio = true, permitirCero = true} = {}) => {
        const info = leerHoraEntera(selector);
        const valida = (permitirVacio && info.vacia) ||
            (info.valida && (permitirCero || info.valor > 0));
        $(selector).toggleClass("is-invalid", !valida);
        return valida;
    };

    const elementoModalEspera = document.getElementById("fcModalEspera");
    const modalMensaje = () => bootstrap.Modal.getOrCreateInstance(document.getElementById("fcModalMensaje"));
    const modalConfirmar = () => bootstrap.Modal.getOrCreateInstance(document.getElementById("fcModalConfirmar"));
    const modalEspera = () => bootstrap.Modal.getOrCreateInstance(
        elementoModalEspera,
        {backdrop: "static", keyboard: false}
    );

    let operacionesEnEspera = 0;

    const mostrarEspera = () => {
        operacionesEnEspera += 1;
        if (!elementoModalEspera.classList.contains("show")) {
            modalEspera().show();
        }
    };

    const ocultarEspera = () => {
        operacionesEnEspera = Math.max(0, operacionesEnEspera - 1);
        if (operacionesEnEspera === 0 && elementoModalEspera.classList.contains("show")) {
            modalEspera().hide();
        }
    };

    const mostrarMensaje = (mensaje, titulo = "SIPEFI") => {
        const abrirMensaje = () => {
            $("#fcModalMensajeTitulo").text(titulo);
            $("#fcModalMensajeTexto").html(mensaje);
            modalMensaje().show();
        };

        if (elementoModalEspera.classList.contains("show")) {
            elementoModalEspera.addEventListener("hidden.bs.modal", abrirMensaje, {once: true});
        } else {
            abrirMensaje();
        }
    };

    const mensajeError = (respuesta) => {
        let texto = respuesta?.error || "No fue posible completar la operación.";
        if (respuesta?.referencia) {
            texto += `<br><small>Referencia de soporte: <strong>${escapeHtml(respuesta.referencia)}</strong></small>`;
        }
        mostrarMensaje(texto, "No fue posible continuar");
    };

    const post = (ruta, datos = {}) => new Promise((resolve, reject) => {
        $.ajax({
            url: URL_BASE + ruta,
            method: "POST",
            dataType: "json",
            cache: false,
            headers: {"X-CSRFToken": Cookies.get("csrftoken") || ""},
            data: {obj: JSON.stringify(datos)},
            success: resolve,
            error: (xhr) => reject(xhr.responseJSON || {estatus: xhr.status, error: xhr.statusText}),
        });
    });

    const ejecutar = async (funcion, {espera = true} = {}) => {
        try {
            if (espera) mostrarEspera();
            return await funcion();
        } catch (error) {
            mensajeError(error);
            throw error;
        } finally {
            if (espera) ocultarEspera();
        }
    };

    const inicializarReloj = () => {
        const actualizar = () => {
            const ahora = new Date();
            $("#hora").text([
                ahora.getHours(), ahora.getMinutes(), ahora.getSeconds()
            ].map(v => String(v).padStart(2, "0")).join(":"));
        };
        actualizar();
        window.setInterval(actualizar, 1000);
    };

    Object.assign(FC, {
        URL_BASE,
        estado,
        escapeHtml,
        normalizarNumero,
        normalizarHoraBD,
        numero,
        leerHoraEntera,
        esHoraEntera,
        marcarCampoHoraEntera,
        modalConfirmar,
        mostrarEspera,
        ocultarEspera,
        mostrarMensaje,
        mensajeError,
        post,
        ejecutar,
        inicializarReloj,
    });
})();
