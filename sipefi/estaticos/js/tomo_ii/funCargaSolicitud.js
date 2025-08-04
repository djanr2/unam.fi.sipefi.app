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
		'TESIS': {
	      labels: ['Grado de la Tesis', 'Institución que otorga título', 'Nombre del repositorio', 'URL del repositorio'],
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
	 * @param {Object} param Parametro que tiene el objeto con la informacion de la solicitud que se esta editando o visualizando.
	 * @return {void} 
	 * @method cargaCatalogos
	 * @static
	 */
	const cargaCatalogos = (opc, param) => {
		try{
			soltii.cargaMenuLlenadoBotones();
			//inicializa datatables
			fl.cargaTablasSolicitud();
			let obj = fComun.getVarLocalJ("catalogos");
			// Cargar combos del tab "Datos generales"
			llenaCombo("area_con", obj.catAreaCon || [], false);
			llenaCombo("modalidad", obj.catModalidad || [], false);
			llenaCombo("tipo_modalidad", obj.catTipoMod || [], false);
			llenaCombo("valor_practico", obj.catValPract || [], false);
			$('#valor_practico').select2({
			    placeholder: "Elige una opción",
			    width: '100%'
			});
			llenaCombo("caracter", obj.catCarAsig || [], false);

			// Cargar combos del tab "Relación con Licenciaturas"
			llenaCombo("rel_licenciatura", obj.catLic || [], false);
			llenaCombo("rel_semestre", [...Array(10).keys()].map(i => [i + 1, `Semestre ${i + 1}`]), false); // del 1 al 10
			// seriación antecedente y consecuente (múltiple)
			$('#ser_anterior').select2({
			    placeholder: "Selecciona una o más seriaciones",
			    width: '100%'
			});
			$('#ser_consecuente').select2({
			    placeholder: "Selecciona una o más seriaciones",
			    width: '100%'
			});
			llenaCombo("ser_anterior", obj.catAsig || [], false);
			llenaCombo("ser_consecuente", obj.catAsig || [], false);
			
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
		if(opc == 2){ //Solo si estamos editando una solicitud existente
			soltii.pintaSolicitud(param);
		}
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
	  
	  // Obtener arrays de selección múltiple (filtrando si hay un "0")
	  let serAnt = $("#ser_anterior").val() || [];
	  let serCon = $("#ser_consecuente").val() || [];
	  serAnt = serAnt.filter(val => val !== "0");
	  serCon = serCon.filter(val => val !== "0");
	  
	  const txtAnt = serAnt.map(val => $(`#ser_anterior option[value="${val}"]`).text().trim());
	  const txtCon = serCon.map(val => $(`#ser_consecuente option[value="${val}"]`).text().trim());

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
	  // Validación: no debe haber elementos comunes entre antecedente y consecuente
	  const interseccion = serAnt.some(val => serCon.includes(val));
	  if (interseccion) {
       fComun.mostrarTooltipCampo("#ser_consecuente", "No puede haber materias repetidas en seriación antecedente y consecuente");
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

	  // Construir textos para mostrar en la tabla
	  const mostrarAnt = txtAnt.join(" | ");
	  const mostrarCon = txtCon.join(" | ");
	  
	  // Botón de eliminar y campo oculto con valores concatenados
	  const botonEliminar = `
	    <button class="btn btn-sm btn-danger btnEliminarRelacion">
	      <i class="fas fa-trash-alt"></i>
	    </button>
	    <input type="hidden" class="datos-relacion" 
	           value="${idLic}@##@${semestre}@##@${serAnt.join(",")}@##@${serCon.join(",")}">
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
	  $("#ser_anterior").val(null).trigger("change");
	  $("#ser_consecuente").val(null).trigger("change");;
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

	  // Recorremos los 4 campos extra
	   for (let i = 0; i < 4; i++) {
	     const label = labels[i];
	     const requerido = requeridos[i];
	     const divId = `#div_extra_${i + 1}`;
	     const labelId = `#lbl_extra_${i + 1}`;

	     if (label && label.trim() !== '') {
	       $(divId).show();
	       $(labelId).html(generaLabel(label, requerido));
	     } else {
	       $(divId).hide();
	     }
	   }
	};
	
	/**
	 * Función que valida los campos requeridos según el tipo seleccionado y agrega una fila a la tabla.
	 */
	const validaCamposReqBiblio = () => {
		const tipoTextoOrig = $('#tipo_bibliografia option:selected').text().trim();
		const tipoTexto = $('#tipo_bibliografia option:selected').text().trim().toUpperCase();
		const config = camposPorTipo[tipoTexto] || camposPorTipo['DEFAULT'];
		const requeridos = config.requeridos;

		// Obtener valores
		const idTipo = $('#tipo_bibliografia').val();
		const autor = $('#autor_biblio').val().trim();
		const anio = $('#anio_biblio').val().trim();
		const clasif = $('#clasificacion_biblio').val().trim();
		const clasifTexto = $('#clasificacion_biblio option:selected').text().trim();
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
		    <td>${tipoTextoOrig}</td>
		    <td>${autor}</td>
		    <td>${anio}</td>
			<td>${clasifTexto}</td>
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
		      <input type="hidden" class="datos-biblio" value="${idTipo}@##@${autor}@##@${anio}@##@${clasif}@##@${titulo}@##@${extra1}@##@${extra2}@##@${extra3}@##@${extra4}@##@${temas}">
		    </td>
		  </tr>
		`;

		// Agrega fila al DataTable
		$('#tablaBibliografia').DataTable().row.add($(fila)).draw();

		// Limpia los campos
		$('#tipo_bibliografia').val('0').trigger('change');
		$('#autor_biblio').val('');
		$('#anio_biblio').val('');
		$('#clasificacion_biblio').val('0');
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
		const clasifTexto = fila.eq(3).text().trim().toLowerCase();
		const clasif = clasifTexto === 'complementaria' ? 1 : 0;
		
	    data.push({
	      idTipo: tipoObj ? tipoObj[0] : null,
	      tipo: tipoTexto,
	      autor: fila.eq(1).text().trim(),
	      anio: fila.eq(2).text().trim(),
		  clasifBiblio: clasif,
	      titulo: fila.eq(4).text().trim(),
	      extra1: fila.eq(5).text().trim(),
	      extra2: fila.eq(6).text().trim(),
	      extra3: fila.eq(7).text().trim(),
	      extra4: fila.eq(8).text().trim(),
	      temas: fila.eq(9).text().trim()
	    });
	  });
	
	  return data;
	};
	
	/**
	 * Función que recorre la tabla de relación con licenciaturas para extraer
	 * los datos seleccionados por el usuario.
	 * 
	 * Cada fila contiene: licenciatura, semestre, seriación antecedente y consecuente.
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
	    const semestre = fila.eq(1).text().trim();
	    const serAntTexto = fila.eq(2).text().trim();
	    const serConTexto = fila.eq(3).text().trim();

	    // Separar por '|', quitar espacios extras y filtrar vacíos
	    const serAntArr = serAntTexto.split("|").map(t => t.trim()).filter(t => t);
	    const serConArr = serConTexto.split("|").map(t => t.trim()).filter(t => t);

	    // Buscar los IDs correspondientes en catálogo
	    const idAnt = serAntArr.map(nombre =>
	      (catalogoAsig.find(([id, nom]) => nom.trim() === nombre)?.[0]) || null
	    );

	    const idCon = serConArr.map(nombre =>
	      (catalogoAsig.find(([id, nom]) => nom.trim() === nombre)?.[0]) || null
	    );

	    // Buscar ID de licenciatura
	    const licObj = catalogoLic.find(([id, nombre]) => nombre.trim() === licNombre);
	    const idLic = licObj ? licObj[0] : null;

	    data.push({
	      idLicenciatura: idLic,
	      licenciatura: licNombre,
	      semestre: semestre,
	      idSeriacionAnterior: idAnt,
	      seriacionAnterior: serAntArr,
	      idSeriacionConsecuente: idCon,
	      seriacionConsecuente: serConArr
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
	 * @param {int} accion Parametro que indica la accion a realizar a la solicitud (1-Guardar o editar solicitud, 2-Procesar solicitud, 3-Rechazar solicitud).
	 * @param {Object} obj Parametro que contiene informacion de la solicitud.
	 * @param {Boolean} saveObjC Parametro que indica si se debe guardar informacion para el calculo.
	 * @return {void} 
	 * @method accionSolicitud
	 * @static
	 */
	const accionSolicitud = (accion) => {
		objSolicitud = construirSolicitud();
		let modalAprob = "#modalAprobSoliEstatus";
		objSolicitud["accionSoli"] = accion;
		
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
							"Contacta al área de soporte con Osvaldo Ruiz <br>" +
							"<strong><a href=\"mailto:oruiz@unam.mx?subject=Necesito%20ayuda\">" +
								"oruiz@unam.mx" +
							"</a></strong>";
					mostrarModalGuardar(2,texto);
				}
			}catch(e){console.log(e)}
		});
		
	};
	
	/**
	 * Funcion que ayuda a validar los botones que deben presentarse a cada perfil y en la seccion especifica.
	 * @param {int} accion Parametro que indica si se pueden o no mostrar los botones. (1-se pueden mostrar, 2-esconder botones).
	 * @return {void} 
	 * @method validarBotonesCambioEstatus
	 * @static
	 */
	const validarBotonesCambioEstatus = (accion) => {
		let idRV = fComun.getVarLocalJ("idsValidador");
		accion = Number(accion);
		let rol = Number($("#rol").html());
		$('.menuBotones[target="rechazarSolicitud"]').hide();
		$('.menuBotones[target="aprobarSolicitud"]').hide();
		if($.inArray(rol,idRV) != -1){
			$('.menuBotones[target="rechazarSolicitud"]').show();
			$('.menuBotones[target="aprobarSolicitud"]').show();
		}else{
			if(accion == 1){
				$('.menuBotones[target="aprobarSolicitud"]').show();
			}
		}
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
		  valorPractico: $('#valor_practico').val(),
	      caracterAsignatura: $('#caracter').val(),
	      nombreAsignatura: $('#asignatura').val(),
		  claveAsignatura: $('#clave_asignatura').val(),
	      creditos: $('#creditos').val(),
	      hSemTeoria: $('#h_sem_teo').val(),
	      hSemPractica: $('#h_sem_pra').val(),
	      hSemestreTeoria: $('#h_semestre_teo').val(),
	      hSemestrePractica: $('#h_semestre_pra').val(),
	      objAsig: $("#objetivo").val()
	    },
	    relacionLicenciaturas: obtenerRelLicAsig(),
	    temario: obtenerTemarioYContenido().temas,
		actPracticas: $('#horasPracticasTemario').val(),
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
	    const modal = $("#modalRespGuardar");
	    const header = modal.find(".modal-header");
	    const title = modal.find(".modal-title");
	    const body = modal.find(".textoBody");
	    const btn = modal.find(".modal-body button");

	    // Título
	    title.html(opc == 1 ? "Guardado/Actualización exitosa" : "Mensaje de error");

	    // Limpiar clases de header
	    header.removeClass("headerModalError headerModalSucess headerModalInfo headerModalAlerta");

	    header.addClass(opc == 1 ? "headerModalSucess" : "headerModalError");
	    body.html(texto);

	    // Botón con estilo correspondiente
	    btn.attr("class", opc == 1 ? "btn btn-success" : "btn btn-danger");

	    modal.modal("show");
	    fComun.ocultarEspera();
	};
	
	/**
	 * Funcion que muestra la informacion de la solicitud procesada de acuerdo a la accion elegida.
	 * @param {Object} obj Parametro que contiene la informacion de la solicitud, asi como la accion a realizar con dicha informacion (1-visualizar, 2-editar).
	 * @return {void}
	 * @method cargaSolicitudAccion
	 * @static
	 */
	const cargaSolicitudAccion = (solicitud) => {
		let accion = Number(solicitud.accion);
		fComun.guardaVarLocalS("accionSoli",accion);
		fComun.guardaVarLocal("objSoli",solicitud);
		//Solicitud existente
		$("#numSolicitud").html(solicitud.numSolicitud);
		$("#estatusSoli").html(solicitud.nomEstSoli);
		$("#idES").html(solicitud.idEstSoli);
		$("#usuarioSol").html(solicitud.usuarioSoli);
		validarBotonesCambioEstatus(1);
		if(accion == 2){ // 2-Editar
			$('.menuBotones[target="guardarSolicitud"]').show();
			$('.menuBotones[target="#modalComentarios"]').show();
		}else if(accion == 1){ // Visualizar
			$('.menuBotones[target="guardarSolicitud"]').hide();
		}
		/*	
			Si solo puede visualizar sin proceder a validar
			se esconden todos los botones menos el de regresar
		*/
		if(!fComun.getVarLocalJ("canAffect")){
			$('.menuBotones').hide();
			$('.menuBotones[target="regresarBusqSoli"]').show();
		}
		
		try {
			if (!solicitud) return;

			// === 1. DATOS GENERALES ===
			const dg = solicitud.datosGenerales;
			$('#asignatura').val(dg.asignatura);
			$('#clave_asignatura').val(dg.claveAsignatura);
			$('#creditos').val(dg.creditos);
			$('#area_con').val(dg.areaConocimiento);
			$('#modalidad').val(dg.modalidad);
			$('#tipo_modalidad').val(dg.tipoModalidad);
			$('#caracter').val(dg.caracterAsignatura);
			$("#valor_practico").val(solicitud.valorPractico).trigger("change");
			$('#h_sem_teo').val(dg.hSemTeoria);
			$('#h_sem_pra').val(dg.hSemPractica);
			$('#h_semestre_teo').val(dg.hSemestreTeoria);
			$('#h_semestre_pra').val(dg.hSemestrePractica);
			$('#objetivo').val(dg.objAsig);

			// === 2. RELACIÓN CON LICENCIATURAS (sección tabla) ===

			(solicitud.relacionLicenciaturas || []).forEach(rel => {
			  const idLic = rel.idLic;
			  const semestre = rel.semestre;
			  const serAnt = rel.seriacionAnt || [];
			  const serCon = rel.seriacionCons || [];

			  // Establecer licenciatura y semestre
			  $('#rel_licenciatura').val(idLic).trigger('change');
			  $('#rel_semestre').val(semestre).trigger('change');

			  // Cargar select multiple de seriación antecedente y consecuente
			  $('#ser_anterior').val(serAnt).trigger('change');
			  $('#ser_consecuente').val(serCon).trigger('change');

			  // Simular clic en botón agregar relación
			  $('#btnAgregarRelLicAsig').click();
			});
			
			// === 3. TEMARIO Y CONTENIDO ===
			$('#horasPracticasTemario').val(solicitud.actPracticas);
			(solicitud.temario || []).forEach(t => {
			  $('#nombreTema').val(t.nombre);
			  $('#horasTema').val(t.horas);
			  $('#objetivoTema').val(t.objetivo);
			  $('#btnAgregarTema').trigger('click');
			});
			
			(solicitud.contenido || []).forEach(c => {
			  $('#temaContenido').val(c.temaRelacionado).trigger('change');
			  $('#contenidoTema').val(c.contenido);
			  $('#btnAgregarContenido').trigger('click');
			});

			// === 4. BIBLIOGRAFÍA ===
			const tablaBib = $('#tablaBibliografia').DataTable();
			const catTipoBib = fComun.getVarLocalJ("catalogos")?.catTipoBib || [];
			tablaBib.clear();

			(solicitud.bibliografia || []).forEach(b => {
				const tipoBib = catTipoBib.find(([id]) => id == b.idTipo)?.[1] || "Tipo desconocido";
				const clasif = b.clasifBiblio == 1 ? "Complementaria" : "Básica";
				const hidden = `<input type="hidden" class="datos-biblio" value="${b.idTipo}@##@${b.autor}@##@${b.anio}@##@${b.clasifBiblio}@##@${b.titulo}@##@${b.extra1}@##@${b.extra2}@##@${b.extra3}@##@${b.extra4}@##@${b.temas}">`;

				tablaBib.row.add([
					tipoBib, b.autor, b.anio, clasif, b.titulo, b.extra1, b.extra2, b.extra3, b.extra4, b.temas,
					`<button class="btn btn-sm btn-danger btn-eliminar-biblio"><i class="fas fa-trash-alt"></i></button>${hidden}`
				]);
			});
			tablaBib.draw();

			// === 5. ESTRATEGIAS Y EVALUACIÓN ===
			const estEval = solicitud.estrategiasEvaluacion;
			$('#estrategias_didacticas').val(estEval.estrategiasDidacticas || []).trigger('change');
			$('#formacion_integral').val(estEval.formacionIntegral);
			$('#perfil_profesiografico').val(estEval.perfilProfesiografico);
			$('#eval_diagnostica').val(estEval.formasEvaluacion.diagnostica || []).trigger('change');
			$('#eval_formativa').val(estEval.formasEvaluacion.formativa || []).trigger('change');
			$('#eval_sumativa').val(estEval.formasEvaluacion.sumativa || []).trigger('change');

			// === 6. COMENTARIOS ===
			$("#seccionComentarios").html("");
			const comentarios = solicitud.comentarios || [];
			if (comentarios.length === 0) {
			  $("#seccionComentarios").html("<p class='text-muted'>No hay comentarios registrados.</p>");
			} else {
			  comentarios.forEach((comentario, i) => {
			    const html = `
			      <div class="card mb-3 shadow-sm border">
			        <div class="card-header d-flex justify-content-between align-items-center bg-light">
			          <strong class="text-primary">${comentario.usuario}</strong>
			          <span class="text-muted small"><strong>${comentario.fecha}</strong></span>
			        </div>
			        <div class="card-body">
			          ${comentario.comentario}
			        </div>
			      </div>
			    `;
			    $("#seccionComentarios").append(html);
			  });
			}

		} catch (e) {
			console.error("Error cargando la solicitud:", e);
		}
	};
	
	return{
		cssVistaCaptura:	cssVistaCaptura,
		cargaCatalogos:	cargaCatalogos,
		agregarRelacionLicAsig: agregarRelacionLicAsig,
		actualizarCamposExtra:	actualizarCamposExtra,
		validaCamposReqBiblio:	validaCamposReqBiblio,
		accionSolicitud:	accionSolicitud,
		cargaSolicitudAccion:	cargaSolicitudAccion
	}
}();