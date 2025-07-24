/**
 * fComun es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos ayuda a organizar las funciones en comun o que pueden ser reutilizadas 
 * en varias partes del codigo.
 * @module fComun
 */
const fComun = function(){
	
	/**
	 * Constante que define las url que se usaran en peticiones Ajax con carga de datos grande
	 * y requieren algun modal de carga de datos.
	 * @constant urlsAjax
	 * @default
	 */
	let urlsAjax = ['/buscaSolicitud/', '/accionSolicitud/',
					'/llenaTablasSoli/', '/cargaSolicitud/', 
					'/recargaPagina/','/cancelarSolicitud/'
					];
	
	/**
	 * Funcion que ayuda a cifrar las peticiones ajax con CSRF para que el flujo de datos sea seguro.
	 * @param {String} method Define el tipo de metodo utilizado para peticiones (POST, GET, PUT...)
	 * @return {void} 
	 * @method csrfSafeMethod
	 * @static
	 */
	// these HTTP methods do not require CSRF protection
	const csrfSafeMethod = (method) => (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	
	/**
	 * Funcion que ayuda a inicializar los modales con ciertas caracteristicas.
	 * @return {void} 
	 * @method iniciaModalComentarios
	 * @static
	 */
	const iniciaModalComentarios = () => {
		$('#modalComentarios').modal({
			backdrop: false,
			show: false,
			keyboard: false
		});
		$("#comentarios").Editor();  
		iniciaModalDraggable();
	};
	
	/**
	 * Funcion que ayuda a inicializar los modales de tipo draggables con ciertas caracteriscas.
	 * @return {void} 
	 * @method iniciaModalDraggable
	 * @static
	 */
	const iniciaModalDraggable = () => {
		$('.modal.draggable>.modal-dialog').draggable({
		    cursor: 'move',
		    handle: '.modal-header'
		});
		$('.modal.draggable>.modal-dialog>.modal-content>.modal-header').css('cursor', 'move');
	};
	
	/**
	 * Funcion que ayuda a inicializar las caracteristicas iniciales de peticiones Ajax, 
	 * datepicker, tooltipster, DataTables e inicia modales con ciertas caracteristicas.
	 * @param {Object} urls Parametro que indica las url que seran usadas.
	 * @return {void} 
	 * @method initDefault
	 * @static
	 */
	const initDefault = (urls = urlsAjax) => {
		
		$.fn.modal.Constructor.prototype.enforceFocus = function() {};
		
		/***.::| Evento que inicializa datePicker |::.***/
		$('.fecha').datepicker($.fn.datepicker.languages['es-ES']);
		
		$(".fechaSinRest").datepicker({
			format: 'dd/mm/yyyy',
		    autoHide: true,
		    autoPick: true,
		    inline: true,
		    days: ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'],
		    daysShort: ['Dom','Lun','Mar','Mie','Jue','Vie','Sab'],
		    daysMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sa'],
		    weekStart: 1,
		    months: ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
		    monthsShort: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
		});
		
		$.fn.modal.Constructor.prototype.enforceFocus = function() {};
		
		$('.modalStatic').modal({
	  		  keyboard: false,
	  		  backdrop: 'static',
	  		  show: false
		});
		
		$.ajaxSetup({
		    beforeSend: function(xhr, settings) {
		        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		        	let csrftoken = Cookies.get('csrftoken');
		            xhr.setRequestHeader("X-CSRFToken", csrftoken);
		            xhr.setRequestHeader("tokenSistema", $("#token").html());
		        }
		        for(idx in urls){
		        	if ( settings.url.includes(urls[idx]) ) {
		        		mostrarEspera();
		        	}
		        }
		    }
		});
		
		$( document ).ajaxComplete(function( event, xhr, settings ) {
			let acceso = xhr.getResponseHeader('AccesoSistema');
			let url = settings.url;
			if(!url.includes("ParametrosDT_Esp.json")) {
	        	ocultarEspera();
	        }
			if(acceso)
		    	if(acceso == 'NOK')
		    		$(".SIPEFI_LOGIN").trigger("click");
		});
		
		//Inicializamos los valores default para los Tooltip
		$.tooltipster.setDefaults({
			theme: 'tooltipster-punk',
			animation: 'fade',
			contentAsHTML: 'true',
			side: 'right',
			trigger: 'custom',
			triggerOpen: {
			        click: true,
			        tap: true
			},
			triggerClose: {
			        click: true,
			        tap: true
			}
		});	
		
		/****
		 * inicializacion por default todas las datatables
		 ****/
		$.extend( true, $.fn.dataTable.defaults, {
			"fixedHeader": true,
			"colReorder": false,
			"ordering": false,
            "lengthMenu": [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"] ],
			"dom": '<"tituloTablas esconder">frtlip',
			"info":     false,
			"language": {
				"url": "SARC/estaticos/js/datatable/ParametrosDT_Esp.json"
			}
		} );
	};
	
	/**
	 * Funcion que muestra un modal de espera.
	 * @return {void} 
	 * @method mostrarEspera
	 * @static
	 */
	const mostrarEspera = () => {
		$(".espera").modal('show');
	};
	
	/**
	 * Funcion que oculta un modal de espera.
	 * @return {void} 
	 * @method ocultarEspera
	 * @static
	 */
	const ocultarEspera = () => {
		 $('.espera').each(function(){
             $(this).modal('hide');
         });
	};
	
	/**
	 * Funcion que ayuda a procesar informacion entre el cliente y servidor por metodo POST con ayuda de AJAX.
	 * @param {String} urlPost Es la cadena url que se usara en la peticion POST al servidor.
	 * @param {Object} dataPost Es el objeto que se desea pasar en la peticion POST al servidor.
	 * @param {Function} handleData Funcion que obtendra la respuesta de la peticion POST al servidor.
	 * @return {void} 
	 * @method post
	 * @static
	 */
	const post = (urlPost, dataPost, handleData) => {
		let timeReq = new Date();
		$.ajax({
	        url: urlPost + "?frequest=" + String(timeReq.getTime()),
	        data: dataPost,
	        dataType: 'json',
	        type: "post",
	        cache: false,
	        success: function (data) {
	        	handleData(data);
	        },
            error: function(){
            	handleData("No se obtuvo nada");
            }
	      });
	};
	
	/**
	 * Funcion que ayuda a procesar informacion entre el cliente y servidor por metodo POST con ayuda de AJAX,
	 * pero la informacion la trata como tipo JSON.
	 * @param {String} urlPost Es la cadena url que se usara en la peticion POST al servidor.
	 * @param {Object} dataPost Es el objeto que se desea pasar en la peticion POST al servidor.
	 * @param {Function} handleData Funcion que obtendra la respuesta de la peticion POST al servidor.
	 * @return {void} 
	 * @method post2
	 * @static
	 */
	const post2 = (urlPost, dataPost, handleData) => {
		let timeReq = new Date();
		$.ajax({
	        url: urlPost + "?frequest=" + String(timeReq.getTime()),
	        data: {obj: JSON.stringify(dataPost)},
	        dataType: 'json',
	        type: "post",
	        cache: false,
	        success: function (data) {
	        	handleData(data);
	        },
            error: function(xhr, status, error){
        		console.error("Error:", error);
            	handleData("No se obtuvo nada");
            }
	      });
	};
	
	/**
	 * Funcion que ayuda a procesar informacion entre el cliente y servidor por metodo POST con ayuda de AJAX,
	 * pero la informacion que se envia es de tipo File.
	 * @param {String} urlPost Es la cadena url que se usara en la peticion POST al servidor.
	 * @param {Object} dataPost Es el objeto que se desea pasar en la peticion POST al servidor.
	 * @param {Function} handleData Funcion que obtendra la respuesta de la peticion POST al servidor.
	 * @return {void} 
	 * @method postFile
	 * @static
	 */
	const postFile = (urlPost, dataPost, handleData) => {
		let timeReq = new Date();
		$.ajax({
	        url: urlPost  + "?frequest=" + String(timeReq.getTime()),
	        data: dataPost,
	        type: "post",
	        contentType: false, 
            processData: false,
	        cache: false,
	        success: function (data) {
	        	handleData(data);
	        },
            error: function(){
            	handleData("No se obtuvo nada");
            }
	      });
	};
	
	/**
	 * Funcion que ayuda a procesar informacion entre el cliente y servidor por metodo POST con ayuda de AJAX,
	 * pero la informacion que se devuelve es de tipo Blob, la cual contiene un archivo a descargar.
	 * @param {String} urlPost Es la cadena url que se usara en la peticion POST al servidor.
	 * @param {Object} dataPost Es el objeto que se desea pasar en la peticion POST al servidor.
	 * @param {Function} handleData Funcion que obtendra la respuesta de la peticion POST al servidor.
	 * @return {void} 
	 * @method postFileDownload
	 * @static
	 */
	const postFileDownload = (urlPost, dataPost, handleData) => {
		let timeReq = new Date();
		$.ajax({
			type: "POST",
	        url: urlPost  + "?frequest=" + String(timeReq.getTime()),
	        data: {obj: JSON.stringify(dataPost)},
    	    xhrFields: {
    	        responseType: 'blob' // to avoid binary data being mangled on charset conversion
    	    },
    	    success: function(blob, status, xhr) {
    	        // check for a filename
    	        let filename = "";
    	        let disposition = xhr.getResponseHeader('Content-Disposition');
    	        if (disposition && disposition.indexOf('attachment') !== -1) {
    	            let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
    	            let matches = filenameRegex.exec(disposition);
    	            if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
    	        }
	            var URL = window.URL || window.webkitURL;
	            var downloadUrl = URL.createObjectURL(blob);
	            if (filename) {
	                let a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
	            } 
    	    },
            error: function(){ 
            	handleData("No se obtuvo nada");
            }
		});
	};
	
	/**
	 * Funcion que ayuda a procesar informacion entre el cliente y servidor por metodo POST con ayuda de AJAX,
	 * pero la informacion que se devuelve es de tipo Blob, la cual contiene un archivo a descargar y la informacion que se manda es un archivo.
	 * @param {String} urlPost Es la cadena url que se usara en la peticion POST al servidor.
	 * @param {Object} dataPost Es el objeto que se desea pasar en la peticion POST al servidor.
	 * @return {void} 
	 * @method postSendFileDownloadFile
	 * @static
	 */
	const postSendFileDownloadFile = (urlPost, dataPost) => {
		let timeReq = new Date();
		$.ajax({
			type: "POST",
	        url: urlPost  + "?frequest=" + String(timeReq.getTime()),
	        data: dataPost,
	        contentType: false, 
            processData: false,
	        cache: false,
    	    xhrFields: {
    	        responseType: 'blob' // to avoid binary data being mangled on charset conversion
    	    },
    	    success: function(blob, status, xhr) {
    	    	let xMessage = xhr.getResponseHeader('X-Message');
    	    	if(xMessage.length > 0){
			    	let textoTit = "Mensaje de error";
					fcs.creaModalSuccesError(2, textoTit, xMessage, false, "");
			    }
    	        // check for a filename
    	        let filename = "";
    	        let disposition = xhr.getResponseHeader('Content-Disposition');
    	        if (disposition && disposition.indexOf('attachment') !== -1) {
    	            let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
    	            let matches = filenameRegex.exec(disposition);
    	            if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
    	        }
	            var URL = window.URL || window.webkitURL;
	            var downloadUrl = URL.createObjectURL(blob);
	            if (filename) {
	                let a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
	            }   
    	    },
            error: function(){
            	let textoTit = "Mensaje de error";
            	let msj = "No se obtuvo nada";
				fcs.creaModalSuccesError(2, textoTit, msj, false, "");
            }
		});
	};
	
	/**
	 * Funcion que ayuda a refrescar la informacion de las tablas de tipo DataTables.
	 * @param {String} nomT Nombre de la tabla a la que se le desean actualizar los datos en su DataTable
	 * @param {Object} datos Lista de datos a presentar en la tabla DataTable. 
	 * @return {void} 
	 * @method refrescaTabla
	 * @static
	 */
	const refrescaTabla = (nomT, datos) => {
		let table = $(nomT).DataTable();
		table.rows().remove().rows.add(datos).draw();
		table.rows().draw();
	};
	
	/**
	 * Funcion que ayuda a darle formato de tipo moneda o porcentaje al numero pasado.
	 * @param {String} valor Parametro que indica el numero deseado para dar formato.
	 * @param {int} opc Parametro que indica si se desea dar formato a una moneda o a un porcentaje (1- porcentajes, 2- monedas). 
	 * @return {String} Devuelve un numero con formato de moneda o de porcentaje. 
	 * @method moneyFormat
	 * @static
	 */
	const moneyFormat = (valor, opc) => {
		let numero = String(valor).replace(new RegExp("\,",'g'),"");
  		if($.isNumeric(numero)){
  			numero = parseFloat(numero); //Convertimos valor a flotante, como por ejemplo 8.846431261894337e-05 = 0.00008846431261894337
  			numero = String(numero); //Ahora si convertimos numero para tratarlo 
  			let minus = (numero.match("-") != null)?true:false;
  			numero = (minus)?numero.replace("-",""):numero;
			let hasDecimal = (numero.split(".").length == 2)?true:false;
			let newValor = (opc==1 && hasDecimal)?numero:parseFloat(numero).toFixed(2);
			let enteroDeci = newValor.split(".");
			let nums = enteroDeci[0].split("");
			let long = nums.length - 1; // Se saca la longitud del arreglo
			let patron = 3; //Indica cada cuanto se ponen las comas
			let prox = 2; // Indica en que lugar se debe insertar la siguiente coma
			let res = "";
			while (long > prox) {
				nums.splice((long - prox),0,","); //Se agrega la coma
				prox += patron; //Se incrementa la proxima posicion para colocar la coma
			}
			for (let i = 0; i <= nums.length-1; i++) {
				res += nums[i]; //Se crea la nueva cadena para devolver el valor formateado
			}
			return ((minus)?"-":"")+res+"."+enteroDeci[1];
  		}else{
  			return "";
  		}
	};
	
	/**
	 * Funcion que ayuda a crear validaciones para elementos de tipo input en el front.
	 * @param {Object} element Parametro que indica el objeto del DOM al que se le desea poner la validacion.
	 * @return {void} 
	 * @method validadorForm
	 * @static
	 */
	const validadorForm = (element) => {
		$(element).focus(function(){
			if(!$(this).hasClass("SIBA")){
				let valor = String($(this).val()).replace(new RegExp("\,|[$]",'g'),"");
				$(this).val(valor);
			}
		});
	
		$(element).focusout(function(){
			if(!$(this).hasClass("SIBA")){
				let valor = moneyFormat($(this).val(),(element==='.inputPorcentaje')?1:2);
				$(this).val(valor);
			}
		});
	
		$(element).keydown(function (e) {
			if(e.shiftKey){
				e.preventDefault();
			}else if((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 96 && e.keyCode <= 105) 
						|| e.keyCode === 8 || e.keyCode === 37 || e.keyCode === 39 || e.keyCode === 9 || e.keyCode === 46){
				return;
		    }else if(e.keyCode === 190 || e.keyCode === 110 || e.keyCode == 189 || e.keyCode == 109){
		    		if($(this).hasClass("SIBA")){
		    			e.preventDefault()
		    		}else{
		    			//Dejamos poner un solo punto decimal y un menos
		    			let mod = e.keyCode % 2;
		    			let sep = (mod == 0)?".":(mod==1)?"-":"";
		    			let tam = (String($(this).val()).split(sep)).length;
		    			(tam > 1)? e.preventDefault():"";
		    		}
		     }else{
		    	 e.preventDefault();
		     }
		});
	};
	
	/**
	 * Funcion que ayuda a quitar formato de moneda o porcentaje a algun numero para ser procesado posteriormente.
	 * @param {String} valor Parametro que indica el numero al que se le desea quitar el formato.
	 * @return {String} Devuelve el numero pasado sin comas ni simbolos especiales. 
	 * @method quitaFormato
	 * @static
	 */
	const quitaFormato = (valor) => String(valor).replace(new RegExp("\,|[$]",'g'),"");
	
	/**
	 * Funcion que ayuda a obtener una fecha.
	 * @param {int} dmenos Parametro que indica el numero de dias menos que necesitas de la fecha actual.
	 * @param {int} dmas Parametro que indica el numero de dias mas que necesitas de la fecha actual.
	 * @return {String} Se regresa la fecha solicitada. 
	 * @method fecha
	 * @static
	 */
	const fecha = (dmenos, dmas) => {
		let d = new Date();
		let month = d.getMonth()+1;
		let day = d.getDate() + dmenos + dmas;	
		return (day<10 ? '0' : '') + day + '/' +
		    (month<10 ? '0' : '') + month + '/' +
		     d.getFullYear();
	};
	
	/**
	 * Funcion que guarda una variable en la memoria local del cliente como tipo JSON. 
	 * @param {String} nomObj Parametro que indica el nombre de la variable.
	 * @param {Object} obj Parametro de tipo JSON que se desea guardar.
	 * @return {void}
	 * @method guardaVarLocal
	 * @static
	 */
	const guardaVarLocal = (nomObj, obj) => {
		localStorage.setItem(nomObj, JSON.stringify(obj));
	};
	
	/**
	 * Funcion que guarda una variable en la memoria local del cliente como tipo String. 
	 * @param {String} nomObj Parametro que indica el nombre de la variable.
	 * @param {String} obj Parametro de tipo String que se desea guardar.
	 * @return {void}
	 * @method guardaVarLocalS
	 * @static
	 */
	const guardaVarLocalS = (nomObj, obj) => {
		localStorage.setItem(nomObj, obj);
	};
	
	/**
	 * Funcion que obtine una variable que fue guardada en la memoria local del cliente como tipo JSON. 
	 * @param {String} nomObj Parametro que indica el nombre de la variable.
	 * @return {Object} Regresa un objeto de tipo JSON.
	 * @method getVarLocalJ
	 * @static
	 */
	const getVarLocalJ = (nomObj) => JSON.parse(localStorage.getItem(nomObj));
	
	/**
	 * Funcion que obtine una variable que fue guardada en la memoria local del cliente como tipo String. 
	 * @param {String} nomObj Parametro que indica el nombre de la variable.
	 * @return {String} Regresa el valor de la variable guardada.
	 * @method getVarLocalS
	 * @static
	 */
	const getVarLocalS = (nomObj) => localStorage.getItem(nomObj);
	
	/**
	 * Funcion que ayuda a crear un ToolTip en el elemento del DOM deseado, agregando estilo de error. 
	 * @param {Object} elem Parametro que contiene el elemento del DOM donde se desea crear el tooltip.
	 * @param {String} texto Parametro que contiene el contenido del tooltip a mostrar.
	 * @param {String} sideOp Parametro que indica la posicion donde se desea presentar el tooltip.
 	 * @return {void}
	 * @method creaTooltip
	 * @static
	 */
	const creaTooltip = (elem, texto, sideOp) => {
		$(elem).tooltipster({
			side: sideOp,
            content: '<strong>'+texto+'</strong>'
		});
		$(elem).addClass("estiloErrorInput");
	};
	
	/**
	 * Funcion que ayuda a crear un ToolTip en el elemento del DOM deseado. 
	 * @param {Object} elem Parametro que contiene el elemento del DOM donde se desea crear el tooltip.
	 * @param {String} texto Parametro que contiene el contenido del tooltip a mostrar.
	 * @param {String} sideOp Parametro que indica la posicion donde se desea presentar el tooltip.
 	 * @return {void}
	 * @method creaTooltipSM
	 * @static
	 */
	const creaTooltipSM = (elem, texto, sideOp) => {
		$(elem).tooltipster({
			side: sideOp,
            content: '<strong>'+texto+'</strong>'
		});
		$(elem).tooltipster('open');
	};
	
	/**
	 * Funcion que ayuda a crear un ToolTip en el elemento del DOM deseado, agregando estilo de warning. 
	 * @param {Object} elem Parametro que contiene el elemento del DOM donde se desea crear el tooltip.
	 * @param {String} texto Parametro que contiene el contenido del tooltip a mostrar.
	 * @param {String} sideOp Parametro que indica la posicion donde se desea presentar el tooltip.
 	 * @return {void}
	 * @method creaTooltipWarning
	 * @static
	 */
	const creaTooltipWarning = (elem, texto, sideOp) => {
		$(elem).tooltipster({
			side: sideOp,
			theme: 'tooltipster-warning',
            content: '<strong>'+texto+'</strong>'
		});
		$(elem).addClass("estiloWarning");
	};
	
	/**
	 * Funcion que ayuda a eliminar elementos del DOM de tipo Tooltip. 
	 * @param {Object} elem Parametro que contiene el elemento del DOM donde se desea eliminar el tooltip.
 	 * @return {void}
	 * @method destruyeTooltip
	 * @static
	 */
	const destruyeTooltip = (elem) => {
		$(elem).removeClass("estiloErrorInput");
		$(elem).removeClass("estiloWarning");
		$(elem).tooltipster('destroy');
	};
	
	/**
	 * Funcion que ayuda a buscar los roles posibles del validador.
	 * @param {String} nombreRol Parametro que contine el nombre del Rol.
 	 * @return {void}
	 * @method consultaRolesValidador
	 * @static
	 */
	const consultaRolesValidador = (nombreRol) => {
		let param = {
				nomRol: nombreRol
		}
		post("/buscaRol/",param, function(resp){
			try{
				let roles = resp.roles;
				guardaVarLocal("ids"+nombreRol,{"roles": roles})
			}catch(e){ console.log(e) }
		});
	};
	
	/**
	 * Funcion que ayuda a convertir los numeros a romanos.
	 * @param {String} num Parametro que contine el numero que se desea convertir a romano.
 	 * @return {String} Se regresa el numero romano.
	 * @method numToRoman
	 * @static
	 */
	const numToRoman = (num) => {
	    if (isNaN(num))
	        return NaN;
	    let digits = String(+num).split(""),
	        key = ["","C","CC","CCC","CD","D","DC","DCC","DCCC","CM",
	               "","X","XX","XXX","XL","L","LX","LXX","LXXX","XC",
	               "","I","II","III","IV","V","VI","VII","VIII","IX"],
	        roman = "",
	        i = 3;
	    while (i--)
	        roman = (key[+digits.pop() + (i * 10)] || "") + roman;
	    return Array(+digits.join("") + 1).join("M") + roman;
	};
	
	/**
	 * Funcion que ayuda a recargar la pagina del sistema PF.
 	 * @return {void}
	 * @method recargaPagina
	 * @static
	 */
	const recargaPagina = () => {
		let param = {
				token: $("#token").html()
		}
		post("/recargaPagina/",param, function(resp){
				location.reload(true);
				solTomoII.cargaMenuIniBotones();
		});
	};
	
	/**
	 * Funcion que ayuda a poner propiedades a elementos del DOM.
	 * @param {Object} objE Lista de elementos a los que se les desea asignar la propiedad.
	 * @param {String} propN Nombre de la propiedad para asignar a los elementos.
	 * @param {Object} valProp Valor de la propiedad que se desea asignar a los elementos. 
 	 * @return {void}
	 * @method setPropElems
	 * @static
	 */
	const setPropElems = (objE, propN, valProp) => {
		for(idx in objE){
			$(objE[idx]).prop(propN,valProp).trigger("change");
		}
	};
	
	/**
	 * Funcion que ayuda a inicializar las caracteristicas por default de los elementos de tipo Select2, y crear elementos select2.
	 * @param {Object} obj Parametro que contiene el elemento que se desea inicializar como tipo Select2.
	 * @param {Object} datos Parametro que contiene la lista de datos que se presentaran en el elemento select.
	 * @param {int} search Parametro que indica el numero minimo de letras que se requieren para realizar la busqueda de elementos entre la lista.
	 * @return {void} 
	 * @method select2
	 * @static
	 */
	const select2 = (obj, datos, search) => {
		$(obj).empty();
		$(obj).select2({
			minimumResultsForSearch: search,
			data: datos,
			dropdownAutoWidth : true,
		    language: {
				  noResults: function() { return "Sin coincidencias =("; },
				  searching: function() { return "Buscando..."; }
			},
		});		
	};
	
	/**
	 * Funcion que genera modal de error o de exito con especificaciones especiales.
	 * @param {int} opc Parametro que indica si se desea tratar como modal de error o de exito.
	 * @param {String} textHeader Parametro que indica el titulo del modal.
	 * @param {String} textBody Parametro que contiene el mensaje que se desea poner en el cuerpo del modal.
	 * @param {Boolean} especial Booleano que indica si se desea hacer un trato especial al elemento al dar click.
	 * @param {Object} funcionAccion Funcion que sera aplicada al dar click.
	 * @param {int} numElem Parametro que indica el numero de elementos de la funcion destino que se desean aplicar.
	 * @param {Object} arg1 Objecto de la primera entrada a la funcion destino.
	 * @param {Object} arg2 Objecto de la segunda entrada a la funcion destino.
	 * @return {void} 
	 * @method creaModalSuccesError
	 * @static
	 */
	const creaModalSuccesError = (opc, textHeader, textBody, especial, funcionAccion, numElem = 0 , arg1 = "", arg2 = "") => {
		let idModal = "#modalRespGuardar";
		$(idModal + " .modal-title").html(textHeader);
		$(idModal + " .modal-header").removeClass((opc==1)?"headerModalError":"headerModalSucess");
		$(idModal + " .modal-header").addClass((opc==1)?"headerModalSucess":"headerModalError");
		$(idModal + " .textoBody").html(textBody);
		$(idModal + " .modal-body button").attr('class',(opc==1)?'btn btn-success':'btn btn-danger');
		$(idModal + " .close").addClass('regresarEspe');
		$(idModal + " .modal-body button").addClass('regresarEspe');
		comunE.eventoEspecial(".regresarEspe", idModal, especial, funcionAccion, numElem, arg1, arg2);
		$(idModal).modal('show');
		fComun.ocultarEspera();
	};
	
	/**
	 * Funcion que genera un modal de alerta.
	 * @param {String} textHeader Parametro que indica el titulo del modal.
	 * @param {String} textBody Parametro que contiene el mensaje que se desea poner en el cuerpo del modal.
	 * @param {Object} funcionAccion Funcion que sera aplicada al dar click.
	 * @param {int} numParam Parametro que indica el numero de elementos de la funcion destino que se desean aplicar.
	 * @param {Object} param1 Objecto de la primera entrada a la funcion destino.
	 * @param {Object} param2 Objecto de la segunda entrada a la funcion destino.
	 * @return {void} 
	 * @method creaModalAlerta
	 * @static
	 */
	const creaModalAlerta = (textHeader, textBody, funcionAccion, numParam, param1, param2) => {
		let idModal = "#modalAlerta";
		$(idModal + " .modal-title").html(textHeader);
		$(idModal + " .textoBody").html("<strong>"+textBody+"</strong><br>");
		$(idModal + " .close").addClass('regresarEspe');
		$(idModal + " .modal-body .btn-secondary").addClass('regresarEspe letraBlanca').html("<strong>Cancelar</strong>");
		$(idModal + " .modal-body .btn-warning").addClass('confirmAccion letraBlanca').html("<strong>Confirmar</strong>");
		comunE.eventoEspecial(".regresarEspe",idModal,false,"",0,"","");
		comunE.eventoEspecial(".confirmAccion", idModal, true, funcionAccion, numParam, param1, param2);
		$(idModal).modal('show');
		fComun.ocultarEspera();
	};
	
	/**
	 * Funcion que apoya a eliminar un registro de la tabla que se esta trabajando. 
	 * @param {Object} elem Parametro que contiene el objeto del elemento que sera procesado.
	 * @param {String} nomTabla Parametro que contiene el id de la tabla donde se eliminara registro.
	 * @return {void} 
	 * @method eliminaRegTabla
	 * @static
	 */
	const eliminaRegTabla = (elem, nomTabla) => {
		let table = $(nomTabla).DataTable();
		let idxCell = table.cell($(elem).parent()).index()
		let renglon = idxCell.row;
		table.row(renglon).remove().draw();
	};
	
	return{
		post: post,
		refrescaTabla: refrescaTabla,
		postFile: postFile,
		moneyFormat: moneyFormat,
		validadorForm: validadorForm,
		post2: post2,
		quitaFormato: quitaFormato,
		mostrarEspera: mostrarEspera,
		ocultarEspera: ocultarEspera,
		guardaVarLocal: guardaVarLocal,
		guardaVarLocalS: guardaVarLocalS,
		getVarLocalJ: getVarLocalJ,
		getVarLocalS: getVarLocalS,
		initDefault: initDefault,
		urlsAjax: urlsAjax,
		creaTooltip: creaTooltip,
		destruyeTooltip: destruyeTooltip,
		consultaRolesValidador: consultaRolesValidador,
		numToRoman: numToRoman,
		fecha: fecha,
		creaTooltipSM: creaTooltipSM,
		recargaPagina: recargaPagina,
		setPropElems: setPropElems,
		creaTooltipWarning: creaTooltipWarning,
		select2: select2,
		postFileDownload: postFileDownload,
		postSendFileDownloadFile: postSendFileDownloadFile,
		creaModalSuccesError: creaModalSuccesError,
		creaModalAlerta: creaModalAlerta,
		iniciaModalComentarios: iniciaModalComentarios,
		eliminaRegTabla: eliminaRegTabla
	}
}();