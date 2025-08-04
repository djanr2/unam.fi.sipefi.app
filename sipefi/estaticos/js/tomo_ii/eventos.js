/**
 * etii es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos apoya con los eventos que se estaran usando en el front del sistema SIPEFI-TOMO II.
 * @module etii
 */

const etii = function(){
	
	let listaTemas = [];       // [{ id, nombre, horas, objetivo }]
	let listaContenidos = [];  // [{ idTema, texto }]
	let contadorTemas = 1;
	
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
				  	//fcs.validaSoliRiesgos(1);
				    break;
			  case 'rechazarSolicitud':
				  	//fcs.modalRechazoSoli();
				    break;
			  case '#modalComentarios':
				  	$(accion).modal('show');
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
			let idSol = String($("#numSolicitud").html());
			let txtH = "Mensaje de alerta";
			let body = "<div class='form-group'>" +
			  				"<label for='razonCS'>Por favor escribe la raz&oacute;n por la que deseas cancelar la solicitud SIPEFI-" + idSol + ". " +
			  				"Tomando en cuenta que si confirmas la petici&oacute;n, se eliminar&aacute; la solicitud de forma permanente.</label>" +
			  				"<textarea class='form-control' id='razonCS' rows='3'></textarea>" +
			  				"<br>" +
			  				"<label for='razonCS'>&#191;Estas seguro de eliminar la solicitud SIPEFI-" + idSol + "&#63;</label>" +
			  			"</div>";
			fcs.creaModalAlerta(txtH, body, fcs.realizaCancelacionSolicitud, 0, "", "");
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
		$("#btnAgregarTema").on("click", agregarTema);
		
		/**
		 * Evento para agregar contenido a un tema previamente seleccionado.
		 * Valida el contenido, actualiza el contador, agrega una fila a la tabla de contenidos
		 * y actualiza la numeración global de contenidos.
		 */
		$("#btnAgregarContenido").on("click", agregarContenido);
	   
	   $("#tablaRelacionesLic").on("click", ".btnEliminarRelacion", function () {
		 let tablaRelacionesDT = $('#tablaRelacionesLic').DataTable();
	     tablaRelacionesDT.row($(this).closest("tr")).remove().draw();
	   });
	   
	   // Evento: cambiar tipo de bibliografía
	   $('#tipo_bibliografia').on('change', function () {
	       fcs.actualizarCamposExtra();
	   });
	   
	   /**
	    * Evento delegado para eliminar una fila de la tabla de bibliografía.
	    * Se adjunta al contenedor y aplica solo a botones con clase 'btn-eliminar-biblio'.
	    */
	   $('#tablaBibliografia tbody').on('click', '.btn-eliminar-biblio', function () {
	     $('#tablaBibliografia').DataTable().row($(this).closest('tr')).remove().draw();
	   });
	   
	   /**
	    * Evento que se ejecuta al hacer clic en el botón de agregar bibliografía.
	    * Valida campos mínimos y agrega la fila a la tabla.
	    */
	   $('#btnAgregarBibliografia').on('click', function () {
	     fcs.validaCamposReqBiblio();
	   });
		
	   //Eventos de modal y dataTables complementarios
	   eventosModalDTable();
		
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
	
	    listaTemas.push({ id: contadorTemas++, nombre, horas, objetivo });
	
	    $("#nombreTema, #horasTema, #objetivoTema").val(""); // Limpiar campos
	    reconstruirDesdeEstructuras();
	  };
	
	  /**
	   * Agrega un contenido relacionado a un tema.
	   */
	  const agregarContenido = () => {
	    const idTema = parseInt($("#temaContenido").val());
	    const texto = $("#contenidoTema").val().trim();
	
	    if (!idTema || !texto)
	      return fComun.mostrarTooltipCampo("#contenidoTema", "Selecciona un tema y escribe el contenido");
	
	    listaContenidos.push({ idTema, texto });
	
	    $("#contenidoTema").val(""); // Limpiar campo
	    reconstruirDesdeEstructuras();
	  };
	
	  /**
	   * Reconstruye las tablas y el select desde las estructuras de datos.
	   */
	  const reconstruirDesdeEstructuras = () => {
	    const tablaTemasDT = $('#tablaTemas').DataTable();
	    const tablaContenidosDT = $('#tablaContenidos').DataTable();
	
	    tablaTemasDT.clear().draw(false);
	    tablaContenidosDT.clear().draw(false);
	    $("#temaContenido").empty();
	
	    let mapIdTemaToNumero = {};
	    let mapIdTemaToNombre = {};
	
	    // === Renderizar temas y construir mapa ===
	    listaTemas.forEach((tema, idx) => {
	      const numero = idx + 1;
	      const fila = [
	        numero,
	        tema.nombre,
	        tema.horas,
	        tema.objetivo,
	        `<button class="btn btn-danger btn-sm" onclick="etii.eliminarTema(${tema.id})">
	           <i class="fas fa-trash-alt"></i>
	         </button>`
	      ];
	      const row = tablaTemasDT.row.add(fila).draw(false);
	      $(row.node()).attr("data-idtema", tema.id);
	
	      mapIdTemaToNumero[tema.id] = numero;
	      mapIdTemaToNombre[tema.id] = tema.nombre;
	
	      $("#temaContenido").append(`<option value="${tema.id}">${numero}. ${tema.nombre}</option>`);
	    });
	
	    // === Renderizar contenidos ===
	    const contadorPorTema = {};
	    listaContenidos = listaContenidos.filter(contenido => mapIdTemaToNumero[contenido.idTema]); // eliminar huérfanos
	
	    listaContenidos.forEach(contenido => {
	      const numTema = mapIdTemaToNumero[contenido.idTema];
	      const nombreTema = mapIdTemaToNombre[contenido.idTema];
	      const numContenido = contadorPorTema[contenido.idTema] = (contadorPorTema[contenido.idTema] || 1);
	
	      const fila = [
	        `${numTema}. ${nombreTema}`,
	        `${numTema}.${numContenido}`,
	        contenido.texto,
			`<button class="btn btn-danger btn-sm" onclick="etii.eliminarContenido(this)">
			     <i class="fas fa-trash-alt"></i>
			   </button>`
	      ];
	
	      const row = tablaContenidosDT.row.add(fila).draw(false);
	      $(row.node()).attr("data-idtema", contenido.idTema);
	
	      contadorPorTema[contenido.idTema]++;
	    });
	  };
	
	  /**
	   * Elimina un tema si no tiene contenido asociado.
	   * @param {number} id - ID del tema a eliminar
	   */
	  const eliminarTema = (id) => {
	    const tieneContenido = listaContenidos.some(c => c.idTema === id);
	    if (tieneContenido) {
	      fComun.mostrarModalAdvertencia("No puedes eliminar este tema porque tiene contenido asociado.");
	      return;
	    }
	
	    listaTemas = listaTemas.filter(t => t.id !== id);
	    reconstruirDesdeEstructuras();
	  };
	  
	 /**
	 * Elimina el contenido asociado al botón presionado.
	 * @param {HTMLElement} boton - Referencia al botón dentro de la fila
	 */
	const eliminarContenido = (boton) => {
	  const tabla = $('#tablaContenidos').DataTable();
	  const fila = $(boton).closest('tr');
	  tabla.row(fila).remove().draw(false);
	
	  // También remover de la estructura
	  const idTema = parseInt(fila.attr("data-idtema"));
	  const texto = fila.find('td:eq(2)').text().trim(); // Tercer columna (contenido)
	
	  // Eliminar solo la primera coincidencia (por si hay duplicados)
	  const idx = listaContenidos.findIndex(c => c.idTema === idTema && c.texto === texto);
	  if (idx >= 0) listaContenidos.splice(idx, 1);
	
	  reconstruirDesdeEstructuras();
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
	 * Funcion que inicializa el evento necesario para el modal de eleccion de rol.
	 * @param {Object} objB Nodo del objeto del boton donde se asigno el evento.
	 * @param {Object} objM Nodo del modal que se esta trabajando.
	 * @return {void} 
	 * @method eventoRol
	 * @static
	 */
	const eventoRol = (objB, objM) => {
		/**
		 * Solo si tiene mas de un perfil, elegir uno solo
		 * @event module:etii~ObjB
		 * @type {object}
		 * @listens click
		 */
		$(objB).unbind("click");
		$(objB).on('click', function () {
			let valor = parseInt($("#selectRol").val());
			if(valor != 0){
				soltii.iniciaComponentes(valor);
				if (document.activeElement) document.activeElement.blur(); // evitar warning accesibilidad
				$(objM).modal('hide');
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
			$(modal).modal('hide');
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
			$(objM).modal('hide');
			opc==1?fcs.accionSolicitud(4):"";
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
			$(objM).modal('hide');
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
	
	return{
		cargaEventosPrincipales: cargaEventosPrincipales,
		accionSolicitud:	accionSolicitud,
		eventoRol:	eventoRol,
		eventoEspecial:	eventoEspecial,
		eventoAlerta:	eventoAlerta,
		eventoAprobSoli:	eventoAprobSoli,
		eliminarTema:	eliminarTema,
		eliminarContenido:	eliminarContenido
	}
}();