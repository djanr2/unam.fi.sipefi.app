/**
 * soltii es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase es la principal, es decir, funciona como un main, ya que es la primera que en 
 * interactuar entre el cliente y servidor, entonces aqui podremos encontrar las funciones principales
 * del sistema.
 * @module soltii
 */
const soltii = function(){
	
	/**
	 * Funcion que recibe los parametros iniciales del sistema, obtenidos del servidor.
	 * @param {Object} idsValidador Contiene la lista de IDS de los validadores.
	 * @return {void} 
	 * @method inicio
	 * @static
	 */
	const inicio = (idsValidador) => {
		fComun.guardaVarLocal("idsValidador",idsValidador);
		fComun.guardaVarLocal("objSoli",{accion: 0});
		let roles = JSON.parse(String($("#rol").html()).replace(new RegExp("'",'g'),"\""));
		let tamRol = roles.resp.length;
		fComun.initDefault();
		fComun.iniciaModalComentarios();
		fl.cargaTablasP1();
		cargaMenuIniBotones();
		(tamRol>1)?eligeRol(roles):iniciaComponentes(roles.resp[0].id);
	};

	/**
	 * Funcion que inicializa los componentes en el sistema de acuerdo al perfil y usuario logueado.
	 * @param {int} valor Contiene el perfil del usuario logueado.
	 * @return {void} 
	 * @method iniciaComponentes
	 * @static
	 */
	const iniciaComponentes = (valor) => {
		$("#rol").html(valor);
		//Quitamos opcion de crear solicitudes nuevas al validador
		let idRV = fComun.getVarLocalJ("idsValidador");
		$("button[target|='aprobarSolicitud']").html("Solicitar aprobaci&oacute;n");
		$(".creaSolicitud").show();
		if($.inArray(valor,idRV) != -1){
			$(".creaSolicitud").hide();
			$("#tablaSoliUsuario").parent().css("margin-top", "100px");
			$("button[target|='aprobarSolicitud']").html("Aprobar");
		}
		cargaInfoTablasP1();
		etii.cargaEventosPrincipales();
		fComun.validadorForm(".inputNumber");
		fComun.validadorForm(".inputPorcentaje");
	};
	
	/**
	 * Funcion que inicializa modal para elegir el rol a usar, cuando el usuario tiene muchos rol definidos.
	 * @param {Object} obj Contiene la lista de roles que tiene definidos el usuario logueado.
	 * @return {void} 
	 * @method eligeRol
	 * @static
	 */
	const eligeRol = (obj) => {
		let opcSelect = [{id: "0", text: "Elige tu perfil"}]; 
		let objOpc = obj.resp;
		for(i in objOpc){opcSelect.push({id: objOpc[i].id, text: objOpc[i].rol})} 
		$('#modalSelectRol').modal('show');
		etii.eventoRol(".cierraRol",'#modalSelectRol');
		fl.select2("#selectRol",opcSelect,1);
	};
	
	/**
	 * Funcion que inicializa el menu de botones, secciones para la pantalla principal.
	 * @return {void} 
	 * @method cargaMenuIniBotones
	 * @static
	 */
	const cargaMenuIniBotones = () => {
		$('.menuBotones').hide();
		$(".SIPEFI_LOGIN").show();
		$('.menuBotones[target="cargarSolicitud"]').show();
		$("#seccionBusqSoli").show();
	    $("#seccionCapturaSoli").hide();
	    //Se limpia primero sección de comentarios
	    $("#seccionComentarios").html("");
	    $(".bCancelarSol").hide();
	};
	
	/**
	 * Funcion que inicializa el menu de botones, secciones para la pantalla de carga de la solicitud.
	 * @return {void} 
	 * @method cargaMenuLlenadoBotones
	 * @static
	 */
	const cargaMenuLlenadoBotones = () => {
		let accion = parseInt(fComun.getVarLocalS("accionSoli"));
		let rolUser = parseInt($("#rol").html());
		let idRV = fComun.getVarLocalJ("idsValidador");
		let canAffect = fComun.getVarLocalJ("canAffect");
		$('.menuBotones').hide();
		$(".SIPEFI_LOGIN").hide();
		$('.menuBotones[target="regresarBusqSoli"]').show();
		
		if(accion == 1){ //Modo visualizar
			$('.menuBotones[target="guardarSolicitud"]').hide();
		}else{ //Modo edicion/copia solicitud/nueva solicitud
			$('.menuBotones[target="guardarSolicitud"]').show();
		}
		if($.inArray(rolUser,idRV) != -1 && canAffect){ //Solo si tiene perfil validador y la solicitud cumple requisitos podra rechazar solicitud
			$('.menuBotones[target="rechazarSolicitud"]').show();
			$('.menuBotones[target="#modalComentarios"]').show();
			//Solo poner boton de cancelar al validador del area
			let rolSol = parseInt(fComun.getVarLocalS("rolSol"));
			let compRol = rolUser-rolSol
			if(compRol == 1 || compRol == 0)
				$(".bCancelarSol").show();
		}else if(canAffect){
			$('.menuBotones[target="#modalComentarios"]').show();
		}
		$("#seccionBusqSoli").hide();
	    $("#seccionCapturaSoli").show();
	    fl.defaultTooltipster();
	};
	
	/**
	 * Funcion que carga la informacion de las tres tablas principales en la pantalla inicial del sistema,
	 * en donde se muestran las solicitudes procesadas por los usuarios.
	 * @return {void} 
	 * @method cargaInfoTablasP1
	 * @static
	 */
    const cargaInfoTablasP1 = () => {
    	let param = {
    			user: $("#usuario").html(),
    			rol: $("#rol").html()
    	}
    	fComun.post("/SIPEFI/llenaTablasSoli",param, function(resp){
			try{
				let obj = resp;
				fComun.guardaVarLocal("catalogos",obj.catalogos)
				$(".tituloTablas").removeClass("esconder");
				/*Primero validamos informacion de solicitudes
				 * realizadas por el usuario logueado*/
				if(obj.estatusTSU == 200){
					fComun.refrescaTabla("#tablaSoliUsuario",obj.TSU);
				}
				/*Solicitudes donde participo el usuario logueado
				 * y que ha mandado a siguienes estatus*/
				if(obj.estatusTSA == 200){
					fComun.refrescaTabla("#tablaSoliAvanzadas",obj.TSA);
				}
				/*De igual manera validamos y obtenemos las solicitudes que
				 * han sido realizadas en el rango de hoy - 30 dias*/
				if(obj.estatusTSR == 200){
					fComun.refrescaTabla("#tablaSoliRecientes",obj.TSR);
				}
				soltii.cargaEstilosTablas();
			}catch(e){console.log(e)}
		});
    };
	
	/**
	 * Funcion que ayuda a modificar los estilos de las tablas que estan siendo trabajadas en el sistema.
	 * @return {void} 
	 * @method cargaEstilosTablas
	 * @static
	 */
	const cargaEstilosTablas = () => {
		let idRV = fComun.getVarLocalJ("idsValidador");
		let rol = parseInt($("#rol").html());
		$("#tablaSoliUsuario_wrapper .tituloTablas").html(
				($.inArray(rol,idRV) != -1)?'<strong>Validaciones pendientes</strong>':
											'<strong>Solicitudes pendientes de '+$("#usuario").html()+'</strong>');
		$("#tablaSoliAvanzadas_wrapper .tituloTablas").html('<strong>Solicitudes donde '+$("#usuario").html()+' particip&oacute;</strong>');
		$("#tablaSoliRecientes_wrapper .tituloTablas").html('<strong>Solicitudes recientes</strong>');
		$("#tablaSoliUsuario th").addClass("centrar");
		$("#tablaSoliAvanzadas th").addClass("centrar");
		$("#tablaSoliRecientes th").addClass("centrar");
		$("#tablaSoliUsuario").parent().addClass("espacioTablas");
		$("#tablaSoliAvanzadas").parent().addClass("espacioTablas");
		$("#tablaSoliRecientes").parent().addClass("espacioTablas");
		$(".dataTables_length").addClass("espacioRegMostrar");
	};
	
    /**
	 * Funcion encargada de realizar las acciones para la solicitud (1- Visualizar solicitud, 2- Editar solicitud).
	 * @param {String} infoSelect Contiene la informacion general de la solicitud elegida para realizar una accion.
	 * @param {int} opc Parametro que define la accion a realizar con la solicitud.
	 * @return {void} 
	 * @method realizaAccionSolicitud
	 * @static
	 */
	const realizaAccionSolicitud = (infoSelect, opc) => {
    	let accion = "";
    	let infoUtil = "";
    	let canAffect = false;
    	 //Edicion o visualizar solicitud 1, 2
		accion = String(infoSelect).split("__")[0];
    	infoUtil = String(infoSelect).split("__")[1];
    	let eSoli = parseInt(String(infoUtil).split("#@@#")[1]); 
    	canAffect = $.isNumeric(String(infoSelect).split("__")[2]);
    	canAffect = canAffect * ((eSoli == 3)?false:true);
    	canAffect = canAffect==1?true:false;
    	fComun.guardaVarLocal("canAffect",canAffect);
    	fComun.guardaVarLocalS("accionSoli",accion);
    	let param = {
    			action: accion,
    			info: infoUtil,
    			rol: $("#rol").html()
    	}
		//fcs.cargaCatalogos(2,param);
    };
	
	return{
		inicio : inicio,
		cargaEstilosTablas:	cargaEstilosTablas,
		cargaMenuIniBotones:	cargaMenuIniBotones,
		cargaMenuLlenadoBotones:	cargaMenuLlenadoBotones,
		realizaAccionSolicitud:	realizaAccionSolicitud,
		iniciaComponentes:	iniciaComponentes
	}
}();