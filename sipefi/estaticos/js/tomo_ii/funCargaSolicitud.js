/**
 * fcs es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * En esta clase encontraremos la mayoria de las funciones principales del flujo completo del sistema SIPEFI-TOMO II
 * @module fcs
 */
const fcs = function(){
	
	//Variables globales
	const camposPorTipo = {
	    'LIBRO IMPRESO': {
	      labels: ['Editorial', 'Edición', '', ''],
	      requeridos: [true, false, false, false]
	    },
	    'ARTÍCULO IMPRESO': {
	      labels: ['Nombre de la Revista', 'Volumen(Número)', 'Páginas', 'DOI/URL'],
	      requeridos: [true, true, true, false]
	    },
	    'NORMA O LEY': {
	      labels: ['Edición/Revisión', 'Editorial/Organización', 'DOI/URL', 'Fecha precisa: Día y mes'],
	      requeridos: [false, true, true, false]
	    },
	    'APUNTES DE CLASE (MATERIAL DE CURSO)': {
	      labels: ['Tipo de Documento', 'Nombre de la Institución', 'URL/Enlace', 'Asignatura'],
	      requeridos: [true, true, false, false]
	    },
	    'MATERIAL AUDIOVISUAL DIGITAL': {
	      labels: ['Tipo de Contenido', 'Plataforma/Sitio Web', 'URL', 'Fecha precisa: Día y mes'],
	      requeridos: [true, true, true, false]
	    },
	    'LIBRO ELECTRÓNICO': {
	      labels: ['Editorial', 'Edición', 'DOI/URL', ''],
	      requeridos: [true, false, true, false]
	    },
	    'ARTÍCULO ELECTRÓNICO': {
	      labels: ['Nombre de la Revista', 'Volumen(Número)', 'Páginas', 'DOI/URL'],
	      requeridos: [true, true, true, true]
	    },
		'TESIS EN REPOSITORIO DIGITAL': {
	      labels: ['Grado de la tesis', 'Nombre de la institución', 'DOI/URL', ''],
	      requeridos: [true, true, true, false]
	    },
		'INFORME': {
	      labels: ['Serie o número de informe', 'Editorial/Organización', 'URL', ''],
	      requeridos: [true, true, true, false]
	    },
		'PÁGINA WEB': {
	      labels: ['Nombre del sitio web', 'URL', 'Fecha de Consulta: Día y mes', ''],
	      requeridos: [true, true, false, false]
	    },
	    'DEPENDERA DE LA TEMÁTICA A TRATAR': {
	      labels: ['', '', '', ''],
	      requeridos: [false, false, false, false]
	    },
	    'DEFAULT': {
	      labels: ['Campo extra 1', 'Campo extra 2', 'Campo extra 3', 'Campo extra 4'],
	      requeridos: [false, false, false, false]
	    }
	 };

	 let bibliografiaEnEdicion = null;
	 let bibliografiaVisible = '';
	 let listaBibliografias = [];
	 let listaRelacionesLicenciaturas = [];
	 let relacionesVisible = '';
	 let solicitudListaParaGuardar = false;

	 const textoSeguro = (valor) => $('<div>').text(valor == null ? '' : String(valor)).html();

	 const normalizarBibliografia = (bib = {}) => ({
		id: Number(bib.id) || 0,
		idTipo: Number(bib.idTipo) || null,
		tipo: bib.tipo || '',
		autor: bib.autor || '',
		anio: (bib.anio == null || bib.anio === 0 || bib.anio === '0') ? '' : String(bib.anio),
		clasifBiblio: Number(bib.clasifBiblio) === 1 ? 1 : 0,
		titulo: bib.titulo || '',
		extra1: bib.extra1 || '',
		extra2: bib.extra2 || '',
		extra3: bib.extra3 || '',
		extra4: bib.extra4 || '',
		temas: bib.temas || ''
	 });

	 const clonarBibliografia = (bib) => ({ ...normalizarBibliografia(bib) });

	 const accionesBibliografia = (bib, visible = '', editando = false) => `
		<div class="acciones-biblio" data-biblio-id="${bib.id}" ${visible}>
			<button class="btn btn-sm btn-danger btn-eliminar-biblio" type="button" data-biblio-id="${bib.id}" ${editando ? 'disabled' : ''}>
				<i class="fas fa-trash-alt"></i>
			</button>
			<button type="button" class="btn btn-sm btn-danger" onclick="etii.editarBibliografia(${bib.id})" ${editando ? 'hidden' : ''}>
				<i class="fas fa-edit"></i>
			</button>
			<button type="button" class="btn btn-sm btn-danger" onclick="etii.saveBibliografia(${bib.id})" ${editando ? '' : 'hidden'}>
				<i class="fas fa-save"></i>
			</button>
		</div>`;

	 const datosFilaBibliografia = (bib, visible = '', editando = false) => {
		const b = normalizarBibliografia(bib);
		if (!editando) {
			return [
				textoSeguro(b.tipo), textoSeguro(b.autor), textoSeguro(b.anio),
				b.clasifBiblio === 1 ? 'Complementaria' : 'Básica',
				textoSeguro(b.titulo), textoSeguro(b.extra1), textoSeguro(b.extra2),
				textoSeguro(b.extra3), textoSeguro(b.extra4), textoSeguro(b.temas),
				accionesBibliografia(b, visible, false)
			];
		}

		const depende = String(b.tipo).trim().toUpperCase() === 'DEPENDERA DE LA TEMÁTICA A TRATAR';
		const input = (campo, valor) => `<input type="text" class="form-control" id="id-biblio-${campo}-${b.id}" value="${textoSeguro(valor)}">`;
		const textoOInput = (campo, valor) => depende ? textoSeguro(valor) : input(campo, valor);
		const clasificacion = `<select id="id-biblio-clasificacion-${b.id}" class="form-select">
			<option value="0" ${b.clasifBiblio === 0 ? 'selected' : ''}>Básica</option>
			<option value="1" ${b.clasifBiblio === 1 ? 'selected' : ''}>Complementaria</option>
		</select>`;

		return [
			textoSeguro(b.tipo), textoOInput('autor', b.autor), textoOInput('year', b.anio),
			clasificacion, textoOInput('titulo', b.titulo), textoOInput('extra1', b.extra1),
			textoOInput('extra2', b.extra2), textoOInput('extra3', b.extra3), textoOInput('extra4', b.extra4),
			input('temas', b.temas), accionesBibliografia(b, visible, true)
		];
	 };

	 const renderizarBibliografias = () => {
		if (!$.fn.DataTable.isDataTable('#tablaBibliografia')) return;
		const tabla = $('#tablaBibliografia').DataTable();
		const filas = listaBibliografias
			.slice()
			.sort((a, b) => Number(a.id) - Number(b.id))
			.map(bib => datosFilaBibliografia(
				bib,
				bibliografiaVisible,
				Number(bibliografiaEnEdicion) === Number(bib.id)
			));

		tabla.clear();
		if (filas.length) tabla.rows.add(filas);
		tabla.draw(false);
	 };

	 const siguienteIdBibliografia = () => listaBibliografias.reduce(
		(maximo, bib) => Math.max(maximo, Number(bib.id) || 0),
		0
	 ) + 1;

	 const agregarFilaBibliografia = (bib, visible = '', dibujar = true) => {
		bibliografiaVisible = visible;
		listaBibliografias.push(normalizarBibliografia(bib));
		if (dibujar) renderizarBibliografias();
	 };

	 const cargarBibliografias = (bibliografias, visible = '') => {
		bibliografiaVisible = visible;
		bibliografiaEnEdicion = null;

		const idsUsados = new Set();
		let siguienteId = 1;
		listaBibliografias = (Array.isArray(bibliografias) ? bibliografias : [])
			.map(normalizarBibliografia)
			.map(bibliografia => {
				let id = Number(bibliografia.id) || 0;
				if (id <= 0 || idsUsados.has(id)) {
					while (idsUsados.has(siguienteId)) siguienteId += 1;
					id = siguienteId;
				}
				idsUsados.add(id);
				siguienteId = Math.max(siguienteId, id + 1);
				return { ...bibliografia, id };
			})
			.sort((a, b) => a.id - b.id);
		renderizarBibliografias();
	 };

	 const eliminarBibliografia = (idBibliografia) => {
		if (bibliografiaEnEdicion !== null) return false;
		listaBibliografias = listaBibliografias.filter(
			bib => Number(bib.id) !== Number(idBibliografia)
		);
		renderizarBibliografias();
		return true;
	 };

	 // --- Estilo para resaltar select2 inválidos (una sola vez) ---
	 (function ensureSelect2InvalidStyle() {
	   const styleId = "select2-invalid-style";
	   if (!document.getElementById(styleId)) {
	     const css = `
	       .select2-container .select2-selection.is-invalid {
	         border-color: #dc3545 !important;
	         box-shadow: 0 0 0 .25rem rgba(220,53,69,.25);
	       }`;
	     const s = document.createElement('style');
	     s.id = styleId; 
	     s.textContent = css;
	     document.head.appendChild(s);
	   }
	 })();
	
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

	const reiniciarFormularioNuevaSolicitud = () => {
		$('#numSolicitud').text('xxxx');
		$('#estatusSoli').text('Elaboración');
		$('#idES').text('1');
		$('#usuarioSol').text($('#usuario').text());

		[
			'#asignatura', '#clave_asignatura', '#creditos', '#h_sem_teo', '#h_sem_pra',
			'#h_semestre_teo', '#h_semestre_pra', '#objetivo', '#horasPracticasTemario',
			'#formacion_integral', '#perfil_profesiografico', '#nombreTema', '#horasTema',
			'#objetivoTema', '#contenidoTema', '#autor_biblio', '#anio_biblio',
			'#titulo_biblio', '#extra_1', '#extra_2', '#extra_3', '#extra_4', '#temas_biblio'
		].forEach(selector => $(selector).val('').removeClass('is-invalid is-readonly'));

		// Restablecer controles que pudieron quedar bloqueados al visualizar otra solicitud.
		$('body').find('input:not([type="hidden"]), textarea').prop('readonly', false).removeClass('is-readonly');
		$('body').find('select').prop('disabled', false);
		[
			'#btnAgregarRelLicAsig', '#btnAgregarTema',
			'#btnAgregarContenido', '#btnAgregarBibliografia'
		].forEach(selector => $(selector).removeClass('d-none').prop('disabled', false));

		$('#seccionComentarios').empty();
		$('#comentarios').find('.Editor-editor').html('');
	};

	const reiniciarSelectsNuevaSolicitud = () => {
		$('#modalidad, #tipo_modalidad, #tipo_bibliografia, #clasificacion_biblio')
			.val('0').trigger('change');
		$('#valor_practico, #rel_semestre, #ser_anterior, #ser_consecuente, ' +
		  '#estrategias_didacticas, #eval_diagnostica, #eval_formativa, #eval_sumativa')
			.val(null).trigger('change');
		$('#rel_licenciatura, #rel_area_con, #rel_caracter').val('0').trigger('change');
	};

	/**
	 * Funcion que carga los catalogos iniciales y necesarios en elementos Select para ser usados en el flujo de carga de una solicitud 
	 * @param {int} opc Parametro que tiene el tipo de visualizacion de la solicitud (nueva, edicion, visualizacion)
	 * @param {Object} param Parametro que tiene el objeto con la informacion de la solicitud que se esta editando o visualizando.
	 * @return {void} 
	 * @method cargaCatalogos
	 * @static
	 */
	const cargaCatalogos = (opc, param = {}) => {
		solicitudListaParaGuardar = false;
		try{
			if (Number(opc) === 1) reiniciarFormularioNuevaSolicitud();
			soltii.cargaMenuLlenadoBotones();
			// Inicializa DataTables y reinicia estructuras dinámicas para evitar datos residuales.
			fl.cargaTablasSolicitud();
			if (typeof etii !== 'undefined' && etii.reiniciarTemarioContenido) etii.reiniciarTemarioContenido();
			cargarRelacionesLicenciaturas([], '');
			cargarBibliografias([], '');
			let obj = fComun.getVarLocalJ("catalogos") || {};
			// Cargar combos del tab "Datos generales"
			llenaCombo("modalidad", obj.catModalidad || [], false);
			llenaCombo("tipo_modalidad", obj.catTipoMod || [], false);
			llenaCombo("valor_practico", obj.catValPract || [], false);
			$('#valor_practico').select2({
			    placeholder: "Elige una opción",
			    width: '100%'
			});

			// Cargar combos del tab "Relación con Licenciaturas"
			llenaCombo("rel_licenciatura", obj.catLic || [], false);
			llenaCombo("rel_area_con", obj.catAreaCon || [], false);
			llenaCombo("rel_caracter", obj.catCarAsig || [], false);
			
			// Dejamos por default la opción 0
			$('#rel_licenciatura').val('0').trigger('change');
			$('#rel_area_con').val('0').trigger('change');
			$('#rel_caracter').val('0').trigger('change');
			
			//Semestre multiple
			llenaCombo("rel_semestre", [...Array(10).keys()].map(i => [i + 1, `Semestre ${i + 1}`]), false); // del 1 al 10
			$('#rel_semestre').select2({
			    placeholder: "Selecciona uno o más semestres",
			    width: '100%'
			});
			// seriación antecedente y consecuente (múltiple)
			$('#ser_anterior').select2({
			    placeholder: "Selecciona una o más seriaciones",
			    width: '100%'
			});
			$('#ser_consecuente').select2({
			    placeholder: "Selecciona una o más seriaciones",
			    width: '100%'
			});

			const asignaturaRequest = param.info?.split('#@@#')[2] || null;
			const thisAsignatura = (asignaturaRequest !==null )? asignaturaRequest: "" ;

			llenaCombo("ser_anterior", (obj.catAsig || []).filter(([index, dato]) => dato !== thisAsignatura), false);
			llenaCombo("ser_consecuente", (obj.catAsig || []).filter(([index, dato]) => dato !== thisAsignatura), false);

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

			if (Number(opc) === 1) {
				reiniciarSelectsNuevaSolicitud();
				solicitudListaParaGuardar = true;
			}
		}catch(e){
			solicitudListaParaGuardar = false;
			console.error("Error al cargar catálogos:", e);
		}
		cssVistaCaptura();
		//Desbloqueamos el campo asignatura, por si es nueva solicitud
		$("#asignatura").prop("readonly", false);
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
	
	const nombreCatalogo = (catalogo, id, fallback = '') => {
		const encontrado = (catalogo || []).find(([valor]) => Number(valor) === Number(id));
		return encontrado ? encontrado[1] : fallback;
	};

	const listaNumerica = (valor) => {
		const entrada = Array.isArray(valor) ? valor : (valor == null || valor === '' ? [] : [valor]);
		return [...new Set(entrada
			.map(Number)
			.filter(numero => Number.isFinite(numero) && numero > 0))];
	};

	const normalizarRelacion = (relacion = {}) => {
		const catalogos = fComun.getVarLocalJ('catalogos') || {};
		const idLicenciatura = Number(relacion.idLicenciatura ?? relacion.idLic) || 0;
		const idAreaConocimiento = Number(relacion.idAreaConocimiento) || 0;
		const idCaracterAsignatura = Number(relacion.idCaracterAsignatura) || 0;

		return {
			idLicenciatura,
			licenciatura: relacion.licenciatura || nombreCatalogo(catalogos.catLic, idLicenciatura),
			idAreaConocimiento,
			areaConocimiento: relacion.areaConocimiento || nombreCatalogo(catalogos.catAreaCon, idAreaConocimiento),
			idCaracterAsignatura,
			caracterAsignatura: relacion.caracterAsignatura || nombreCatalogo(catalogos.catCarAsig, idCaracterAsignatura),
			semestres: listaNumerica(relacion.semestres ?? relacion.semestre),
			idSeriacionAnterior: listaNumerica(relacion.idSeriacionAnterior ?? relacion.seriacionAnt),
			idSeriacionConsecuente: listaNumerica(relacion.idSeriacionConsecuente ?? relacion.seriacionCons)
		};
	};

	const claveRelacion = (relacion) => [
		Number(relacion.idLicenciatura) || 0,
		Number(relacion.idAreaConocimiento) || 0,
		Number(relacion.idCaracterAsignatura) || 0
	].join('|');

	const renderizarRelacionesLicenciaturas = (visible = relacionesVisible) => {
		if (!$.fn.DataTable.isDataTable('#tablaRelacionesLic')) return;
		const tabla = $('#tablaRelacionesLic').DataTable();
		const catalogos = fComun.getVarLocalJ('catalogos') || {};
		const textoAsig = (id) => nombreCatalogo(catalogos.catAsig, id, String(id));
		const idSolicitud = Number($('#numSolicitud').html()) || 0;
		const idPerfil = Number($('#rol').html()) || 0;
		const idEstatus = Number($('#idES').html()) || 0;
		const ocultarPdf = (!idSolicitud || idEstatus === 0) ? 'hidden' : '';

		const filas = listaRelacionesLicenciaturas.map(relacion => {
			const rel = normalizarRelacion(relacion);
			const clave = encodeURIComponent(claveRelacion(rel));
			const acciones = `<div>
				<button type="button" class="btn btn-sm btn-danger btnEliminarRelacion" data-rel-key="${clave}" ${visible}>
					<i class="fas fa-trash-alt"></i>
				</button>
				<button type="button" class="btn btn-sm btn-danger" onclick="etii.descargaPdf(${idPerfil}, ${rel.idLicenciatura}, ${idSolicitud})" ${ocultarPdf}>
					<i class="fas fa-file-pdf"></i>
				</button>
			</div>`;

			return [
				textoSeguro(rel.licenciatura),
				textoSeguro(rel.areaConocimiento),
				textoSeguro(rel.caracterAsignatura),
				rel.semestres.join(' | '),
				rel.idSeriacionAnterior.map(textoAsig).join(' | '),
				rel.idSeriacionConsecuente.map(textoAsig).join(' | '),
				acciones
			];
		});

		tabla.clear();
		if (filas.length) tabla.rows.add(filas);
		tabla.draw(false);
	};

	const agregarFilaRelacion = (relacion, visible = '', dibujar = true) => {
		relacionesVisible = visible;
		listaRelacionesLicenciaturas.push(normalizarRelacion(relacion));
		if (dibujar) renderizarRelacionesLicenciaturas(visible);
	};

	const cargarRelacionesLicenciaturas = (relaciones, visible = '') => {
		relacionesVisible = visible;
		const agrupadas = new Map();

		(Array.isArray(relaciones) ? relaciones : []).forEach(relacionEntrada => {
			const relacion = normalizarRelacion(relacionEntrada);
			const clave = claveRelacion(relacion);
			if (!agrupadas.has(clave)) {
				agrupadas.set(clave, relacion);
				return;
			}

			const actual = agrupadas.get(clave);
			actual.semestres = listaNumerica([...actual.semestres, ...relacion.semestres]);
			actual.idSeriacionAnterior = listaNumerica([
				...actual.idSeriacionAnterior, ...relacion.idSeriacionAnterior
			]);
			actual.idSeriacionConsecuente = listaNumerica([
				...actual.idSeriacionConsecuente, ...relacion.idSeriacionConsecuente
			]);
		});

		listaRelacionesLicenciaturas = Array.from(agrupadas.values());
		renderizarRelacionesLicenciaturas(visible);
	};

	const eliminarRelacionLicenciatura = (claveCodificada) => {
		const clave = decodeURIComponent(String(claveCodificada || ''));
		listaRelacionesLicenciaturas = listaRelacionesLicenciaturas.filter(
			relacion => claveRelacion(relacion) !== clave
		);
		renderizarRelacionesLicenciaturas();
	};

	/**
	 * Función que agrega una nueva relación con licenciatura si es válida, no duplicada y usa DataTables.
	 * @function agregarRelacionLicAsig
	 */
	const agregarRelacionLicAsig = () => {
	  const idLic = $("#rel_licenciatura").val();
	  const txtLic = $("#rel_licenciatura option:selected").text().trim();

	  const idAreaCon = $("#rel_area_con").val();
	  const txtAreaCon = $("#rel_area_con option:selected").text().trim();

	  const idCaracter = $("#rel_caracter").val();
	  const txtCaracter = $("#rel_caracter option:selected").text().trim();

	  const idSolicitud = $("#numSolicitud").html();
	  const idPerfil = $("#rol").html();
	  const idEstatusSolicitud = parseInt($("#idES").html(), 10) || 0;

	  const isVisible = parseInt(fComun.getVarLocalS("accionSoli"));
	  let visible = (isVisible === 1) ? "hidden" : "";

	  let semestres = $("#rel_semestre").val() || [];
	  let serAnt = $("#ser_anterior").val() || [];
	  let serCon = $("#ser_consecuente").val() || [];

	  semestres = semestres.filter(val => val !== "0");
	  serAnt = serAnt.filter(val => val !== "0");
	  serCon = serCon.filter(val => val !== "0");


	  if (!idLic || idLic === "0") {
	    fComun.mostrarTooltipCampo("#rel_licenciatura", "Selecciona una licenciatura válida");
	    return;
	  }

	  if (!idAreaCon || idAreaCon === "0") {
	    fComun.mostrarTooltipCampo("#rel_area_con", "Selecciona un área de conocimiento válida");
	    return;
	  }

	  if (!idCaracter || idCaracter === "0") {
	    fComun.mostrarTooltipCampo("#rel_caracter", "Selecciona un carácter válido");
	    return;
	  }

	  if (!semestres.length) {
	    fComun.mostrarTooltipCampo("#rel_semestre", "Selecciona al menos un semestre");
	    return;
	  }

	  const interseccion = serAnt.some(val => serCon.includes(val));
	  if (interseccion) {
	    fComun.mostrarTooltipCampo("#ser_consecuente", "No puede haber materias repetidas en seriación antecedente y subsecuente");
	    return;
	  }

	  const claveNueva = [Number(idLic), Number(idAreaCon), Number(idCaracter)].join('|');
	  const existe = listaRelacionesLicenciaturas.some(
	    relacion => claveRelacion(relacion) === claveNueva
	  );

	  if (existe) {
	    fComun.mostrarTooltipCampo("#rel_licenciatura", "Ya existe esa relación con la misma área y carácter.");
	    return;
	  }

	  agregarFilaRelacion({
		idLicenciatura: Number(idLic), licenciatura: txtLic,
		idAreaConocimiento: Number(idAreaCon), areaConocimiento: txtAreaCon,
		idCaracterAsignatura: Number(idCaracter), caracterAsignatura: txtCaracter,
		semestres: semestres.map(Number),
		idSeriacionAnterior: serAnt.map(Number), idSeriacionConsecuente: serCon.map(Number)
	  }, visible);

	  $("#rel_licenciatura").val("0").trigger("change");
	  $("#rel_area_con").val("0").trigger("change");
	  $("#rel_caracter").val("0").trigger("change");
	  $("#rel_semestre").val(null).trigger("change");
	  $("#ser_anterior").val(null).trigger("change");
	  $("#ser_consecuente").val(null).trigger("change");
	};
	
	/**
	 * Función que actualiza dinámicamente los textos de los campos adicionales
	 * y marca visualmente si son requeridos, según el tipo de bibliografía seleccionado.
	 */
	const actualizarCamposExtra = () => {
	  const tipo = $('#tipo_bibliografia option:selected').text().trim().toUpperCase();
	  const idTipo = $('#tipo_bibliografia').val();
	  const config = camposPorTipo[tipo] || camposPorTipo['DEFAULT'];
	  const labels = config.labels;
	  const requeridos = config.requeridos;

	  // Ocultar/deshabilitar campos principales si es tipo 11
	  if (idTipo === '11') {
		$('#autor_biblio').prop('disabled', true).closest('.col-md-5').hide();
		$('#anio_biblio').prop('disabled', true).closest('.col-md-2').hide();
		$('#titulo_biblio').prop('disabled', true).closest('.col-md-8').hide();
		$('#lbl_autor').closest('.col-md-5').hide();
		$('#lbl_anio').closest('.col-md-2').hide();
		$('#lbl_titulo').closest('.col-md-8').hide();
	  } else {
		$('#autor_biblio').prop('disabled', false).closest('.col-md-5').show();
		$('#anio_biblio').prop('disabled', false).closest('.col-md-2').show();
		$('#titulo_biblio').prop('disabled', false).closest('.col-md-8').show();
		$('#lbl_autor').closest('.col-md-5').show();
		$('#lbl_anio').closest('.col-md-2').show();
		$('#lbl_titulo').closest('.col-md-8').show();
	  }

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

		// Only validate required fields if not tipo 11
		if (idTipo !== '11') {
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

		const idBibliografia = siguienteIdBibliografia();
		agregarFilaBibliografia({
			id: idBibliografia, idTipo: Number(idTipo), tipo: tipoTextoOrig, autor, anio,
			clasifBiblio: Number(clasif), titulo, extra1, extra2, extra3, extra4, temas
		});

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
	const obtenerBibliografia = () => listaBibliografias
		.slice()
		.sort((a, b) => Number(a.id) - Number(b.id))
		.map(clonarBibliografia);
	
	/**
	 * Función que recorre la tabla de relación con licenciaturas para extraer
	 * los datos seleccionados por el usuario.
	 * 
	 * Cada fila contiene: licenciatura, area conocimiento, caracter, semestre, seriación antecedente y consecuente.
	 *
	 * @function obtenerRelLicAsig
	 * @returns {Array<Object>} Arreglo con objetos que representan la relación con licenciaturas.
	 */
	const obtenerRelLicAsig = () => listaRelacionesLicenciaturas.map(relacion => {
		const rel = normalizarRelacion(relacion);
		return {
			idLicenciatura: rel.idLicenciatura,
			licenciatura: rel.licenciatura,
			idAreaConocimiento: rel.idAreaConocimiento,
			areaConocimiento: rel.areaConocimiento,
			idCaracterAsignatura: rel.idCaracterAsignatura,
			caracterAsignatura: rel.caracterAsignatura,
			semestres: [...rel.semestres],
			idSeriacionAnterior: [...rel.idSeriacionAnterior],
			idSeriacionConsecuente: [...rel.idSeriacionConsecuente]
		};
	});

	/**
	 * Función que obtiene la información capturada en las tablas de Temario y Contenido.
	 * La tabla de Temas contiene número, nombre, horas y objetivo.
	 * La tabla de Contenido contiene el número del subtema, la relación con el tema y la descripción.
	 * 
	 * @function obtenerTemarioYContenido
	 * @returns {Object} Objeto con dos arreglos: `temas` y `contenidos`.
	 */
	const obtenerTemarioYContenido = () => {
		return (typeof etii !== 'undefined' && etii.obtenerTemarioContenido)
			? etii.obtenerTemarioContenido()
			: { temas: [], contenidos: [] };
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
		if (!solicitudListaParaGuardar) {
			return fComun.mostrarModalAdvertencia(
				'La solicitud todavía no termina de cargar. Actualiza la pantalla y vuelve a intentarlo.'
			);
		}

		if (typeof etii !== 'undefined' && etii.hayEdicionPendiente && etii.hayEdicionPendiente()) {
			return fComun.mostrarModalAdvertencia('Guarda primero la edición abierta en temas, contenidos o bibliografía antes de continuar.');
		}

		if (!String($('#asignatura').val() ?? '').trim()) {
			return fComun.mostrarTooltipCampo('#asignatura', 'Captura el nombre de la asignatura antes de guardar.');
		}

		objSolicitud = construirSolicitud();
		let modalAprob = "#modalAprobSoliEstatus";
		objSolicitud["accionSoli"] = accion;
		const idEstSolicitud = $("#idES").html();
		
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
						//Bloqueamos el campo asignatura, ya no se puede modificar
						$("#asignatura").prop("readonly", true);
					}else if(accion == 2){ //Se proceso correctamente estatus solicitud
						let msjConfirm = "La aprobaci&oacute;n de la solicitud se ha realizado correctamente.";
						let estatus = objSolicitud["idEstSoli"];
						msjConfirm = (idEstSolicitud == 1)?"La solicitud ha sido enviada correctamente para su aprobaci&oacute;n.":msjConfirm;
						$(modalAprob+" .textoBody").html(msjConfirm);
						fComun.mostrarModal(modalAprob);
						etii.eventoAprobSoli(".cierraModalAprob",modalAprob);
					}else if(accion == 3){ //Se rechazo correctamente la solicitud
						let msjConfirm = "La solicitud ha sido rechazada correctamente.";
						$(modalAprob+" .textoBody").html(msjConfirm);
						fComun.mostrarModal(modalAprob);
						etii.eventoAprobSoli(".cierraModalAprob",modalAprob);
					}
				}else{
					let palabra = (accion==1)?"guardado":(accion==2)?"procesamiento":"rechazo";
					if([400, 401, 403, 409].includes(Number(obj.estatus || obj.code))){
						texto = "No fue posible realizar el "+palabra+" de la solicitud <br>" +
								(obj.error || "La acción no está permitida.");
					}else{
						texto = "No fue posible realizar el "+palabra+" de la solicitud <br>" +
								"Contacta al área de soporte SIPEFI <br>" +
								"<strong><a href=\"mailto:sipefi@fi.unam.edu?subject=Necesito%20ayuda\">" +
									"sipefi@fi.unam.edu" +
								"</a></strong>";
					}
					
					if(obj.referencia){
						texto += "<br><small>Referencia de soporte: <strong>" + obj.referencia + "</strong></small>";
					}
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
	  const temarioContenido = obtenerTemarioYContenido();
	  return {
		datosGenerales: {
		  modalidad: $('#modalidad').val(),
		  tipoModalidad: $('#tipo_modalidad').val(),
		  valorPractico: $('#valor_practico').val() || [],
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
	    temario: temarioContenido.temas,
		actPracticas: $('#horasPracticasTemario').val(),
	    contenido: temarioContenido.contenidos,
	    bibliografia: obtenerBibliografia(),
	    estrategiasEvaluacion: {
	      estrategiasDidacticas: $('#estrategias_didacticas').val() || [],
	      formasEvaluacion: {
	        diagnostica: $('#eval_diagnostica').val() || [],
	        formativa: $('#eval_formativa').val() || [],
	        sumativa: $('#eval_sumativa').val() || []
	      },
	      formacionIntegral: $('#formacion_integral').val(),
	      perfilProfesiografico: $('#perfil_profesiografico').val()
	    },
	    metadatos: {
	      usuario: $("#usuario").html(),
	      rol: $("#rol").html(),
	      numSolicitud: $("#numSolicitud").html(),
	      accionGA: ($.isNumeric($("#numSolicitud").html()) ? 2 : 1),
	      idEstSoli: $("#idES").html(),
	      usuarioSoli: $("#usuarioSol").html(),
	      comentarios: $("#comentarios").Editor("getText"),
	      cargaCompleta: solicitudListaParaGuardar
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

	    fComun.mostrarModal(modal);
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
		solicitudListaParaGuardar = false;
		let accion = Number(solicitud.accion);
		fComun.guardaVarLocalS("accionSoli",accion);
		fComun.guardaVarLocal("objSoli",solicitud);
		//Solicitud existente
		$("#numSolicitud").html(solicitud.numSolicitud);
		$("#estatusSoli").html(solicitud.nomEstSoli);
		$("#idES").html(solicitud.idEstSoli);
		$("#usuarioSol").html(solicitud.usuarioSoli);
		let visible = '';

		validarBotonesCambioEstatus(1);
		if(accion == 2){ // 2-Editar

			$('.menuBotones[target="guardarSolicitud"]').show();
			$('.menuBotones[target="#modalComentarios"]').show();
		}else if(accion == 1){ // Visualizar
			visible = 'hidden';
			$('.menuBotones[target="guardarSolicitud"]').hide();
			//Ponemos campos como visualizacion
			//Inputs de texto / números / fechas / etc. → readonly
			$('body').find('input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="file"])')
			        .prop('readonly', true)
			        .toggleClass('is-readonly', true);

			// Textareas → readonly
			$('body').find('textarea')
			        .prop('readonly', true)
			        .toggleClass('is-readonly', true);

			// Selects → disabled
			$('body').find('select').prop('disabled', true);

			// Select2
			$('body').find('select.select2').prop('disabled', true).trigger('change.select2');

			//Ocultamos los botones de “agregar”
			const btnsOcultar = [
				'#btnAgregarRelLicAsig',
			    '#btnAgregarTema',
			    '#btnAgregarContenido',
			    '#btnAgregarBibliografia'
			];
			btnsOcultar.forEach(sel => $(sel).toggleClass('d-none', true));
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
			const dg = solicitud.datosGenerales || {};
			$('#asignatura').val(dg.asignatura ?? '');
			$('#clave_asignatura').val(dg.claveAsignatura ?? '');
			$('#creditos').val(dg.creditos ?? '');
			$('#modalidad').val(dg.modalidad ?? '');
			$('#tipo_modalidad').val(dg.tipoModalidad ?? '');
			$("#valor_practico").val(Array.isArray(solicitud.valorPractico) ? solicitud.valorPractico : []).trigger("change");
			$('#h_sem_teo').val(dg.hSemTeoria ?? '');
			$('#h_sem_pra').val(dg.hSemPractica ?? '');
			$('#h_semestre_teo').val(dg.hSemestreTeoria ?? '');
			$('#h_semestre_pra').val(dg.hSemestrePractica ?? '');
			$('#objetivo').val(dg.objAsig ?? '');

			if(dg.tipoModalidad !== 1 && accion == 2){
				$("#valor_practico").prop("disabled", false);
			}

			// === 2. RELACIÓN CON LICENCIATURAS ===
			cargarRelacionesLicenciaturas(solicitud.relacionLicenciaturas || [], visible);

			// === 3. TEMARIO Y CONTENIDO ===
			$('#horasPracticasTemario').val(solicitud.actPracticas ?? '');
			etii.cargarTemarioContenido(solicitud.temario || [], solicitud.contenido || []);

			// === 4. BIBLIOGRAFÍA ===
			const catTipoBib = fComun.getVarLocalJ('catalogos')?.catTipoBib || [];
			const bibliografias = (solicitud.bibliografia || []).map(b => ({
				...b,
				tipo: catTipoBib.find(([id]) => Number(id) === Number(b.idTipo))?.[1] || 'Tipo desconocido'
			}));
			cargarBibliografias(bibliografias, visible);

			// === 5. ESTRATEGIAS Y EVALUACIÓN ===
			const estEval = solicitud.estrategiasEvaluacion || {};
			const formasEvaluacion = estEval.formasEvaluacion || {};
			$('#estrategias_didacticas').val(Array.isArray(estEval.estrategiasDidacticas) ? estEval.estrategiasDidacticas : []).trigger('change');
			$('#formacion_integral').val(estEval.formacionIntegral ?? '');
			$('#perfil_profesiografico').val(estEval.perfilProfesiografico ?? '');
			$('#eval_diagnostica').val(Array.isArray(formasEvaluacion.diagnostica) ? formasEvaluacion.diagnostica : []).trigger('change');
			$('#eval_formativa').val(Array.isArray(formasEvaluacion.formativa) ? formasEvaluacion.formativa : []).trigger('change');
			$('#eval_sumativa').val(Array.isArray(formasEvaluacion.sumativa) ? formasEvaluacion.sumativa : []).trigger('change');

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
			
			//Bloqueamos el campo asignatura, ya no se puede modificar
			$("#asignatura").prop("readonly", true);
			solicitudListaParaGuardar = true;

		} catch (e) {
			solicitudListaParaGuardar = false;
			console.error("Error cargando la solicitud:", e);
			fComun.mostrarModalAdvertencia(
				'No fue posible reconstruir completamente la solicitud. Actualiza la pantalla antes de guardar.'
			);
		}
	};
	
	/**
	 * Funcion que se encarga de presentar un modal de alerta, para asegurar la accion solicitada de rechazo de la solicitud.
	 * @return {void}
	 * @method modalRechazoSoli
	 * @static
	 */
	const modalRechazoSoli = () => {
		$("#modalAlerta .textoBody").html("" +
				"Se procede a realizar el <strong>rechazo</strong> de la <br>" +
				"solicitud <strong>" + $("#numSolicitud").html() + "</strong> con estatus <strong>" + $("#estatusSoli").html() + "</strong>."+ 
				"<br><br>" +
				"<center>"+
					"<strong>&#191;Confirmas la petici&oacute;n&#63;</strong>" +
				"</center>"+
				"");
		$("#modalAlerta .modal-body .btn-secondary").attr('id','cerrarAlerta').html('Cancelar');
		$("#modalAlerta .modal-body .btn-warning").attr('id','rechazarSoli').html('<strong>Confirmar</strong>');
		fComun.mostrarModal('#modalAlerta');
		etii.eventoAlerta("#cerrarAlerta","#modalAlerta",0);
		etii.eventoAlerta("#rechazarSoli","#modalAlerta",1);
	};
	
	/**
	 * Funcion que realiza la validacion de la solicitud.
	 * @param {int} opc Parametro que indica si la solicitud debe ser procesada o solo se tiene que realizar la validacion.
	 * @return {void}
	 * @method validaSolicitud
	 * @static
	 */
	const validaSolicitud = (opc = 2) =>{
		const errs = [];
		const invalidEls = [];

		// Limpia marcas previas (inputs, selects, textareas y contenedores select2) de errores
		$('input, select, textarea').removeClass('is-invalid');
		$('.select2-selection').removeClass('is-invalid');

		const mark = (sel, msg) => { 
		  const $el = $(sel);
		  $el.addClass('is-invalid');
		  // Si es select2, marca su contenedor visual
		  if ($el.hasClass('select2-hidden-accessible') || $el.data('select2')) {
		    const $cont = $el.next('.select2').find('.select2-selection');
		    $cont.addClass('is-invalid');
		  }
		  errs.push(msg); 
		  invalidEls.push(sel); 
		};

		const valOf = (id) => ($(`#${id}`).val() ?? '').toString().trim();
		const numOf = (id) => {
		  const n = parseFloat(valOf(id).replace(',', '.'));
		  return Number.isFinite(n) ? n : NaN;
		};
		const checkText = (id, label) => { if (!valOf(id)) mark(`#${id}`, `Captura ${label}.`); };
		const checkNumberPos = (id, label) => {
		  const n = numOf(id);
		  if (!Number.isFinite(n) || n <= 0) mark(`#${id}`, `${label} debe ser un número > 0.`);
		  return n;
		};
		const checkSelect = (id, label) => {
		  const $el = $(`#${id}`);
		  const v = $el.val();
		  const isArray = Array.isArray(v);
		  const emptyArray = isArray && v.length === 0;
		  const onlyZeros = isArray && v.every(x => x === '0' || x === 0 || x === '' || x == null);
		  const emptyScalar = !isArray && (!v || v === '0');
		  if (emptyArray || onlyZeros || emptyScalar) mark(`#${id}`, `Selecciona ${label}.`);
		};
		
		const checkNumberNonNeg = (id, label) => {
		  const n = numOf(id);
		  if (!Number.isFinite(n) || n < 0) mark(`#${id}`, `${label} debe ser un número ≥ 0.`);
		  return n;
		};

		// Los datos canónicos se conservan fuera de DataTables.
		// DataTables es únicamente la capa de presentación y nunca la fuente de guardado/validación.
		const temarioContenidoActual = obtenerTemarioYContenido();
		const relacionesActuales = obtenerRelLicAsig();
		const bibliografiasActuales = obtenerBibliografia();

		// === Validamos campos input y select validados ===
		// Selects requeridos 
		[
		  ['modalidad', 'la modalidad'],
		  ['tipo_modalidad', ' el tipo de modalidad'],
		  ['estrategias_didacticas', 'al menos una estrategia didáctica'],
		  ['eval_diagnostica', 'la evaluación diagnóstica'],
		  ['eval_formativa', 'la evaluación formativa'],
		  ['eval_sumativa', 'la evaluación sumativa'],
		].forEach(([id, label]) => checkSelect(id, label));

		// Inputs / Textareas requeridos (formacion_integral es OPCIONAL)
		[
		  ['asignatura', 'el nombre de la asignatura'],
		  ['clave_asignatura', 'la clave de la asignatura'],
		  ['objetivo', 'el objetivo general'],
		  ['perfil_profesiografico', 'el perfil profesiográfico'],
		].forEach(([id, label]) => checkText(id, label));

		// Números requeridos
		const creditos         = checkNumberPos('creditos', 'los créditos');
		const hSemTeoSemana    = checkNumberNonNeg('h_sem_teo', 'las horas teóricas por semana');
		const hSemPraSemana    = checkNumberNonNeg('h_sem_pra', 'las horas prácticas por semana');
		const hSemTeoTotal     = checkNumberNonNeg('h_semestre_teo', 'las horas teóricas del semestre');
		const hSemPraTotal     = checkNumberNonNeg('h_semestre_pra', 'las horas prácticas del semestre');
		const horasPracTemario = checkNumberNonNeg('horasPracticasTemario', 'las horas prácticas del temario');

		// --- Reglas de coherencia horas prácticas ---
		// Si por semana NO hay prácticas, entonces semestre y temario deben ser 0.
		// Si por semana SÍ hay prácticas (>0), entonces semestre y temario deben ser >0.
		if (Number.isFinite(hSemPraSemana) && Number.isFinite(hSemPraTotal) && Number.isFinite(horasPracTemario)) {
		  if (hSemPraSemana === 0) {
		    if (hSemPraTotal !== 0) {
				mark('#h_semestre_pra', 'Si horas prácticas por semana = 0, las horas prácticas del semestre deben ser 0.');
		    }
			if (horasPracTemario !== 0) {
              mark('#horasPracticasTemario', 'Si horas prácticas por semana = 0, las horas de actividades prácticas deben ser 0.');
			}
		  } else if (hSemPraSemana > 0) {
		    if (!(hSemPraTotal > 0)) {
		      mark('#h_semestre_pra', 'Si hay horas prácticas por semana, debe haber horas prácticas del semestre (> 0).');
		    }
		  }
		}
		
		// --- Reglas de coherencia horas prácticas ---
		// Si por semana NO hay teoricas, entonces semestre ser 0.
		// Si por semana SÍ hay teoricas (>0), entonces semestre >0.
		if (Number.isFinite(hSemTeoSemana) && Number.isFinite(hSemTeoTotal)) {
		  if (hSemTeoSemana === 0) {
		    if (hSemTeoTotal !== 0) {
		      mark('#h_semestre_teo', 'Si horas teoricas por semana = 0, las horas teoricas del semestre deben ser 0.');
		    }
		  } else if (hSemTeoSemana > 0) {
		    if (!(hSemTeoTotal > 0)) {
		      mark('#h_semestre_teo', 'Si hay horas teoricas por semana, debe haber horas teoricas del semestre (> 0).');
		    }
		  }
		}
		
		// === Validamos secciones dinámicas con sus estructuras internas completas ===
		if (relacionesActuales.length < 1) mark('#tablaRelacionesLic', 'Agrega al menos una relación licenciatura–asignatura.');
		if (bibliografiasActuales.length < 1) mark('#tablaBibliografia', 'Agrega al menos una referencia bibliográfica.');
		if (temarioContenidoActual.temas.length < 1) mark('#tablaTemas', 'Agrega al menos un tema al temario.');
		if (temarioContenidoActual.contenidos.length < 1) mark('#tablaContenidos', 'Agrega al menos un contenido (para algún tema).');

		// === Validamos Horas del semestre desde el modelo interno, no desde celdas HTML ===
		const sumaHorasTemas = temarioContenidoActual.temas.reduce((total, tema) => {
		  const horas = parseFloat(String(tema.horas ?? '').replace(',', '.'));
		  return total + (Number.isFinite(horas) ? horas : 0);
		}, 0);

		const horasTotalesSemestre = hSemTeoTotal + hSemPraTotal;
		const esperado             = sumaHorasTemas + horasPracTemario;

		if (Number.isFinite(horasTotalesSemestre) && Number.isFinite(esperado)) {
		  if (Math.abs(horasTotalesSemestre - esperado) > 0.0001) {
		    $('#h_semestre_teo, #h_semestre_pra, #horasPracticasTemario, #tablaTemas').addClass('is-invalid');
		    $('.select2-selection[aria-labelledby="h_semestre_teo"], .select2-selection[aria-labelledby="h_semestre_pra"]').addClass('is-invalid');
		    errs.push(
		      `Las horas totales del semestre (${horasTotalesSemestre}) deben ser iguales a ` +
		      `Horas de temas (${sumaHorasTemas}) + Horas prácticas del temario (${horasPracTemario}).`
		    );
		  }
		}
		
		if (Number.isFinite(hSemTeoSemana) && Number.isFinite(hSemPraSemana)) {
		  if (hSemTeoSemana === 0 && hSemPraSemana === 0) {
		    mark('#h_sem_teo', 'Debe haber horas teóricas o prácticas por semana (> 0 en al menos una).');
		    mark('#h_sem_pra', 'Debe haber horas teóricas o prácticas por semana (> 0 en al menos una).');
		  }
		}

		// === Resultado: si hay errores, mostramos modal de errores ===
		if (errs.length) {
		  const txtH = "No se puede procesar la solicitud";
		  const body = `
		    <div class='form-group'>
		      <p>Corrige lo siguiente antes de continuar:</p>
		      <ul class="mb-0">
		        ${errs.map(e => `<li>${e}</li>`).join('')}
		      </ul>
		    </div>`;
		  fComun.mostrarModalAdvertencia(body, txtH);

		  // Enfoca el primer inválido y hace scroll
		  if (invalidEls.length) {
		    const $first = $(invalidEls[0]);
		    try { 
		      if ($first.data('select2')) { $first.select2('open'); }
		      else { $first.trigger('focus'); } 
		    } catch(e) {}
		    try {
		      $('html, body').animate({ scrollTop: Math.max(0, $first.offset().top - 120) }, 350);
		    } catch(e) {}
		  }
		  return;
		}

		// === si todo OK: procesar ===
		accionSolicitud(2);
	};
	
	/**
	 * Funcion que ayuda a cancelar una solicitud que ya no se requiere en el sistema SIPEFI
	 * @return {void}
	 * @method realizaCancelacionSolicitud
	 * @static
	 */
	const realizaCancelacionSolicitud = () => {
		let param = {
			numSoli: $("#numSolicitud").html(),
			estatus: $("#idES").html(),
			rol: $("#rol").html(),
			usuario: $("#usuario").html(),
			comentario: $("#razonCS").val()
		};
		fComun.post2("/SIPEFI/cancelarSolicitud/", param, function(resp){
			try{
				let obj = resp;
				if(obj.code == 200){
					let modalAprob = "#modalAprobSoliEstatus";
					let msjConfirm = "La solicitud ha sido cancelada correctamente.";
					$(modalAprob+" .textoBody").html(msjConfirm);
					fComun.mostrarModal(modalAprob);
					etii.eventoAprobSoli(".cierraModalAprob", modalAprob);
				}else{
					texto = "No fue posible realizar la cancelaci&oacute;n de la solicitud <br>" +
							"Contacta al área de soporte SIPEFI <br>" +
							"<strong><a href=\"mailto:sipefi@fi.unam.edu?subject=Necesito%20ayuda\">" +
								"sipefi@fi.unam.edu" +
							"</a></strong>";
					if(obj.code == 409 || obj.code == 403){
						texto = obj.error;
					}
					if(obj.referencia){
						texto += "<br><small>Referencia de soporte: <strong>" + obj.referencia + "</strong></small>";
					}
					mostrarModalGuardar(2,texto);
				}
			}catch(e){console.log(e)}
		});
	};
	
	const editarBibliografiaFila = (idBibliografia) => {
		if (bibliografiaEnEdicion !== null) return false;
		const existe = listaBibliografias.some(bib => Number(bib.id) === Number(idBibliografia));
		if (!existe) return false;
		bibliografiaEnEdicion = Number(idBibliografia);
		renderizarBibliografias();
		$('.menuBotones[target="guardarSolicitud"], .menuBotones[target="aprobarSolicitud"], .menuBotones[target="rechazarSolicitud"]').prop('disabled', true);
		return true;
	};

	const guardarBibliografiaFila = (idBibliografia) => {
		if (Number(bibliografiaEnEdicion) !== Number(idBibliografia)) return false;
		const indice = listaBibliografias.findIndex(bib => Number(bib.id) === Number(idBibliografia));
		if (indice < 0) return false;

		const bib = listaBibliografias[indice];
		const depende = String(bib.tipo).trim().toUpperCase() === 'DEPENDERA DE LA TEMÁTICA A TRATAR';
		const valor = (campo, actual) => (depende && campo !== 'temas')
			? actual
			: ($(`#id-biblio-${campo}-${bib.id}`).val() ?? '');

		listaBibliografias[indice] = normalizarBibliografia({
			...bib,
			autor: valor('autor', bib.autor),
			anio: valor('year', bib.anio),
			clasifBiblio: Number($(`#id-biblio-clasificacion-${bib.id}`).val()) === 1 ? 1 : 0,
			titulo: valor('titulo', bib.titulo),
			extra1: valor('extra1', bib.extra1),
			extra2: valor('extra2', bib.extra2),
			extra3: valor('extra3', bib.extra3),
			extra4: valor('extra4', bib.extra4),
			temas: valor('temas', bib.temas)
		});

		bibliografiaEnEdicion = null;
		renderizarBibliografias();
		$('.menuBotones[target="guardarSolicitud"], .menuBotones[target="aprobarSolicitud"], .menuBotones[target="rechazarSolicitud"]').prop('disabled', false);
		return true;
	};

	const hayBibliografiaEnEdicion = () => bibliografiaEnEdicion !== null;

	return{
		cssVistaCaptura:	cssVistaCaptura,
		cargaCatalogos:	cargaCatalogos,
		agregarRelacionLicAsig: agregarRelacionLicAsig,
		cargarRelacionesLicenciaturas: cargarRelacionesLicenciaturas,
		eliminarRelacionLicenciatura: eliminarRelacionLicenciatura,
		cargarBibliografias: cargarBibliografias,
		eliminarBibliografia: eliminarBibliografia,
		editarBibliografiaFila: editarBibliografiaFila,
		guardarBibliografiaFila: guardarBibliografiaFila,
		hayBibliografiaEnEdicion: hayBibliografiaEnEdicion,
		actualizarCamposExtra:	actualizarCamposExtra,
		validaCamposReqBiblio:	validaCamposReqBiblio,
		accionSolicitud:	accionSolicitud,
		cargaSolicitudAccion:	cargaSolicitudAccion,
		modalRechazoSoli:	modalRechazoSoli,
		validaSolicitud:	validaSolicitud,
		realizaCancelacionSolicitud:	realizaCancelacionSolicitud
	}
}();