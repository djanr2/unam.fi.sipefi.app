/**
 * etii es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos apoya con los eventos que se estaran usando en el front del sistema SIPEFI-TOMO II.
 * @module etii
 */

const etii = function(){
	
	let listaTemas = [];       // [{ id, nombre, horas, objetivo }]
	let listaContenidos = [];  // [{ id, idTema, texto }]
	let contadorTemas = 1;
	let contadorContenidos = 1;
	let temaEnEdicionId = null;
	let contenidoEnEdicionId = null;
	let isActionEditingBibliografia = false;

	const textoNormalizado = (valor) => valor == null ? '' : String(valor);
	const textoHtmlSeguro = (valor) => $('<div>').text(textoNormalizado(valor)).html();
	const numeroEntero = (valor, defecto = 0) => {
		const numero = Number.parseInt(valor, 10);
		return Number.isFinite(numero) ? numero : defecto;
	};

	const reiniciarTemarioContenido = (renderizar = true) => {
		listaTemas = [];
		listaContenidos = [];
		contadorTemas = 1;
		contadorContenidos = 1;
		temaEnEdicionId = null;
		contenidoEnEdicionId = null;
		isActionEditingBibliografia = false;

		if (renderizar &&
			$.fn.DataTable.isDataTable('#tablaTemas') &&
			$.fn.DataTable.isDataTable('#tablaContenidos')) {
			reconstruirDesdeEstructuras();
		}
	};

	const cargarTemarioContenido = (temario, contenidos) => {
		reiniciarTemarioContenido(false);
		const mapaNumeroAId = new Map();

		const temasEntrada = Array.isArray(temario) ? temario : [];
		temasEntrada
			.map((tema, indice) => ({ tema: tema && typeof tema === 'object' ? tema : {}, indice }))
			.sort((a, b) => numeroEntero(a.tema.numeroTema, a.indice + 1) - numeroEntero(b.tema.numeroTema, b.indice + 1))
			.forEach(({ tema, indice }) => {
				const numeroOriginal = numeroEntero(tema.numeroTema, indice + 1);
				const idInterno = contadorTemas++;
				if (!mapaNumeroAId.has(numeroOriginal)) mapaNumeroAId.set(numeroOriginal, idInterno);
				listaTemas.push({
					id: idInterno,
					nombre: textoNormalizado(tema.nombre),
					horas: textoNormalizado(tema.horas),
					objetivo: textoNormalizado(tema.objetivo)
				});
			});

		const contenidosEntrada = Array.isArray(contenidos) ? contenidos : [];
		contenidosEntrada
			.map((contenido, indice) => ({ contenido: contenido && typeof contenido === 'object' ? contenido : {}, indice }))
			.sort((a, b) => {
				const temaA = numeroEntero(a.contenido.temaRelacionado, 0);
				const temaB = numeroEntero(b.contenido.temaRelacionado, 0);
				if (temaA !== temaB) return temaA - temaB;
				const numeroA = numeroEntero(textoNormalizado(a.contenido.numeroCont).split('.')[1], a.indice + 1);
				const numeroB = numeroEntero(textoNormalizado(b.contenido.numeroCont).split('.')[1], b.indice + 1);
				return numeroA - numeroB;
			})
			.forEach(({ contenido }) => {
				const numeroTema = numeroEntero(contenido.temaRelacionado, 0);
				const idTema = mapaNumeroAId.get(numeroTema);
				if (!idTema) {
					console.warn('Contenido omitido porque no existe su tema relacionado.', contenido);
					return;
				}
				listaContenidos.push({
					id: contadorContenidos++,
					idTema,
					texto: textoNormalizado(contenido.contenido)
				});
			});

		reconstruirDesdeEstructuras();
	};

	const obtenerTemarioContenido = () => {
		const mapaIdNumero = {};
		const temas = listaTemas.map((tema, indice) => {
			const numero = indice + 1;
			mapaIdNumero[tema.id] = numero;
			return {
				numeroTema: numero,
				nombre: textoNormalizado(tema.nombre).trim(),
				horas: textoNormalizado(tema.horas).trim(),
				objetivo: textoNormalizado(tema.objetivo).trim()
			};
		});

		const contadores = {};
		const contenidosSalida = [];
		listaContenidos.forEach(contenido => {
			const numeroTema = mapaIdNumero[contenido.idTema];
			if (!numeroTema) return;
			contadores[contenido.idTema] = (contadores[contenido.idTema] || 0) + 1;
			contenidosSalida.push({
				temaRelacionado: String(numeroTema),
				numeroCont: `${numeroTema}.${contadores[contenido.idTema]}`,
				contenido: textoNormalizado(contenido.texto).trim()
			});
		});

		return { temas, contenidos: contenidosSalida };
	};

	const hayEdicionPendiente = () => Boolean(
		temaEnEdicionId !== null ||
		contenidoEnEdicionId !== null ||
		isActionEditingBibliografia ||
		(typeof fcs !== 'undefined' && fcs.hayBibliografiaEnEdicion && fcs.hayBibliografiaEnEdicion())
	);

	/**
	 * Suma de horas ya capturadas en los temas.
	 * @return {number}
	 */
	const horasTemasCapturadas = () =>
	  listaTemas.reduce((acc, t) => acc + (parseInt(t.horas, 10) || 0), 0);

	/**
	 * Pinta "X de Y" y aplica estado del botón/inputs para Temas.
	 * Regla: NO se puede capturar si no hay horas definidas (totalTeo <= 0) o si ya no quedan horas (restantes <= 0).
	 * Devuelve totales sin truncar (restantes puede ser negativo para mostrar sobregiro).
	 * @return {{totalTeo:number, usadas:number, restantes:number}}
	 */
	const actualizaHorasTeoricasRestantes = () => {
	  const totalTeo  = (parseInt($("#h_semestre_teo").val(), 10) || 0)
					 + (parseInt($("#h_semestre_pra").val(), 10) || 0);
	  const usadas    = horasTemasCapturadas() + (parseInt($('#horasPracticasTemario').val() , 10) || 0);
	  const restantes = totalTeo - usadas;

	  // Texto "X de Y"
	  $("#horasRestantes").text(Math.max(restantes, 0));
	  $("#horasTotales").text(totalTeo);

	  // Colores del bloque completo
	  const $box = $("#boxHorasRestantes");
	  $box
	    .removeClass("bg-success bg-danger bg-secondary")
	    .addClass(totalTeo <= 0 ? "bg-secondary" : (restantes > 0 ? "bg-success" : "bg-danger"))
	    .attr(
	      "title",
	      totalTeo <= 0
	        ? "Define primero las horas teóricas del semestre en Datos generales."
	        : (restantes < 0 ? `Sobregiro de ${Math.abs(restantes)} h teóricas` : "")
	    );

	  // Bloqueo de botón (y opcionalmente inputs)
	  const bloquear = (totalTeo <= 0) || (restantes <= 0);
	  $("#btnAgregarTema").prop("disabled", bloquear);

	  // impedir tecleo hasta definir horas:
	  $("#nombreTema, #horasTema, #objetivoTema").prop("disabled", totalTeo <= 0);

	  // Feedback del input "Horas tema"
	  const v = parseInt($("#horasTema").val(), 10) || 0;
	  $("#horasTema").toggleClass("is-invalid", totalTeo > 0 && v > Math.max(restantes, 0));

	  return { totalTeo, usadas, restantes };
	};
	
	/**
	 * 
	 * Funcion que inicializa los eventos principales a usar en el sistema SIPEFI-TOMO II.
	 * @return {void} 
	 * @method cargaEventosPrincipales
	 * @static
	 */
	const cargaEventosPrincipales = () => {
		
		//Cargamos eventos necesarios para la sesion
		comunE.cargaEventoSesion();
		
		/**
		 * Acciones de los botones de barra superior.
		 * @event module:etii~.menuBotones
		 * @type {object}
		 * @listens click
		 */
		$(".menuBotones").unbind("click");
		$(".menuBotones").on("click",function(){
			let accion = $(this).attr("target");
			switch(accion) {
			  case 'regresarBusqSoli':
				  	fComun.recargaPagina();
				    break;
			  case 'regresarLlenaSoli':
				  	soltii.cargaMenuLlenadoBotones();
				  	break;
			  case 'cargarSolicitud':
				  	fComun.guardaVarLocalS("accionSoli",0);
				  	fComun.guardaVarLocal("canAffect",true);
				  	fcs.cargaCatalogos(1,{rol: $("#rol").html()});
				    break;
			  case 'guardarSolicitud':
				  	$("#usuarioSol").html($("#usuario").html());
				  	fcs.accionSolicitud(1);
				    break;
			  case 'aprobarSolicitud':
				  	fcs.validaSolicitud(1);
				    break;
			  case 'rechazarSolicitud':
				  	fcs.modalRechazoSoli();
				    break;
			  case '#modalComentarios':
				  	fComun.mostrarModal(accion);
				    break;
			}
		});
		
		/**
		 * Evento para ajustar css de select2.
		 * @event module:etii~.custom-select
		 * @type {object}
		 * @listens select2:select
		 */
		$(".custom-select").unbind("select2:select");
		$(".custom-select").on("select2:select",function(){
			fcs.cssVistaCaptura();
		});
		
		/**
		 * .::| Evento que ayuda a mostrar modal para cancelar solicitud |::.
		 * @event module:etii~.bCancelarSol
		 * @type {object}
		 * @listens click
		 */
		$(".bCancelarSol").unbind("click");
		$(".bCancelarSol").on("click",function(){
			//solo se puede usar si la solicitud ya tiene un numero de solicitud asignado
			if($.isNumeric($("#numSolicitud").html())){
				let idSol = String($("#numSolicitud").html());
				let txtH = "Mensaje de alerta";
				let body = "<div class='form-group'>" +
				  				"<label for='razonCS'>Por favor escribe la raz&oacute;n por la que deseas cancelar la solicitud SIPEFI-" + idSol + ". " +
				  				"Tomando en cuenta que si confirmas la petici&oacute;n, se eliminar&aacute; la solicitud de forma permanente.</label>" +
				  				"<br><br><textarea class='form-control' id='razonCS' rows='3'></textarea>" +
				  				"<br>" +
				  				"<label for='razonCS'>&#191;Estas seguro de eliminar la solicitud SIPEFI-" + idSol + "&#63;</label>" +
				  			"</div>";
				fComun.creaModalAlerta(txtH, body, fcs.realizaCancelacionSolicitud, 0, "", "");
			}
		});
		
		/**
		 * Asigna automáticamente el tipo de modalidad según la modalidad seleccionada
		 * @event module:etii~#modalidad
		 * @listens change
		 */
		$("#modalidad").unbind("change");
		$("#modalidad").on("change", function () {
			try {
				const idModalidad = parseInt($(this).val());
				const catRel = fComun.getVarLocalJ("catalogos").catRelMod || [];

				// Buscar la relación
				const encontrado = catRel.find(([idMod]) => idMod === idModalidad);
				if (encontrado) {
					const idTipoMod = encontrado[1];
					$("#tipo_modalidad").val(idTipoMod);
					if(idTipoMod === 1){
						$("#valor_practico").val(null).trigger('change').prop("disabled", true);
						$("#h_sem_pra").val('0').trigger('change').prop("disabled", true);
						$("#h_semestre_pra").val('0').trigger('change');
					}else {
						$("#valor_practico").val(null).trigger('change').prop("disabled", false);
						$("#h_sem_pra").val('0').trigger('change').prop("disabled", false);
						$("#h_semestre_pra").val('0').trigger('change');
					}
				} else {
					$("#tipo_modalidad").val(0); 
				}
			} catch (e) {
				console.error("Error al asignar tipo modalidad:", e);
			}
		});

		$("#h_sem_teo").on("input", actualizaCreditos);
		$("#h_sem_pra").on("input", actualizaCreditos);
		
		/**
		 * Evento que activa la función agregarRelacion al hacer clic en el botón.
		 * Solo se ejecuta si el botón con ID #btnAgregarRelacion está presente en la vista.
		 * @event module:etii~#btnAgregarRelacion
		 * @type {object}
		 * @listens click
		 */
		$("#btnAgregarRelLicAsig").unbind("click");
		$("#btnAgregarRelLicAsig").on("click", function () {
		  fcs.agregarRelacionLicAsig();
		});

		/**
		 * Evento para agregar un tema con nombre, horas y objetivo específico.
		 * Valida los campos, actualiza las estructuras internas y agrega el tema a la tabla de temas.
		 * También agrega una opción al <select> de temas y actualiza la numeración global.
		 */
		$("#btnAgregarTema").off("click.sipefiTema").on("click.sipefiTema", agregarTema);
		
		/**
		 * Evento para agregar contenido a un tema previamente seleccionado.
		 * Valida el contenido, actualiza el contador, agrega una fila a la tabla de contenidos
		 * y actualiza la numeración global de contenidos.
		 */
		$("#btnAgregarContenido").off("click.sipefiContenido").on("click.sipefiContenido", agregarContenido);
	   
	   $("#tablaRelacionesLic")
		.off("click.sipefiRelacion", ".btnEliminarRelacion")
		.on("click.sipefiRelacion", ".btnEliminarRelacion", function () {
			fcs.eliminarRelacionLicenciatura($(this).attr("data-rel-key"));
		});
	   
	   // Evento: cambiar tipo de bibliografía
	   $('#tipo_bibliografia').off('change.sipefiBibliografia').on('change.sipefiBibliografia', function () {
	       fcs.actualizarCamposExtra();
	   });

	   /**
	    * Evento delegado para eliminar una fila de la tabla de bibliografía.
	    * Se adjunta al contenedor y aplica solo a botones con clase 'btn-eliminar-biblio'.
	    */
	   $('#tablaBibliografia tbody')
		.off('click.sipefiBibliografia', '.btn-eliminar-biblio')
		.on('click.sipefiBibliografia', '.btn-eliminar-biblio', function () {
			fcs.eliminarBibliografia($(this).attr('data-biblio-id'));
		});
	   
	   /**
	    * Evento que se ejecuta al hacer clic en el botón de agregar bibliografía.
	    * Valida campos mínimos y agrega la fila a la tabla.
	    */
	   $('#btnAgregarBibliografia').off('click.sipefiBibliografia').on('click.sipefiBibliografia', function () {
	     fcs.validaCamposReqBiblio();
	   });
		
	   //Eventos de modal y dataTables complementarios
	   eventosModalDTable();
	   
	   actualizaHorasTeoricasRestantes(); // Refresca el badge/botón de horas teoricas restantes
	   
	   $("#horasTema").on("input", function(){
	     // Solo marca inválido si supera lo restante
	     actualizaHorasTeoricasRestantes(); // recalcula y aplica la clase 'is-invalid' si corresponde
	   });

	   $("#horasPracticasTemario").on("input", function(){
	     // Solo marca inválido si supera lo restante
	     actualizaHorasTeoricasRestantes(); // recalcula y aplica la clase 'is-invalid' si corresponde
	   });

	   $("#s-2-tab").on('click', function(){
	     // Solo marca inválido si supera lo restante
	     actualizaHorasTeoricasRestantes(); // recalcula y aplica la clase 'is-invalid' si corresponde
	   });
	   
	   /**
	    * .::| Evento que inicializa el filtro de Licenciaturas en la vista de Coordinador |::.
	    * @event module:etii~.filtroLicenciaturas
	    * @type {object}
	    * @listens change
	    */
	   $("#filtroLicenciatura").unbind("change");
	   $("#filtroLicenciatura").on("change", function () {

	       try {
	           let idLicSel = $(this).val(); 
			   
	           soltii.pintaTablaAsigXLic(idLicSel || "");

	       } catch (e) {
	           console.error("Error al filtrar por licenciatura:", e);
	       }
	   });
	   
	   /**
	    * .::| Evento que descarga el PDF de la asignatura seleccionada |::.
	    * @event module:etii~.btnDescargarPDF
	    * @type {object}
	    * @listens click
	    */
	   $(document).off("click", ".btnDescargarPDF");
	   $(document).on("click", ".btnDescargarPDF", function () {
	       const idLic = $(this).data("licenciatura-id");
	       const idAsig = $(this).data("solicitud-id");
	       const info  = $(this).data("info-util"); 
		   
		   console.log(info)
	       //aqui mandar llamar a la funcion que tienes de descarga del PDF
	   });
	   
	   
	    $("#btnDescargarAllPdf").off("click");

		$("#btnDescargarAllPdf").on("click", function () {

			const $btn = $(this);
			const $spinner = $btn.find(".spinner-border");
			const $text = $btn.find(".btn-text");

			const idPerfil = parseInt($("#rol").html(), 10) || 0;
			const idLic = $("#filtroLicenciatura").val();

			if (!idLic) {
				return fComun.mostrarModalAdvertencia(
					"Selecciona al menos una licenciatura para descargar masivamente el PDF del Tomo II."
				);
			}

			$btn.prop("disabled", true);
			$spinner.removeClass("d-none");
			$text.html('<i class="fa-solid fa-file-pdf me-1"></i> Generando PDF...');

			descargaAllPdf(idPerfil, idLic);

			setTimeout(function () {
				$btn.prop("disabled", false);
				$spinner.addClass("d-none");
				$text.html('<i class="fa-solid fa-file-pdf me-1"></i> Descargar PDF (Tomo II)');
			}, 28000);
		});
	   
	};
	
	  /**
	   * Agrega un nuevo tema a la lista y actualiza la vista.
	   */
	  const agregarTema = () => {
	    const nombre = $("#nombreTema").val().trim();
	    const horas = $("#horasTema").val().trim();
	    const objetivo = $("#objetivoTema").val().trim();
	
	    if (!nombre) return fComun.mostrarTooltipCampo("#nombreTema", "El nombre del tema es requerido");
	    if (!horas || isNaN(horas) || parseInt(horas) <= 0)
	      return fComun.mostrarTooltipCampo("#horasTema", "Ingresa las horas del tema (mayor a 0)");
	    if (!objetivo) return fComun.mostrarTooltipCampo("#objetivoTema", "El objetivo del tema es requerido");
	
		const horasNueva = parseInt(horas, 10);
  		const { totalTeo, usadas, restantes } = actualizaHorasTeoricasRestantes();
		
		// NO permitir capturar si no han definido total teórico
	    if (totalTeo <= 0) {
	    	return fComun.mostrarModalAdvertencia(
	    		"Primero define las horas teóricas del semestre en la sección Datos generales."
	    	);
	  	}
  		// Si ya hay total teórico definido, no permitimos rebasarlo
	    if (totalTeo > 0 && horasNueva > Math.max(totalTeo - usadas, 0)) {
	    	return fComun.mostrarModalAdvertencia(
	      	`No puedes agregar ${horasNueva} h. Te quedan ${Math.max(totalTeo - usadas, 0)} h teóricas por asignar.`
	    	);
	    }
		
	    listaTemas.push({ id: contadorTemas++, nombre, horas, objetivo });
	
	    $("#nombreTema, #horasTema, #objetivoTema").val(""); // Limpiar campos
	    reconstruirDesdeEstructuras();
		
		actualizaHorasTeoricasRestantes(); // Refresca el badge/botón de horas teoricas restantes
	  };
	
	  /**
	   * Agrega un contenido relacionado a un tema.
	   */
	  const agregarContenido = () => {
	    const idTema = parseInt($("#temaContenido").val());
	    const texto = $("#contenidoTema").val().trim();
	
	    if (!idTema || !texto)
	      return fComun.mostrarTooltipCampo("#contenidoTema", "Selecciona un tema y escribe el contenido");
	
	    listaContenidos.push({ id: contadorContenidos++, idTema, texto });
	
	    $("#contenidoTema").val(""); // Limpiar campo
	    let option = $("#temaContenido").val();
	    reconstruirDesdeEstructuras();
	    $("#temaContenido").val(option);
	  };
	
	  /**
	   * Reconstruye las tablas y el select desde las estructuras de datos.
	   */
	  const reconstruirDesdeEstructuras = () => {
		if (!$.fn.DataTable.isDataTable('#tablaTemas') || !$.fn.DataTable.isDataTable('#tablaContenidos')) {
			return;
		}

		const tablaTemasDT = $('#tablaTemas').DataTable();
		const tablaContenidosDT = $('#tablaContenidos').DataTable();
		const modoVisualizacion = numeroEntero(fComun.getVarLocalS('accionSoli'), 0) === 1;
		const atributoOculto = modoVisualizacion ? 'hidden' : '';
		const mapaIdTemaToNumero = {};
		const mapaIdTemaToNombre = {};

		const filasTemas = listaTemas.map((tema, indice) => {
			const numero = indice + 1;
			mapaIdTemaToNumero[tema.id] = numero;
			mapaIdTemaToNombre[tema.id] = textoNormalizado(tema.nombre);
			const editando = Number(temaEnEdicionId) === Number(tema.id);

			const nombre = editando
				? `<input type="text" class="form-control" id="id-nombre-tema-${tema.id}" value="${textoHtmlSeguro(tema.nombre)}">`
				: textoHtmlSeguro(tema.nombre);
			const horas = editando
				? `<input type="number" class="form-control" id="id-horas-tema-${tema.id}" value="${textoHtmlSeguro(tema.horas)}">`
				: textoHtmlSeguro(tema.horas);
			const objetivo = editando
				? `<input type="text" class="form-control" id="id-objetivo-tema-${tema.id}" value="${textoHtmlSeguro(tema.objetivo)}">`
				: textoHtmlSeguro(tema.objetivo);

			const acciones = `<div ${atributoOculto}>
				<button type="button" class="btn btn-danger btn-sm" onclick="etii.eliminarTema(${tema.id})" ${editando ? 'disabled' : ''}>
					<i class="fas fa-trash-alt"></i>
				</button>
				<button type="button" class="btn btn-danger btn-sm" onclick="etii.editarTema(${tema.id})" ${editando ? 'hidden' : ''}>
					<i class="fas fa-edit"></i>
				</button>
				<button type="button" class="btn btn-danger btn-sm" onclick="etii.saveTema(${tema.id})" ${editando ? '' : 'hidden'}>
					<i class="fas fa-save"></i>
				</button>
			</div>`;

			return [numero, nombre, horas, objetivo, acciones];
		});

		tablaTemasDT.clear();
		if (filasTemas.length) tablaTemasDT.rows.add(filasTemas);
		tablaTemasDT.draw(false);

		$('#temaContenido').empty();
		listaTemas.forEach((tema, indice) => {
			$('#temaContenido').append(
				$('<option>', { value: tema.id, text: `${indice + 1}. ${textoNormalizado(tema.nombre)}` })
			);
		});

		const contadorPorTema = {};
		const filasContenidos = [];
		listaContenidos.forEach(contenido => {
			const numeroTema = mapaIdTemaToNumero[contenido.idTema];
			if (!numeroTema) {
				console.warn('Contenido no mostrado porque su tema ya no existe.', contenido);
				return;
			}

			contadorPorTema[contenido.idTema] = (contadorPorTema[contenido.idTema] || 0) + 1;
			const numeroContenido = contadorPorTema[contenido.idTema];
			const identificadorVisible = `${numeroTema}.${numeroContenido}`;
			const editando = Number(contenidoEnEdicionId) === Number(contenido.id);
			const textoContenido = editando
				? `<input type="text" class="form-control" id="id-contenido-${contenido.id}" value="${textoHtmlSeguro(contenido.texto)}">`
				: textoHtmlSeguro(contenido.texto);

			const acciones = `<div ${atributoOculto}>
				<button type="button" class="btn btn-danger btn-sm" onclick="etii.eliminarContenido(${contenido.id})" ${editando ? 'disabled' : ''}>
					<i class="fas fa-trash-alt"></i>
				</button>
				<button type="button" class="btn btn-danger btn-sm" onclick="etii.editarContenido(${contenido.id})" ${editando ? 'hidden' : ''}>
					<i class="fas fa-edit"></i>
				</button>
				<button type="button" class="btn btn-danger btn-sm" onclick="etii.saveContenido(${contenido.id})" ${editando ? '' : 'hidden'}>
					<i class="fas fa-save"></i>
				</button>
			</div>`;

			filasContenidos.push([
				`${numeroTema}. ${textoHtmlSeguro(mapaIdTemaToNombre[contenido.idTema])}`,
				identificadorVisible,
				textoContenido,
				acciones
			]);
		});

		tablaContenidosDT.clear();
		if (filasContenidos.length) tablaContenidosDT.rows.add(filasContenidos);
		tablaContenidosDT.draw(false);
		actualizaHorasTeoricasRestantes();
	  };

	  const eliminarTema = (id) => {
		if (temaEnEdicionId !== null || contenidoEnEdicionId !== null) {
			return fComun.mostrarModalAdvertencia('Guarda primero la edición abierta.');
		}
		const tieneContenido = listaContenidos.some(contenido => Number(contenido.idTema) === Number(id));
		if (tieneContenido) {
			return fComun.mostrarModalAdvertencia('No puedes eliminar este tema porque tiene contenido asociado.');
		}
		listaTemas = listaTemas.filter(tema => Number(tema.id) !== Number(id));
		reconstruirDesdeEstructuras();
	  };

	  const editarTema = (id) => {
		if (temaEnEdicionId !== null || contenidoEnEdicionId !== null) return;
		if (!listaTemas.some(tema => Number(tema.id) === Number(id))) return;
		temaEnEdicionId = Number(id);
		reconstruirDesdeEstructuras();
		$('.menuBotones[target="guardarSolicitud"], .menuBotones[target="aprobarSolicitud"], .menuBotones[target="rechazarSolicitud"]').prop('disabled', true);
	  };

	  const saveTema = (id) => {
		if (Number(temaEnEdicionId) !== Number(id)) return;
		const tema = listaTemas.find(item => Number(item.id) === Number(id));
		if (!tema) return;
		tema.nombre = textoNormalizado($(`#id-nombre-tema-${id}`).val());
		tema.horas = textoNormalizado($(`#id-horas-tema-${id}`).val());
		tema.objetivo = textoNormalizado($(`#id-objetivo-tema-${id}`).val());
		temaEnEdicionId = null;
		reconstruirDesdeEstructuras();
		$('.menuBotones[target="guardarSolicitud"], .menuBotones[target="aprobarSolicitud"], .menuBotones[target="rechazarSolicitud"]').prop('disabled', false);
	  };

	  const eliminarContenido = (id) => {
		if (temaEnEdicionId !== null || contenidoEnEdicionId !== null) {
			return fComun.mostrarModalAdvertencia('Guarda primero la edición abierta.');
		}
		listaContenidos = listaContenidos.filter(contenido => Number(contenido.id) !== Number(id));
		reconstruirDesdeEstructuras();
	  };

	  const editarContenido = (id) => {
		if (temaEnEdicionId !== null || contenidoEnEdicionId !== null) return;
		if (!listaContenidos.some(contenido => Number(contenido.id) === Number(id))) return;
		contenidoEnEdicionId = Number(id);
		reconstruirDesdeEstructuras();
		$('.menuBotones[target="guardarSolicitud"], .menuBotones[target="aprobarSolicitud"], .menuBotones[target="rechazarSolicitud"]').prop('disabled', true);
	  };

	  const saveContenido = (id) => {
		if (Number(contenidoEnEdicionId) !== Number(id)) return;
		const contenido = listaContenidos.find(item => Number(item.id) === Number(id));
		if (!contenido) return;
		contenido.texto = textoNormalizado($(`#id-contenido-${id}`).val());
		contenidoEnEdicionId = null;
		reconstruirDesdeEstructuras();
		$('.menuBotones[target="guardarSolicitud"], .menuBotones[target="aprobarSolicitud"], .menuBotones[target="rechazarSolicitud"]').prop('disabled', false);
	  };

	const editarBibliografia = (idBibliografia) => {
		if (fcs.editarBibliografiaFila(idBibliografia)) isActionEditingBibliografia = true;
	};

	const saveBibliografia = (idBibliografia) => {
		if (fcs.guardarBibliografiaFila(idBibliografia)) isActionEditingBibliografia = false;
	};


	
	/**
	 * Calcula los créditos automáticamente con base en horas semana teóricas y prácticas
	 * @event module:etii~#h_sem_teo
	 * @event module:etii~#h_sem_pra
	 * @listens input
	 */
	const actualizaCreditos = () => {
		try {
			const hTeo = parseFloat($("#h_sem_teo").val()) || 0;
			const hPra = parseFloat($("#h_sem_pra").val()) || 0;
			const creditos = (hTeo * 2) + hPra;
			$("#h_semestre_teo").val(hTeo*16);
			$("#h_semestre_pra").val(hPra*16);
			$("#creditos").val(creditos);
			
			actualizaHorasTeoricasRestantes(); 
		} catch (e) {
			console.error("Error al calcular créditos:", e);
		}
	};
	
	/**
	 * 
	 * Funcion que inicializa los eventos utilizados en un modal para un datatable.
	 * @return {void} 
	 * @method eventosModalDTable
	 * @static
	 */
	const eventosModalDTable = () => {
		
		/**
		 * Evento para ajustar estilos de datatables.
		 * @event module:etii~.table.display
		 * @type {object}
		 * @listens draw.dt
		 */
		$('table.display').on('draw.dt', function () {
			soltii.cargaEstilosTablas();
			etii.accionSolicitud();
		} );
		
		/**
		 * Evento que sirve para poder manipular el modal de comentarios draggable por toda la pagina eliminando el bloqueo de la pantalla inferior.
		 * @event module:etii~#modalComentarios
		 * @type {object}
		 * @listens shown.bs.modal
		 */
		$("#modalComentarios").unbind("shown.bs.modal");
		$('#modalComentarios').on('shown.bs.modal', function () {
			 $('body').removeClass('modal-open');
		});
		
		/**
		 * Evento que permite minimizar el modal de comentarios sin destruir su contenido.
		 * Oculta el modal visualmente sin eliminar la instancia de Bootstrap ni perder los datos.
		 * @event module:etii~#btnMinimizarComentarios
		 * @type {object}
		 * @listens click
		 */
		$("#btnMinimizarComentarios").unbind("click");
		$("#btnMinimizarComentarios").on("click", function () {
		  const modalInstance = bootstrap.Modal.getInstance(document.getElementById("modalComentarios"));
		  if (modalInstance) {
		    modalInstance.hide(); // Oculta sin cerrar ni destruir
		  }
		});
		
	};
	
	/**
	 * 
	 * Funcion que ayuda a crear eventos especiales, es decir, con funcionalidades adicionales al dar click sobre un boton de algun modal.
	 * @param {Object} elemento Nodo del elemento al que se le desea asignar el evento.
	 * @param {Object} modal Nodo del modal donde se estara trabajando.
	 * @param {Boolean} especial Booleano que indica si se desea hacer un trato especial al elemento al dar click.
	 * @param {Object} funcionDest Funcion que sera aplicada al dar click.
	 * @param {int} numEl Parametro que indica el numero de elementos de la funcion destino que se desea aplicar.
	 * @param {Object} param1 Objecto de la primera entrada a la funcion destino.
	 * @param {Object} param2 Objecto de la segunda entrada a la funcion destino.
	 * @return {void} 
	 * @method eventoEspecial
	 * @static
	 */
	const eventoEspecial = (elemento, modal, especial, funcionDest, numEl, param1, param2) => {
		numEl = parseInt(numEl);
		
		/**
		 * Evento que ayuda a realizar alguna accion especial de algun elemento.
		 * @event module:etii~#elementoEspecial
		 * @type {object}
		 * @listens click
		 */
		$(elemento).unbind("click");
		$(elemento).on('click', function () {
			fComun.ocultarModal(modal);
			if(especial){
				if(numEl == 0){
					funcionDest();
				}else if(numEl == 1){
					funcionDest(param1);
				}else if(numEl == 2){
					funcionDest(param1, param2);
				}
			}
		});
	};
	
	/**
	 * Funcion que ayuda a crear evento especial a los modales de tipo alerta.
	 * @param {Object} objB Nodo del elemento al que se le desea asignar el evento.
	 * @param {Object} objM Nodo del modal donde se estara trabajando.
	 * @param {int} opc Parametro que indica si sera necesario realizar una accion adicional al cerrar el modal.
	 * @return {void} 
	 * @method eventoAlerta
	 * @static
	 */
	const eventoAlerta = (objB, objM, opc) => {
		
		/**
		 * Evento que ayuda a realizar alguna accion especial del boton de cerrar de un modal de tipo alerta.
		 * @event module:etii~#botonAlerta
		 * @type {object}
		 * @listens click
		 */
		$(objB).unbind("click");
		$(objB).on('click', function () {
			fComun.ocultarModal(objM);
			opc==1?fcs.accionSolicitud(3):"";
		});
	};
	
	/**
	 * Funcion que ayuda a crear evento especial para el modal de la aprobacion exitosa de la solicitud.
	 * @param {Object} objB Nodo del elemento al que se le desea asignar el evento.
	 * @param {Object} objM Nodo del modal donde se estara trabajando.
	 * @return {void} 
	 * @method eventoAprobSoli
	 * @static
	 */
	const eventoAprobSoli = (objB, objM) => {
		/**
		 * Evento que ayuda a refrescar la pagina tras dar click al boton del modal.
		 * @event module:etii~#botonModAprob
		 * @type {object}
		 * @listens click
		 */
		$(objB).unbind("click");
		$(objB).on('click', function () {
			fComun.ocultarModal(objM);
			location.reload();
		});
	};
	
	/**
	 * Funcion que ayuda a crear evento necesario para saber que accion se desea aplicar a la solicitud visualizada.
	 * @return {void} 
	 * @method accionSolicitud
	 * @static
	 */
	const accionSolicitud = () => {
		/**
		 * Evento que ayuda a saber que accion se desea aplicar a la solicitud.
		 * @event module:etii~.accionSolicitud
		 * @type {object}
		 * @listens change
		 */
		$(".accionSolicitud").unbind("change");
		$(".accionSolicitud").on("change",function(){
			let rolSol = 99;
			try{
				rolSol = $(this).val().split("#@@#")[5].split("__")[0];
			}catch(e){}
			fComun.guardaVarLocalS("rolSol", rolSol);
			soltii.realizaAccionSolicitud($(this).val());
			$(this).val(0);
		});
	};

	const descargaPdf = (idPerfil, idLic, idSolicitud) => {
		let param = {
				idPerfil: idPerfil,
				idLic: idLic,
				idSolicitud: idSolicitud
		};
		fComun.postFileDownload("/SIPEFI/reporte/generarPdf/", param, function(resp){});
	};
	
	const descargaAllPdf = (idPerfil, idLic) => {
	    const idPerfilOk = parseInt(idPerfil, 10) || (parseInt($("#rol").html(), 10) || 0);
	    const idLicOk = (idLic !== undefined && idLic !== null && String(idLic).trim() !== "")
	        ? idLic
	        : $("#filtroLicenciatura").val();

	    if (!idLicOk) {
	        return fComun.mostrarModalAdvertencia(
	            "Selecciona al menos una licenciatura para descargar masivamente el PDF del Tomo II."
	        );
	    }

	    let param = { idPerfil: idPerfilOk, idLic: idLicOk };
	    fComun.postFileDownload("/SIPEFI/reporte/generarPdf/", param, function(resp){});
	};


	
	return{
		cargaEventosPrincipales: cargaEventosPrincipales,
		reiniciarTemarioContenido: reiniciarTemarioContenido,
		cargarTemarioContenido: cargarTemarioContenido,
		obtenerTemarioContenido: obtenerTemarioContenido,
		hayEdicionPendiente: hayEdicionPendiente,
		accionSolicitud:	accionSolicitud,
		eventoEspecial:	eventoEspecial,
		eventoAlerta:	eventoAlerta,
		eventoAprobSoli:	eventoAprobSoli,
		eliminarTema:	eliminarTema,
		editarTema:	editarTema,
		saveTema:	saveTema,
		eliminarContenido:	eliminarContenido,
		editarContenido: editarContenido,
		saveContenido: saveContenido,
		editarBibliografia: editarBibliografia,
		saveBibliografia: saveBibliografia,
		descargaPdf: descargaPdf,
		descargaAllPdf:  descargaAllPdf
	}
}();