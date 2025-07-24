/**
 * etii es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos apoya con los eventos que se estaran usando en el front del sistema SIPEFI-TOMO II.
 * @module etii
 */

const etii = function(){
	
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
				  	//fcs.accionSolicitud(1);
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
		
		//Eventos de modal y dataTables complementarios
		eventosModalDTable();
		
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
		 * @event module:epf~#modalComentarios
		 * @type {object}
		 * @listens shown.bs.modal
		 */
		$("#modalComentarios").unbind("shown.bs.modal");
		$('#modalComentarios').on('shown.bs.modal', function () {
			 $('body').removeClass('modal-open');
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
				rolSol = $(this).val().split("#@@#")[6].split("__")[0];
			}catch(e){}
			fComun.guardaVarLocalS("rolSol", rolSol);
			soltii.realizaAccionSolicitud($(this).val(),0);
			$(this).val(0);
		});
	};
	
	return{
		cargaEventosPrincipales: cargaEventosPrincipales,
		accionSolicitud:	accionSolicitud,
		eventoRol:	eventoRol,
		eventoEspecial:	eventoEspecial,
		eventoAlerta:	eventoAlerta,
		eventoAprobSoli:	eventoAprobSoli
	}
}();