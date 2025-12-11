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
		if(tamRol>1){ //tiene opcion de mas de un perfil
			eligeRol(roles);
		}else{ //perfil unico
			iniciaComponentes(roles.resp[0].id, roles.resp[0].rol);
			pintaRolUsuario(roles.resp[0].rol);
		}
	};
	
	const pintaRolUsuario = (rol) => {
		let icono = "";

		if(rol === "Administrador"){
			icono = '<i class="fas fa-crown"></i>';
		}else if(rol.includes("Operador")){
			icono = '<i class="fas fa-edit"></i>';
		}else if(rol.includes("Validador")){
			icono = '<i class="fas fa-clipboard-check"></i>';
		}else if(rol.includes("Coordinador")){
			icono = '<i class="fas fa-user-tie"></i>';
		}
		
		$("#usuario").after(
		` <span class="ms-2 text-white d-inline-flex align-items-center">${icono}<span>${rol}</span></span>`
		);
	}

	/**
	 * Funcion que inicializa los componentes en el sistema de acuerdo al perfil y usuario logueado.
	 * @param {int} rol Contiene el perfil del usuario logueado.
	 * @param {String} nomRol Contiene el nombre del perfil logueado.
	 * @return {void} 
	 * @method iniciaComponentes
	 * @static
	 */
	const iniciaComponentes = (rol, nomRol) => {
		$("#rol").html(rol);
		if(nomRol.includes("Coordinador")){
			cargaInfoTablasP1(2);
		}else{
			//Quitamos opcion de crear solicitudes nuevas al validador
			let idRV = fComun.getVarLocalJ("idsValidador");
			$("button[target|='aprobarSolicitud']").html("Solicitar validaci&oacute;n");
			$(".creaSolicitud").show();
			$("#tablaSRU").show();
			if($.inArray(rol, idRV) != -1){
				$(".creaSolicitud").hide();
				$("#tablaSoliUsuario").parent().css("margin-top", "100px");
				$("button[target|='aprobarSolicitud']").html("Aprobar");
			}else{
				$("#tablaSRU").hide();
			}
			cargaInfoTablasP1(1);
		}
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
		$('.menuBotones[target="regresarBusqSoli"]').show();
		
		if(accion == 1){ //Modo visualizar
			$('.menuBotones[target="guardarSolicitud"]').hide();
		}else{ //Modo edicion/copia solicitud/nueva solicitud
			$('.menuBotones[target="guardarSolicitud"]').show();
		}
		if($.inArray(rolUser,idRV) != -1 && canAffect){ //Solo si tiene perfil validador y la solicitud cumple requisitos podra rechazar solicitud
			$('.menuBotones[target="rechazarSolicitud"]').show();
			$('.menuBotones[target="#modalComentarios"]').show();
			$(".bCancelarSol").show();
		}else if(canAffect){
			$('.menuBotones[target="#modalComentarios"]').show();
			$(".bCancelarSol").show();
		}
		$("#seccionBusqSoli").hide();
	    $("#seccionCapturaSoli").show();
	    fl.defaultTooltipster();
	};
	
	/**
	 * Funcion que carga la informacion de las tres tablas principales en la pantalla inicial del sistema,
	 * en donde se muestran las solicitudes procesadas por los usuarios.
	 * @param {int} opcion Parametro que contiene la opcion deseada, 1 - Vistas normales, 2 - Vista coordinador
	 * @return {void} 
	 * @method cargaInfoTablasP1
	 * @static
	 */
    const cargaInfoTablasP1 = (opcion) => {
		opcion = parseInt(opcion)
    	let param = {
    			user: $("#usuario").html(),
    			rol: $("#rol").html()
    	}
    	fComun.post("/SIPEFI/llenaTablasSoli",param, function(resp){
			try{
				let obj = resp;
				fComun.guardaVarLocal("catalogos",obj.catalogos)
				if(opcion == 1){
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
				}else{
					fComun.guardaVarLocal("infoAsigLic",obj.infoAsigLic)
					pintaVistaCoordinador();
				}
				soltii.cargaEstilosTablas();
			}catch(e){console.log(e)}
		});
    };
	
	/**
	 * Funcion que ayuda a pintar la información de la vista del coordinador
	 * @return {void} 
	 * @method cargaEstilosTablas
	 * @static
	 */
	const pintaVistaCoordinador = () => {
		$(".opcSeccIni").hide();
		$(".creaSolicitud").hide();
		$("#seccionCoord").show();
		
       	const obj = fComun.getVarLocalJ("catalogos") || {};
		
       	const catLic = obj.catLic || [];

	    const $selLic = $("#filtroLicenciatura");

       	// Limpiamos y agregamos opción "Todas"
       	$selLic.empty().append(
           $('<option>', { value: '' }).text('Todas')
       	);

       	catLic.forEach(([id, nombre]) => {
           $selLic.append(
               $('<option>', { value: id }).text(nombre)
           );
       	});

       	if ($.fn.select2) {
           $selLic.select2({
               placeholder: "Todas las licenciaturas",
               width: '100%',
               allowClear: true,
               language: "es"
           });
       	}
		
		pintaTablaAsigXLic("");
	};
	
	/**
	 * .::| Función que pinta la tabla de Asignaturas por Licenciatura |::.
	 * @function pintaTablaAsigXLic
	 * @param {string|number} idLicFiltro ID de licenciatura a filtrar, o ""/null para todas
	 * @return {void}
	 */
	const pintaTablaAsigXLic = (idLicFiltro = "") => {
	    const raw = fComun.getVarLocalJ("infoAsigLic") || [];
	    const lista = Array.isArray(raw) ? raw : (raw.data || []);
		const idPerfil = $("#rol").html();

	    let html = "";

	    lista.forEach(row => {
	        const [
	            numSoli,          // 0
	            idEst,            // 1
	            estatusDesc,      // 2
	            idLic,            // 3
	            nomLic,           // 4
	            nomAsig,          // 5
	            fechaMod,         // 6
	            infoUtil          // 7
	        ] = row;

	        // Si hay filtro y no coincide la licenciatura, saltamos
	        if (idLicFiltro && String(idLic) !== String(idLicFiltro)) {
	            return;
	        }

	        let badgeClass = "bg-secondary";
	        switch (Number(idEst)) {
	            case 0: badgeClass = "bg-danger"; break;             // Cancelada
	            case 1: badgeClass = "bg-secondary"; break;          // Elaboración
	            case 2: badgeClass = "bg-warning text-dark"; break;  // Revisión
	            case 3: badgeClass = "bg-success"; break;            // Concluida
	        }

	        html += `
	            <tr data-id-licenciatura="${idLic}">
	                <td class="text-center">${numSoli}</td>
	                <td>
	                    <span class="badge ${badgeClass}">${estatusDesc}</span>
	                </td>
	                <td>${nomLic}</td>
	                <td>${nomAsig}</td>
	                <td class="text-center">${fechaMod || ""}</td>
	                <td class="text-center">
	                    <button type="button"
	                            class="btn btn-outline-primary btn-sm btnDescargarPDF"
	                            data-licenciatura-id="${idLic}"
	                            data-solicitud-id="${numSoli}"
	                            data-info-util="${infoUtil}" onclick="etii.descargaPdf(${idPerfil}, ${idLic}, ${numSoli})">
	                        <i class="fa-solid fa-file-pdf me-1"></i>PDFq
	                    </button>
	                </td>
	                <td class="d-none info-util">${infoUtil}</td>
	            </tr>
	        `;
	    });

	    $("#tablaAsigXLic tbody").html(html);
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
				($.inArray(rol,idRV) != -1)?'<strong>Pendientes por validar</strong>':
											'<strong>Solicitudes pendientes de '+$("#usuario").html()+'</strong>');
		$("#tablaSoliAvanzadas_wrapper .tituloTablas").html('<strong>Solicitudes donde particip&eacute;</strong>');
		$("#tablaSoliRecientes_wrapper .tituloTablas").html('<strong>Otras Solicitudes</strong>');
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
	 * @return {void} 
	 * @method realizaAccionSolicitud
	 * @static
	 */
	const realizaAccionSolicitud = (infoSelect) => {
    	let accion = "";
    	let infoUtil = "";
    	let canAffect = false;
    	 //Edicion o visualizar solicitud 1, 2
		accion = String(infoSelect).split("__")[0];
    	infoUtil = String(infoSelect).split("__")[1];
    	let eSoli = parseInt(String(infoUtil).split("#@@#")[1]); 
    	canAffect = $.isNumeric(String(infoSelect).split("__")[2]);
    	canAffect = canAffect;
    	canAffect = canAffect==1?true:false;
    	fComun.guardaVarLocal("canAffect",canAffect);
    	fComun.guardaVarLocalS("accionSoli",accion);
    	let param = {
    			action: accion,
    			info: infoUtil,
    			rol: $("#rol").html()
    	}
		fcs.cargaCatalogos(2,param);
    };
	
	/**
	 * Funcion encargada obtener y de pintar o cargar la informacion de la solicitud elegida.
	 * @param {Object} param Parametro que contiene el objeto con la info necesaria para consultar informacion de la solicitud.
	 * @return {void} 
	 * @method pintaSolicitud
	 * @static
	 */
    const pintaSolicitud = (param) => {
    	fComun.mostrarEspera();
    	fComun.post("/SIPEFI/cargaSolicitud/",param, function(resp){
			try{
				let obj = resp;
				if(obj.estatus == 200){ //Tenemos información que mostrar
					fcs.cargaSolicitudAccion(obj);
				}else{
					$("#modalCargaSoli .modal-title").html("Mensaje de error");
					$("#modalCargaSoli .modal-header").addClass("headerModalError");
					$("#modalCargaSoli .textoBody").html("" +
							"No fue posible realizar la carga de la solicitud <br>" +
							"Contacta al área de soporte SIPEFI <br>" +
							"<strong><a href=\"mailto:sipefi@fi.unam.edu?subject=Necesito%20ayuda\">" +
								"sipefi@fi.unam.edu" +
							"</a></strong>" +
					"");
					$("#modalCargaSoli .modal-body button").attr('class','btn btn-danger');
					$('#modalCargaSoli').modal('show');
				}
			}catch(e){console.log(e)}
		});
    };
	
	return{
		inicio : inicio,
		cargaEstilosTablas:	cargaEstilosTablas,
		cargaMenuIniBotones:	cargaMenuIniBotones,
		cargaMenuLlenadoBotones:	cargaMenuLlenadoBotones,
		realizaAccionSolicitud:	realizaAccionSolicitud,
		iniciaComponentes:	iniciaComponentes,
		pintaSolicitud:	pintaSolicitud,
		pintaRolUsuario: pintaRolUsuario,
		pintaTablaAsigXLic:	pintaTablaAsigXLic
	}
}();