/* global bootstrap, rutaIdiomaDT */
"use strict";

(() => {
    const FC = window.FormacionComplementaria;
    const {
        estado, escapeHtml, numero, leerHoraEntera, marcarCampoHoraEntera
    } = FC;

    const opcionesDataTable = (columnas) => ({
        destroy: false,
        responsive: false,
        autoWidth: false,
        ordering: false,
        pageLength: 5,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"]],
        language: {url: rutaIdiomaDT},
        columns: Array.from({length: columnas}, () => ({defaultContent: ""})),
    });

    const inicializarTablas = () => {
        if (!$.fn.DataTable.isDataTable("#fcTablaListado")) {
            estado.tablas.listado = $("#fcTablaListado").DataTable({
                ...opcionesDataTable(10),
                pageLength: 10,
                columnDefs: [
                    {targets: [0, 3, 6, 7, 8, 9], className: "text-center"},
                    {targets: 9, searchable: false},
                ],
            });
        } else estado.tablas.listado = $("#fcTablaListado").DataTable();

        if (!$.fn.DataTable.isDataTable("#fcTablaTemas")) {
            estado.tablas.temas = $("#fcTablaTemas").DataTable({
                ...opcionesDataTable(4),
                columnDefs: [
                    {targets: [0, 2, 3], className: "text-center"},
                    {targets: 3, searchable: false},
                ],
            });
        } else estado.tablas.temas = $("#fcTablaTemas").DataTable();

        if (!$.fn.DataTable.isDataTable("#fcTablaBibliografia")) {
            estado.tablas.bibliografias = $("#fcTablaBibliografia").DataTable({
                ...opcionesDataTable(10),
                columnDefs: [
                    {targets: [0, 1, 3, 4], className: "text-center"},
                    {targets: 0, searchable: false},
                ],
            });
        } else estado.tablas.bibliografias = $("#fcTablaBibliografia").DataTable();
    };

    const llenarSelect = ($select, items, textoInicial, atributos = {}) => {
        $select.empty().append(new Option(textoInicial, ""));
        items.forEach(item => {
            const option = new Option(item.nombre ?? "", item.id);
            Object.entries(atributos).forEach(([dataName, itemKey]) => {
                option.dataset[dataName] = item[itemKey] ?? "";
            });
            $select.append(option);
        });
    };

    const inicializarSelect2 = () => {
        const simples = ["#fcAsignaturaApoyo", "#fcSubprograma", "#fcAreaConocimiento", "#fcModalidad"];
        simples.forEach(selector => {
            const $elemento = $(selector);
            if ($elemento.hasClass("select2-hidden-accessible")) $elemento.select2("destroy");
            $elemento.select2({width: "100%", allowClear: true, placeholder: "Selecciona una opción"});
        });
        const $estrategias = $("#fcEstrategiasSelect");
        if ($estrategias.hasClass("select2-hidden-accessible")) {
            $estrategias.select2("destroy");
        }
        $estrategias.select2({
            placeholder: "Selecciona una o más estrategias",
            width: "100%",
            closeOnSelect: false
        });
    };

    const pintarCatalogos = () => {
        const cat = estado.catalogos;
        llenarSelect($("#fcSubprograma"), cat.subprogramas || [], "Selecciona", {code: "clave"});
        llenarSelect($("#fcAreaConocimiento"), cat.areas_conocimiento || [], "Selecciona");
        llenarSelect($("#fcModalidad"), cat.modalidades || [], "Selecciona", {prefix: "prefijo"});

        const $estrategias = $("#fcEstrategiasSelect").empty();
        (cat.estrategias || []).forEach(item => $estrategias.append(new Option(item.nombre, item.id)));

        pintarAsignaturas();
        inicializarSelect2();
    };

    const pintarAsignaturas = (valorSeleccionado = null) => {
        const $select = $("#fcAsignaturaApoyo");
        if ($select.hasClass("select2-hidden-accessible")) $select.select2("destroy");
        $select.empty().append(new Option("Selecciona una asignatura", ""));
        estado.asignaturas.forEach(item => {
            const texto = `${item.asignatura} · ${item.clave_asignatura} · ${item.desc_estatus}`;
            const option = new Option(texto, item.id_solicitud);
            option.dataset.name = item.asignatura ?? "";
            option.dataset.key = item.clave_asignatura ?? "";
            option.dataset.status = item.id_estatus_solicitud ?? "";
            $select.append(option);
        });
        if (valorSeleccionado !== null) $select.val(String(valorSeleccionado));
        if ($select.hasClass("select2-hidden-accessible")) $select.trigger("change.select2");
    };

    const renderListado = () => {
        const filas = estado.solicitudes.map(item => {
            const completada = Number(item.id_estatus_fc) === 2;
            const badge = completada
                ? '<span class="badge bg-success">Completada</span>'
                : '<span class="badge bg-secondary">Borrador</span>';
            const icono = completada ? "fa-eye" : "fa-pen-to-square";
            const titulo = completada ? "Consultar" : "Editar";
            return [
                `FC-${escapeHtml(item.id_formacion)}`,
                escapeHtml(item.asignatura_apoyo),
                escapeHtml(item.nombre_asignatura),
                escapeHtml(item.clave_asignatura),
                escapeHtml(item.subprograma),
                escapeHtml(item.modalidad),
                escapeHtml(item.semestre ?? ""),
                badge,
                escapeHtml(item.fecha_modificacion),
                `<div class="fc-actions">
                    <button type="button" class="btn btn-outline-primary btn-sm fc-abrir" data-id="${Number(item.id_formacion)}" title="${titulo}"><i class="fa-solid ${icono}"></i></button>
                    <button type="button" class="btn btn-outline-danger btn-sm fc-pdf" data-id="${Number(item.id_formacion)}" title="Descargar programa de estudios en PDF"><i class="fa-solid fa-file-pdf"></i></button>
                 </div>`,
            ];
        });
        estado.tablas.listado.clear().rows.add(filas).draw(false);
    };

    const TOLERANCIA_HORAS = 0.0001;

    const formatearHoras = (valor) => {
        const numeroValor = Number(valor);
        if (!Number.isFinite(numeroValor)) return "0";
        return Number.isInteger(numeroValor)
            ? String(numeroValor)
            : String(Number(numeroValor.toFixed(2)));
    };

    const horasTotalesSemestre = () =>
        numero($("#fcHorasPraSemestre").val()) ?? 0;

    const horasTemasCapturadas = (excluirId = null) =>
        estado.temas.reduce((total, tema) => {
            if (excluirId !== null && Number(tema.id) === Number(excluirId)) {
                return total;
            }
            return total + (numero(tema.horas) ?? 0);
        }, 0);

    const actualizarHorasRestantes = () => {
        const total = horasTotalesSemestre();
        const usadas = horasTemasCapturadas();
        const restantes = total - usadas;

        $("#fcHorasTotales").text(formatearHoras(total));
        $("#fcHorasRestantes").text(formatearHoras(restantes));

        const $box = $("#fcBoxHorasRestantes");
        $box.removeClass("bg-secondary bg-warning bg-success bg-danger text-dark");

        if (total <= TOLERANCIA_HORAS) {
            $box
                .addClass("bg-secondary")
                .attr("title", "Define primero las horas prácticas por semana en Datos generales.");
        } else if (restantes < -TOLERANCIA_HORAS) {
            $box
                .addClass("bg-danger")
                .attr("title", `El temario excede por ${formatearHoras(Math.abs(restantes))} horas prácticas el total del semestre.`);
        } else if (Math.abs(restantes) <= TOLERANCIA_HORAS) {
            $box
                .addClass("bg-success")
                .attr("title", "Todas las horas prácticas del semestre ya fueron asignadas al temario.");
        } else {
            $box
                .addClass("bg-warning text-dark")
                .attr("title", `Faltan ${formatearHoras(restantes)} horas prácticas por asignar al temario.`);
        }

        const editando = estado.temaEditandoId !== null;
        const sinHorasDisponibles = total <= TOLERANCIA_HORAS ||
            (!editando && restantes <= TOLERANCIA_HORAS);

        $("#fcBtnAgregarTema").prop("disabled", estado.soloLectura || sinHorasDisponibles);
        $("#fcTemaNombre, #fcTemaHoras")
            .prop("disabled", estado.soloLectura || total <= TOLERANCIA_HORAS);

        const horasEntrada = numero($("#fcTemaHoras").val()) ?? 0;
        const usadasSinActual = horasTemasCapturadas(estado.temaEditandoId);
        const disponiblesParaTema = Math.max(0, total - usadasSinActual);

        $("#fcTemaHoras").toggleClass(
            "is-invalid",
            total > TOLERANCIA_HORAS &&
            horasEntrada > disponiblesParaTema + TOLERANCIA_HORAS
        );

        return {total, usadas, restantes};
    };

    const renderTemas = () => {
        estado.temas.sort((a, b) => Number(a.numTema) - Number(b.numTema));
        estado.temas.forEach((tema, indice) => { tema.numTema = indice + 1; });
        const filas = estado.temas.map(tema => [
            tema.numTema,
            escapeHtml(tema.tema),
            escapeHtml(tema.horas),
            estado.soloLectura ? "" : `<div class="fc-actions">
                <button class="btn btn-outline-primary btn-sm fc-editar-tema" data-id="${tema.id}" type="button" title="Editar"><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-outline-danger btn-sm fc-eliminar-tema" data-id="${tema.id}" type="button" title="Eliminar"><i class="fa-solid fa-trash"></i></button>
            </div>`,
        ]);
        estado.tablas.temas.clear().rows.add(filas).draw(false);
        const total = estado.temas.reduce((sum, tema) => sum + (Number(tema.horas) || 0), 0);
        $("#fcHorasTemarioResumen").text(`${formatearHoras(total)} horas prácticas registradas`);
        actualizarHorasRestantes();
    };

    const renderBibliografias = () => {
        const textoBibliografia = (valor) => {
            const texto = String(valor ?? "").trim();
            return texto ? escapeHtml(texto) : '<span class="text-muted">—</span>';
        };

        const filas = estado.bibliografias.map((item, indice) => {
            const seleccionada = item.seleccionada ? "checked" : "";
            const disabled = estado.soloLectura ? "disabled" : "";
            const clasificacion = Number(item.es_complementaria) === 1
                ? "Complementaria"
                : "Básica";

            return [
                `<input type="checkbox"
                        class="form-check-input fc-checkbox fc-biblio-check"
                        data-index="${indice}"
                        ${seleccionada}
                        ${disabled}>`,
                textoBibliografia(item.tipo_bibliografia || item.id_tipo_bibliografia),
                textoBibliografia(item.autor),
                textoBibliografia(item.publicacion),
                clasificacion,
                textoBibliografia(item.titulo),
                textoBibliografia(item.campo_1),
                textoBibliografia(item.campo_2),
                textoBibliografia(item.campo_3),
                textoBibliografia(item.campo_4),
            ];
        });

        estado.tablas.bibliografias.clear().rows.add(filas).draw(false);
        $("#fcSinBibliografia").toggleClass("d-none", estado.bibliografias.length > 0);
    };

    const limpiarTemaEditor = () => {
        estado.temaEditandoId = null;
        $("#fcTemaNombre, #fcTemaHoras").val("");
        $("#fcBtnAgregarTema").html('<i class="fa-solid fa-plus"></i>').attr("title", "Agregar tema");
    };

    const recalcular = () => {
        const pra = leerHoraEntera("#fcHorasPraSemana");
        marcarCampoHoraEntera("#fcHorasPraSemana", {permitirVacio: true, permitirCero: false});

        if (!pra.valida) {
            $("#fcHorasPraSemestre").val("");
            actualizarHorasRestantes();
            return;
        }

        if (pra.vacia) {
            $("#fcHorasPraSemestre").val("");
        } else {
            $("#fcHorasPraSemestre").val((pra.valor ?? 0) * 16);
        }

        actualizarHorasRestantes();
    };

    const actualizarNombreClave = () => {
        const support = $("#fcAsignaturaApoyo option:selected")[0];
        const modality = $("#fcModalidad option:selected")[0];
        const subprogram = $("#fcSubprograma option:selected")[0];
        const supportName = support?.dataset?.name || "";
        const supportKey = support?.dataset?.key || "";
        const prefix = modality?.dataset?.prefix || "";
        const subCode = subprogram?.dataset?.code || "";
        $("#fcNombre").val(prefix && supportName ? `${prefix} ${supportName}. FORMACIÓN COMPLEMENTARIA`.toUpperCase() : "");
        $("#fcClave").val(subCode && supportKey ? `21${String(subCode).padStart(2, "0")}${String(supportKey).padStart(4, "0")}` : "");
    };

    const setSoloLectura = (valor) => {
        estado.soloLectura = Boolean(valor);
        $("#fcSeccionFormulario").toggleClass("fc-readonly", estado.soloLectura);
        $(".fc-editable").prop("disabled", estado.soloLectura);
        $("#fcAsignaturaApoyo, #fcSubprograma, #fcModalidad, #fcEstrategiasSelect")
            .prop("disabled", estado.soloLectura)
            .trigger("change.select2");
        $("#fcBtnGuardar, #fcBtnCompletar").toggleClass("d-none", estado.soloLectura);
        $("#fcAvisoSoloLectura").toggleClass("d-none", !estado.soloLectura);
        renderTemas();
        renderBibliografias();
    };

    const mostrarFormulario = () => {
        $("#fcSeccionListado").addClass("d-none");
        $("#fcSeccionFormulario").removeClass("d-none");
        $("#fcBtnNuevo").addClass("d-none");
        $("#fcBtnRegresar, #fcBtnPdf").removeClass("d-none");
        $("#fcBtnPdf")
            .prop("disabled", !estado.idFormacion)
            .attr("title", estado.idFormacion
                ? "Generar PDF con la \u00faltima informaci\u00f3n guardada"
                : "Guarda primero la solicitud para generar el PDF");
        if (!estado.soloLectura) $("#fcBtnGuardar, #fcBtnCompletar").removeClass("d-none");
        bootstrap.Tab.getOrCreateInstance(document.querySelector('#fcTabs button[data-bs-target="#fcDatos"]')).show();
    };

    const mostrarListado = () => {
        $("#fcSeccionFormulario").addClass("d-none");
        $("#fcSeccionListado").removeClass("d-none");
        $("#fcBtnRegresar, #fcBtnGuardar, #fcBtnCompletar, #fcBtnPdf").addClass("d-none");
        $("#fcBtnNuevo").removeClass("d-none");
        estado.cargaCompleta = false;
    };

    const limpiarFormulario = () => {
        estado.idFormacion = null;
        estado.estatus = 1;
        estado.soloLectura = false;
        estado.cargaCompleta = false;
        estado.temas = [];
        estado.bibliografias = [];
        limpiarTemaEditor();
        $("#fcFolio").text("Nueva solicitud");
        $("#fcEstatusBadge").attr("class", "badge bg-secondary").text("Borrador");
        $("#fcAsignaturaApoyo, #fcSubprograma, #fcAreaConocimiento, #fcModalidad, #fcSemestre").val("").trigger("change.select2");
        $("#fcTipo").val("Práctico");
        $("#fcCaracter").val("Optativo");
        $("#fcNombre, #fcClave, #fcHorasPraSemana, #fcHorasPraSemestre, #fcObjetivo, #fcJustificacion").val("");
        $("#fcJustificacionContador").text("0");
        $("#fcEstrategiasSelect").val([]).trigger("change");
        setSoloLectura(false);
        renderTemas();
        renderBibliografias();
    };

    Object.assign(FC, {
        opcionesDataTable,
        inicializarTablas,
        llenarSelect,
        inicializarSelect2,
        pintarCatalogos,
        pintarAsignaturas,
        renderListado,
        TOLERANCIA_HORAS,
        formatearHoras,
        horasTotalesSemestre,
        horasTemasCapturadas,
        actualizarHorasRestantes,
        renderTemas,
        renderBibliografias,
        limpiarTemaEditor,
        recalcular,
        actualizarNombreClave,
        setSoloLectura,
        mostrarFormulario,
        mostrarListado,
        limpiarFormulario,
    });
})();
