/**
 * fcs es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * En esta clase encontraremos la mayoria de las funciones principales del flujo completo del sistema SIPEFI-TOMO II
 * @module fcs
 */
const fcs = function(){
	//Variables globales
	let objGuardarTemp = {	
							get numSolicitud(){ return $("#numSolicitud").html(); },
							get accionGA(){ return (($.isNumeric(this.numSolicitud))?2:1); },
							get idEstSoli(){ return $("#idES").html(); },
							get usuario(){ return $("#usuario").html(); },
							get usuarioSoli(){ return $("#usuarioSol").html(); },
							get rol(){ return $("#rol").html(); },
							get token(){ return $("#token").html(); },
							get comentarios(){ return $("#comentarios").Editor("getText"); },
						
						};
	let objSolicitud = {}
	let textoError = "Campo obligatorio";
	
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
		const cargaCatalogos = (opc, param) => {
				try{
					soltii.cargaMenuLlenadoBotones();
					let obj = fComun.getVarLocalJ("catalogos");
				}catch(e){console.log(e)}
				cssVistaCaptura();
		};
	
	return{
		cssVistaCaptura:	cssVistaCaptura,
		cargaCatalogos:	cargaCatalogos
	}
}();