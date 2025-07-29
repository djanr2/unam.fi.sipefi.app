/**
 * fcs es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * En esta clase encontraremos la mayoria de las funciones principales del flujo completo del sistema SIPEFI-TOMO II
 * @module fcs
 */
const fcs = function(){
	
	//Variables globales
	const camposPorTipo = {
	    'LIBRO IMPRESO': {
	      labels: ['Editorial', 'Edición (opcional)', '', ''],
	      requeridos: [true, false, false, false]
	    },
	    'ARTÍCULO IMPRESO': {
	      labels: ['Nombre de la Revista', 'Volumen(Número)', 'Páginas', 'DOI/URL (opcional)'],
	      requeridos: [true, true, true, false]
	    },
	    'NORMA O LEY': {
	      labels: ['Edición/Revisión (opcional)', 'Editorial/Organización', 'URL o DOI', ''],
	      requeridos: [false, true, true, false]
	    },
	    'APUNTES DE CLASE (MATERIAL DE CURSO)': {
	      labels: ['Tipo de Documento', 'Nombre de la Institución', 'URL/Enlace (opcional)', ''],
	      requeridos: [true, true, false, false]
	    },
	    'MATERIAL AUDIOVISUAL DIGITAL': {
	      labels: ['Tipo de Contenido', 'Plataforma/Sitio Web', 'URL', ''],
	      requeridos: [true, true, true, false]
	    },
	    'LIBRO ELECTRÓNICO': {
	      labels: ['Editorial', 'Edición (opcional)', 'DOI/URL', ''],
	      requeridos: [true, false, true, false]
	    },
	    'ARTÍCULO ELECTRÓNICO': {
	      labels: ['Nombre de la Revista', 'Volumen(Número)', 'Páginas', 'DOI/URL'],
	      requeridos: [true, true, true, true]
	    },
	    'DEFAULT': {
	      labels: ['Campo extra 1', 'Campo extra 2', 'Campo extra 3', 'Campo extra 4'],
	      requeridos: [false, false, false, false]
	    }
	 };
	
	/**
	 * Funcion que ajusta Look&feel de elementos mostrados en pantalla al usuario.
	 * @return {void} 
	 * @method cssVistaCaptura
	 * @static
	 */
	const cssVistaCaptura = () => {
		$(".row").css("margin-bottom", "5px");
	    $("span [role='presentation']").css("height","36px");
		$("span [role='combobox']").css("height","38px");
		$("span [role='textbox']").css("padding-top","4px");	
		$(".input-group-text").css("border-style","inset");
	};
	
	/**
	 * Funcion que carga los catalogos iniciales y necesarios en elementos Select para ser usados en el flujo de carga de una solicitud 
	 * @param {int} opc Parametro que tiene el tipo de visualizacion de la solicitud (nueva, edicion, visualizacion)
	 * @param {Object} param Parametro que tiene el objeto con la informacion de la solicitud que se esta copiando o editando.
	 * @return {void} 
	 * @method cargaCatalogos
	 * @static
	 */
	const cargaCatalogos = () => {
		try{
			soltii.cargaMenuLlenadoBotones();
			//inicializa datatables
			fl.cargaTablasSolicitud();
			let obj = fComun.getVarLocalJ("catalogos");
			// Cargar combos del tab "Datos generales"
			llenaCombo("area_con", obj.catAreaCon || [], false);
			llenaCombo("modalidad", obj.catModalidad || [], false);
			llenaCombo("tipo_modalidad", obj.catTipoMod || [], false);
			llenaCombo("caracter", obj.catCarAsig || [], false);

			// Cargar combos del tab "Relación con Licenciaturas"
			llenaCombo("rel_licenciatura", obj.catLic || [], false);
			llenaCombo("rel_semestre", [...Array(10).keys()].map(i => [i + 1, `Semestre ${i + 1}`]), false); // del 1 al 10
			llenaCombo("ser_anterior", obj.catAsig || [], true);
			llenaCombo("ser_consecuente", obj.catAsig || [], true);
			
			//Cargar combos de la sección de bibliografia
			llenaCombo("tipo_bibliografia", obj.catTipoBib || [], false);
			
			// Cargar combos de la sección Estrategias y Evaluación
			// Estrategias didácticas (múltiple)
			$('#estrategias_didacticas').select2({
			    placeholder: "Selecciona una o más estrategias",
			    width: '100%'
			});
			llenaCombo("estrategias_didacticas", obj.catEstDid || [], false);

			// Formas de evaluación separadas por tipo
			if (obj.catFormEval) {
			  const diagnostica = obj.catFormEval.filter(f => fComun.quitarAcentos(f[2]) === "diagnostica");
			  const formativa   = obj.catFormEval.filter(f => fComun.quitarAcentos(f[2]) === "formativa");
			  const sumativa    = obj.catFormEval.filter(f => fComun.quitarAcentos(f[2]) === "sumativa");
			
			  llenaCombo("eval_diagnostica", diagnostica, false);
			  llenaCombo("eval_formativa", formativa, false);
			  llenaCombo("eval_sumativa", sumativa, false);
			}
		}catch(e){console.error("Error al cargar catálogos:", e);}
		cssVistaCaptura();
	};
	
	/**
	 * Llena un select a partir de un catálogo tipo array bidimensional.
	 * @param {string} idSelector - ID del select sin "#"
	 * @param {Array} datos - Array de arrays [valor, texto]
	 * @param {boolean} [conElige=true] - Si se incluye opción por default
	 */
	const llenaCombo = (idSelector, datos, conElige = true) => {
		try {
			let $combo = $("#" + idSelector);
			$combo.empty();
			if (conElige) {
				$combo.append('<option value="">Elige una opci&oacute;n</option>');
			}
			datos.forEach(([val, txt]) => {
				$combo.append(`<option value="${val}">${txt}</option>`);
			});
		} catch (e) {
			console.error("Error llenando combo:", idSelector, e);
		}
	};
	
	/**
	 * Función que agrega una nueva relación con licenciatura si es válida, no duplicada y usa DataTables.
	 * @function agregarRelacionLicAsig
	 */
	const agregarRelacionLicAsig = () => {
	  let tablaRelacionesDT = $('#tablaRelacionesLic').DataTable();
	  // Obtener valores seleccionados de los campos
	  const idLic = $("#rel_licenciatura").val();
	  const txtLic = $("#rel_licenciatura option:selected").text().trim();
	  const semestre = $("#rel_semestre").val();
	  const serAnt = $("#ser_anterior").val();
	  const serCon = $("#ser_consecuente").val();
	  const txtAnt = $("#ser_anterior option:selected").text().trim();
	  const txtCon = $("#ser_consecuente option:selected").text().trim();

	  // Validación: licenciatura debe estar seleccionada
	  if (!idLic || idLic === "0") {
	    fComun.mostrarTooltipCampo("#rel_licenciatura", "Selecciona una licenciatura válida");
	    return;
	  }

	  // Validación: semestre obligatorio
	  if (!semestre) {
	    fComun.mostrarTooltipCampo("#rel_semestre", "Selecciona el semestre");
	    return;
	  }

	  // Validación: seriación anterior y consecuente no deben ser iguales (si ambas están definidas)
	  if (serAnt && serCon && serAnt === serCon) {
	    fComun.mostrarTooltipCampo("#ser_consecuente", "No puede ser igual a la seriación anterior");
	    return;
	  }

	  // Validación: evitar duplicados en el DataTable (por nombre de licenciatura)
	  const existe = tablaRelacionesDT
	    .rows()
	    .data()
	    .toArray()
	    .some(row => row[0].trim() === txtLic);

	  if (existe) {
	    fComun.mostrarTooltipCampo("#rel_licenciatura", "Ya existe la relación de la licenciatura.");
	    return;
	  }

	  // Utilidad para mostrar texto solo si el valor es válido (no vacío ni "0")
	  const mostrarTexto = (valor, texto) => {
	    return valor && valor !== "0" ? texto : '';
	  };

	  // Determinar los textos visibles para seriación anterior y consecuente
	  const mostrarAnt = mostrarTexto(serAnt, txtAnt);
	  const mostrarCon = mostrarTexto(serCon, txtCon);

	  // Botón de eliminar y campo oculto con valores concatenados
	  const botonEliminar = `
	    <button class="btn btn-sm btn-danger btnEliminarRelacion">
	      <i class="fas fa-trash-alt"></i>
	    </button>
	    <input type="hidden" class="datos-relacion" 
	           value="${idLic}@##@${semestre}@##@${serAnt || ''}@##@${serCon || ''}">
	  `;

	  // Agregar nueva fila al DataTable
	  tablaRelacionesDT.row.add([
	    txtLic,
	    semestre,
	    mostrarAnt,
	    mostrarCon,
	    botonEliminar
	  ]).draw();

	  // Limpiar campos después de agregar
	  $("#rel_licenciatura").val("0");
	  $("#rel_semestre").val("1");
	  $("#ser_anterior").val("");
	  $("#ser_consecuente").val("");
	};
	
	/**
	 * Función que actualiza dinámicamente los textos de los campos adicionales
	 * y marca visualmente si son requeridos, según el tipo de bibliografía seleccionado.
	 */
	const actualizarCamposExtra = () => {
	  const tipo = $('#tipo_bibliografia option:selected').text().trim().toUpperCase();
	  const config = camposPorTipo[tipo] || camposPorTipo['DEFAULT'];
	  const labels = config.labels;
	  const requeridos = config.requeridos;

	  // Función auxiliar para generar label con o sin asterisco rojo
	  const generaLabel = (texto, requerido) => {
	    return requerido
	      ? `${texto} <span class="text-danger">*</span>`
	      : texto;
	  };

	  $('#lbl_extra_1').html(generaLabel(labels[0] || 'Campo extra 1', requeridos[0]));
	  $('#lbl_extra_2').html(generaLabel(labels[1] || 'Campo extra 2', requeridos[1]));
	  $('#lbl_extra_3').html(generaLabel(labels[2] || 'Campo extra 3', requeridos[2]));
	  $('#lbl_extra_4').html(generaLabel(labels[3] || 'Campo extra 4', requeridos[3]));

	  // Marcar también los campos fijos requeridos
	  $('#lbl_autor').html('<strong>Autor(es) <span class="text-danger">*</span></strong>');
	  $('#lbl_anio').html('<strong>A&ntilde;o de publicaci&oacute;n <span class="text-danger">*</span></strong>');
	  $('#lbl_titulo').html('<strong>T&iacute;tulo <span class="text-danger">*</span></strong>');
	  $('#lbl_temas').html('<strong>Temas donde se recomienda <span class="text-danger">*</span></strong>');
	};
	
	/**
	 * Función que valida los campos requeridos según el tipo seleccionado y agrega una fila a la tabla.
	 */
	const validaCamposReqBiblio = () => {
		const tipoTexto = $('#tipo_bibliografia option:selected').text().trim().toUpperCase();
		const config = camposPorTipo[tipoTexto] || camposPorTipo['DEFAULT'];
		const requeridos = config.requeridos;

		// Obtener valores
		const idTipo = $('#tipo_bibliografia').val();
		const autor = $('#autor_biblio').val().trim();
		const anio = $('#anio_biblio').val().trim();
		const titulo = $('#titulo_biblio').val().trim();
		const extra1 = $('#extra_1').val().trim();
		const extra2 = $('#extra_2').val().trim();
		const extra3 = $('#extra_3').val().trim();
		const extra4 = $('#extra_4').val().trim();
		const temas = $('#temas_biblio').val().trim();

		// Validaciones básicas
		if (!idTipo || idTipo === '0') {
		  fComun.mostrarTooltipCampo('#tipo_bibliografia', 'Selecciona un tipo de bibliografía');
		  return;
		}
		if (!autor) {
		  fComun.mostrarTooltipCampo('#autor_biblio', 'Ingresa el/los autores');
		  return;
		}
		if (!anio || isNaN(anio)) {
		  fComun.mostrarTooltipCampo('#anio_biblio', 'Ingresa un año válido');
		  return;
		}
		if (!titulo) {
		  fComun.mostrarTooltipCampo('#titulo_biblio', 'Ingresa el título');
		  return;
		}
		
		if (!temas) {
		  fComun.mostrarTooltipCampo('#temas_biblio', 'Indica en qué temas se recomienda esta bibliografía');
		  return;
		}

		// Validar campos extras si están marcados como requeridos
		if (requeridos[0] && !extra1) {
		  fComun.mostrarTooltipCampo('#extra_1', `Campo requerido: ${config.labels[0]}`);
		  return;
		}
		if (requeridos[1] && !extra2) {
		  fComun.mostrarTooltipCampo('#extra_2', `Campo requerido: ${config.labels[1]}`);
		  return;
		}
		if (requeridos[2] && !extra3) {
		  fComun.mostrarTooltipCampo('#extra_3', `Campo requerido: ${config.labels[2]}`);
		  return;
		}
		if (requeridos[3] && !extra4) {
		  fComun.mostrarTooltipCampo('#extra_4', `Campo requerido: ${config.labels[3]}`);
		  return;
		}

		// Construcción de fila
		const fila = `
		  <tr>
		    <td>${tipoTexto}</td>
		    <td>${autor}</td>
		    <td>${anio}</td>
		    <td>${titulo}</td>
		    <td>${extra1}</td>
		    <td>${extra2}</td>
		    <td>${extra3}</td>
		    <td>${extra4}</td>
		    <td>${temas}</td>
		    <td>
		      <button class="btn btn-sm btn-danger btn-eliminar-biblio" type="button">
		        <i class="fas fa-trash-alt"></i>
		      </button>
		      <input type="hidden" class="datos-biblio" value="${idTipo}@##@${autor}@##@${anio}@##@${titulo}@##@${extra1}@##@${extra2}@##@${extra3}@##@${extra4}@##@${temas}">
		    </td>
		  </tr>
		`;

		// Agrega fila al DataTable
		$('#tablaBibliografia').DataTable().row.add($(fila)).draw();

		// Limpia los campos
		$('#tipo_bibliografia').val('0');
		$('#autor_biblio').val('');
		$('#anio_biblio').val('');
		$('#titulo_biblio').val('');
		$('#extra_1').val('');
		$('#extra_2').val('');
		$('#extra_3').val('');
		$('#extra_4').val('');
		$('#temas_biblio').val('');
	};
	
	/**
	 * Función que obtiene los datos de la tabla de bibliografía y los estructura como objetos.
	 * Cada fila representa una bibliografía registrada, incluyendo campos adicionales y temas asociados.
	 *
	 * @function obtenerBibliografia
	 * @returns {Array<Object>} Lista de objetos con los datos de la bibliografía.
	 */
	const obtenerBibliografia = () => {
	  const catalogoTipos = (fComun.getVarLocalJ("catalogos")?.catTipoBib) || [];
	  const tabla = $('#tablaBibliografia').DataTable();
	  const data = [];
	
	  tabla.rows().every(function () {
	    const fila = $(this.node()).find('td');
	    const tipoTexto = fila.eq(0).text().trim();
	    const tipoObj = catalogoTipos.find(([id, nombre]) => nombre.trim().toUpperCase() === tipoTexto.toUpperCase());
	
	    data.push({
	      idTipo: tipoObj ? tipoObj[0] : null,
	      tipo: tipoTexto,
	      autor: fila.eq(1).text().trim(),
	      anio: fila.eq(2).text().trim(),
	      titulo: fila.eq(3).text().trim(),
	      extra1: fila.eq(4).text().trim(),
	      extra2: fila.eq(5).text().trim(),
	      extra3: fila.eq(6).text().trim(),
	      extra4: fila.eq(7).text().trim(),
	      temas: fila.eq(8).text().trim()
	    });
	  });
	
	  return data;
	};
	
	/**
	 * Función que recorre la tabla de relación con licenciaturas para extraer
	 * los datos seleccionados por el usuario.
	 * 
	 * Cada fila contiene: licenciatura, semestre, seriación anterior y consecuente.
	 *
	 * @function obtenerRelLicAsig
	 * @returns {Array<Object>} Arreglo con objetos que representan la relación con licenciaturas.
	 */
	const obtenerRelLicAsig = () => {
	  const catalogoLic = fComun.getVarLocalJ("catalogos")?.catLic || [];
	  const catalogoAsig = fComun.getVarLocalJ("catalogos")?.catAsig || [];
	  const tabla = $('#tablaRelacionesLic').DataTable();
	  const data = [];
	
	  tabla.rows().every(function () {
	    const fila = $(this.node()).find('td');
	
	    const licNombre = fila.eq(0).text().trim();
	    const seriacionAnt = fila.eq(2).text().trim();
	    const seriacionCon = fila.eq(3).text().trim();
	
	    const licObj = catalogoLic.find(([id, nombre]) => nombre.trim() === licNombre);
	    const antObj = catalogoAsig.find(([id, nombre]) => nombre.trim() === seriacionAnt);
	    const conObj = catalogoAsig.find(([id, nombre]) => nombre.trim() === seriacionCon);
	
	    data.push({
	      idLicenciatura: licObj ? licObj[0] : null,
	      licenciatura: licNombre,
	      semestre: fila.eq(1).text().trim(),
	      idSeriacionAnterior: antObj ? antObj[0] : null,
	      seriacionAnterior: seriacionAnt,
	      idSeriacionConsecuente: conObj ? conObj[0] : null,
	      seriacionConsecuente: seriacionCon
	    });
	  });

	  return data;
	};
	
	/**
	 * Función que obtiene la información capturada en las tablas de Temario y Contenido.
	 * La tabla de Temas contiene número, nombre, horas y objetivo.
	 * La tabla de Contenido contiene el número del subtema, la relación con el tema y la descripción.
	 * 
	 * @function obtenerTemarioYContenido
	 * @returns {Object} Objeto con dos arreglos: `temas` y `contenidos`.
	 */
	const obtenerTemarioYContenido = () => {
	  const temas = [];
	  const tablaTemasDT = $('#tablaTemas').DataTable();
	
	  tablaTemasDT.rows().every(function () {
	    const data = this.data(); // ← Aquí está la diferencia clave
	    temas.push({
	      numeroTema: data[0]?.toString().trim() || '',
	      nombre: data[1]?.toString().trim() || '',
	      horas: data[2]?.toString().trim() || '',
	      objetivo: data[3]?.toString().trim() || ''
	    });
	  });
	
	  const contenidos = [];
	  const tablaContenidosDT = $('#tablaContenidos').DataTable();
	
	  tablaContenidosDT.rows().every(function () {
	    const data = this.data();
	    contenidos.push({
	      temaRelacionado: data[0]?.toString().trim() || '',
	      numeroCont: data[1]?.toString().trim() || '',
	      contenido: data[2]?.toString().trim() || ''
	    });
	  });
	
	  return { temas, contenidos };
	};
	
	/**
	 * Funcion que ayuda a realizar la accion de la solicitud que el usuario desea aplicar.
	 * @param {int} accion Parametro que indica la accion a realizar a la solicitud (1-Guardar o editar solicitud, 2-Realizar Calculo, 3-Procesar solicitud, 4-Rechazar solicitud).
	 * @param {Object} obj Parametro que contiene informacion de la solicitud.
	 * @param {Boolean} saveObjC Parametro que indica si se debe guardar informacion para el calculo.
	 * @return {void} 
	 * @method accionSolicitud
	 * @static
	 */
	const accionSolicitud = (accion) => {
		objSolicitud = construirSolicitud();
		let modalAprob = "#modalAprobSoliEstatus";
		objRespCalc = [];

		objSolicitud["accionSoli"] = accion;
		console.log(objSolicitud)
		
		fComun.post2("/SIPEFI/accionSolicitud/", objSolicitud, function(resp){
			try{
				let obj = resp;
				if(obj.estatus == 200){
					if(accion == 1){ //Se guardo o edito solicitud
						let numSoli = obj.respuesta.idS;
						let idES = obj.respuesta.idES;
						let nomES = obj.respuesta.nomES;
						$("#numSolicitud").html(numSoli);
						$("#estatusSoli").html(nomES);
						$("#idES").html(idES);
						texto = "Se proces&oacute; correctamente el guardado de la solicitud. <br> " +
								"<strong>Numero solicitud:</strong> SIPEFI-"+numSoli+" ("+nomES+")";
						mostrarModalGuardar(1,texto);
						validarBotonesCambioEstatus(1);
						fComun.guardaVarLocalS("accionSoli",2);
					}else if(accion == 2){ //Se proceso correctamente estatus solicitud
						let msjConfirm = "La aprobaci&oacute;n de la solicitud se ha realizado correctamente.";
						let estatus = objSolicitud["idEstSoli"];
						msjConfirm = (estatus==1)?"La solicitud ha sido enviada correctamente para su aprobaci&oacute;n.":msjConfirm;
						$(modalAprob+" .textoBody").html(msjConfirm);
						$(modalAprob).modal('show');
						epf.eventoAprobSoli(".cierraModalAprob",modalAprob);
					}else if(accion == 3){ //Se rechazo correctamente la solicitud
						let msjConfirm = "La solicitud ha sido rechazada correctamente.";
						$(modalAprob+" .textoBody").html(msjConfirm);
						$(modalAprob).modal('show');
						epf.eventoAprobSoli(".cierraModalAprob",modalAprob);
					}
				}else{
					let palabra = (accion==1)?"guardado":(accion==2)?"procesamiento":"rechazo";
					texto = "No fue posible realizar el "+palabra+" de la solicitud <br>" +
							"<strong>Avisa al &aacute;rea de sistemas correspondiente</strong>";
					mostrarModalGuardar(2,texto);
				}
			}catch(e){console.log(e)}
		});
		
	};
	
	/**
	 * Construye y retorna el objeto solicitud con todos los datos actuales del formulario.
	 * @function construirSolicitud
	 * @returns {Object} Objeto completo de la solicitud.
	 */
	const construirSolicitud = () => {
	  return {
	    datosGenerales: {
	      areaConocimiento: $('#area_con').val(),
	      modalidad: $('#modalidad').val(),
	      tipoModalidad: $('#tipo_modalidad').val(),
	      caracterAsignatura: $('#caracter').val(),
	      nombreAsignatura: $('#asignatura').val(),
	      creditos: $('#creditos').val(),
	      hSemTeoria: $('#h_sem_teo').val(),
	      hSemPractica: $('#h_sem_pra').val(),
	      hSemestreTeoria: $('#h_semestre_teo').val(),
	      hSemestrePractica: $('#h_semestre_pra').val(),
	      objAsig: $("#objetivo").val()
	    },
	    relacionLicenciaturas: obtenerRelLicAsig(),
	    temario: obtenerTemarioYContenido().temas,
	    contenido: obtenerTemarioYContenido().contenidos,
	    bibliografia: obtenerBibliografia(),
	    estrategiasEvaluacion: {
	      estrategiasDidacticas: $('#estrategias_didacticas').val(),
	      formasEvaluacion: {
	        diagnostica: $('#eval_diagnostica').val(),
	        formativa: $('#eval_formativa').val(),
	        sumativa: $('#eval_sumativa').val()
	      },
	      formacionIntegral: $('#formacion_integral').val(),
	      perfilProfesiografico: $('#perfil_profesiografico').val()
	    },
	    metadatos: {
	      usuario: $("#usuario").html(),
	      rol: $("#rol").html(),
	      token: $("#token").html(),
	      numSolicitud: $("#numSolicitud").html(),
	      accionGA: ($.isNumeric($("#numSolicitud").html()) ? 2 : 1),
	      idEstSoli: $("#idES").html(),
	      usuarioSoli: $("#usuarioSol").html(),
	      comentarios: $("#comentarios").Editor("getText")
	    }
	  };
	};
	
	/**
	 * Funcion que se encarga de presentar un modal de error o de guardado exitoso tras procesar el guardado de una solicitud.
	 * @param {int} opc Parametro que indica si se desea presentar modal como error o exitoso.
	 * @param {String} texto Parametro que contiene el texto que se desea poner en el cuerpo del modal.
	 * @return {void}
	 * @method mostrarModalGuardar
	 * @static
	 */
	const mostrarModalGuardar = (opc, texto) => {
		$("#modalRespGuardar .modal-title").html((opc==1)?"Guardado/Actualizaci&oacute;n exitosa":"Mensaje de error");
		$("#modalRespGuardar .modal-header").removeClass((opc==1)?"headerModalError":"headerModalSucess");
		$("#modalRespGuardar .modal-header").addClass((opc==1)?"headerModalSucess":"headerModalError");
		$("#modalRespGuardar .textoBody").html(texto);
		$("#modalRespGuardar .modal-body button").attr('class',(opc==1)?'btn btn-success':'btn btn-danger');
		$('#modalRespGuardar').modal('show');
		fComun.ocultarEspera();
	};
	
	return{
		cssVistaCaptura:	cssVistaCaptura,
		cargaCatalogos:	cargaCatalogos,
		agregarRelacionLicAsig: agregarRelacionLicAsig,
		actualizarCamposExtra:	actualizarCamposExtra,
		validaCamposReqBiblio:	validaCamposReqBiblio,
		accionSolicitud:	accionSolicitud
	}
}();