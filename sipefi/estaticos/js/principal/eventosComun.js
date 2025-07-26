/**
 * comunE es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos apoya con los eventos en comun que se estaran usando en el front
 * @module comunE
 */

const comunE = function(){
	
	/**
	 * 
	 * Funcion que inicializa eventos necesarios para la sesion de los sistemas.
	 * @return {void} 
	 * @method cargaEventoSesion
	 * @static
	 */
	let cargaEventoSesion = function(){
		
		//Enviar una solicitud al servidor cuando se cierre la ventana o se cambie de página
		window.addEventListener('beforeunload', function (event) {
		    let param = {
				token: $("#token").html()
	    	}
		    fComun.post("/SIPEFI/cerrarSesion/",param, function(resp){});
		});
	};
	
	/**
	 * Funcion que ayuda a crear eventos especiales a algun elemento contenido en un modal.
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
		 * @event module:comunE~#elementoEspecial
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
					funcionDest(param1,param2);
				}else if(numEl == -1){
					location.reload();
				}
			}
		});
	};
	
	return{
		cargaEventoSesion:	cargaEventoSesion,
		eventoEspecial:	eventoEspecial
	}
}();