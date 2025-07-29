/**
 * fl es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos apoya con la inicializacion de los objetos que provienen de alguna libreria,
 * como por ejemplo DataTables.
 * @module fl
 */
const fl = function(){
	
	/**
	 * Funcion que ayuda a inicializar las tablas de tipo DataTable que se usaran en la primera vista,
	 * donde se presentan las tablas de las solicitudes en proceso o procesadas, para busqueda de solicitudes, inicializacion por default parametros datatables.
	 * @return {void} 
	 * @method cargaTablasP1
	 * @static
	 */
	const cargaTablasP1 = () => {
		/****
		 * inicializacion por default datatables
		 ****/
		$.extend( true, $.fn.dataTable.defaults, {
			"fixedHeader": true,
			"colReorder": false,
			"ordering": false,
            "lengthMenu": [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "Todos"] ],
			"dom": '<"tituloTablas esconder">frtlip',
			"info":     false,
			"language": {
				"url": rutaIdiomaDT
			}
		} );
		
		$('#tablaSoliUsuario').DataTable({
			"pageLength": 5,
			"columnDefs": [
				{
					"className": "centrar",
	                "targets": "_all"
	            },
	            {
	                "targets": [ 7 ],
	                "visible": false,
	                "searchable": false
	            },
	            {
	            	 "width": "15%", 
	            	 "targets": [3] 
	            },
	            {
	            	 "width": "10%", 
	            	 "targets": [0,2,4,5,6] 
	            },
	            {
	            	"render": function ( data, type, row ) {
	            		let rolSol = parseInt(row[7].split("#@@#")[6]);
	            		let rol = parseInt($("#rol").html());
	            		let estatusSoli = parseInt(row[7].split("#@@#")[1]);
	            		let minusRol =  rol - rolSol;
	            		let canEdit = (minusRol==0||minusRol==1)?true:false;
	            		let infoExtra = (canEdit)?"__1":"";
	            		let selectItem = "<select class='accionSolicitud'>"+
	            							"<option value='0' selected>Elige acci&oacute;n..</option>"+
	            							"<option value='1__"+row[7]+(estatusSoli==3?"__1":infoExtra)+"'>Visualizar</option>"+
	            							((canEdit)?"<option value='2__"+row[7]+infoExtra+"'>Editar</option>":"")+
	            						"</select>";
	                    return selectItem;
	                },
	                "targets": 6
	            }
	         ],
	         "fnCreatedRow": function( nRow, aData, iDataIndex ) {
	        	    if ( String(aData[1]).length > 20 ) {
	        	      $('td:eq(1)', nRow).html( String(aData[1]).substr(0,20) + " . .");
	        	      if(!$('td:eq(1)', nRow).hasClass("tooltipstered")){
							$('td:eq(1)', nRow).tooltipster({
									side: 'top',
									theme: 'tooltipster-noir',
									animation: 'fade',
									contentAsHTML: 'true',
						            content: '<strong>'+aData[1]+'</strong>',
						            trigger: 'custom',
									triggerOpen: {
									        mouseenter: true,
									        tap: true
									},
									triggerClose: {
									        mouseleave: true,
									        tap: true
									}
							});
						}
	        	    }
	          },
	          "rowCallback": function( row, data ) {
	        	    if ( String(data[1]).length > 20 ) {
	        	      $('td:eq(1)', row).html( String(data[1]).substr(0,20) + " . .");
	        	      if(!$('td:eq(1)', row).hasClass("tooltipstered")){
							$('td:eq(1)', row).tooltipster({
									side: 'top',
									theme: 'tooltipster-noir',
									animation: 'fade',
									contentAsHTML: 'true',
						            content: '<strong>'+data[1]+'</strong>',
						            trigger: 'custom',
									triggerOpen: {
									        mouseenter: true,
									        tap: true
									},
									triggerClose: {
									        mouseleave: true,
									        tap: true
									}
							});
						}
	        	    }
	          }
		});
		
		$('#tablaSoliAvanzadas').DataTable({
			"pageLength": 5,
			"columnDefs": [
				{
					"className": "centrar",
	                "targets": "_all"
	            },
	            {
	                "targets": [ 7 ],
	                "visible": false,
	                "searchable": false
	            },
	            {
	            	 "width": "15%", 
	            	 "targets": [3] 
	            },
	            {
	            	 "width": "10%", 
	            	 "targets": [0,2,4,5,6] 
	            },
	            {
	            	"render": function ( data, type, row ) {
	            		let ESoli = String(row[7]).split("#@@#");
	            		let opSelect ="<option value='0' selected>Elige estatus..</option>";
	            		for(i in ESoli){
	            			let obj = String(ESoli[i]).split("||");
	            			let val = "1__" + String(obj[0]).replace("-","#@@#");
	            			let text = obj[1];
	            			opSelect += "<option value='"+val+"'>"+text+"</option>";
	            		}
	            		let selectItem = "<select class='accionSolicitud'>"+
	            							opSelect+
	            						"</select>";
	                    return selectItem;
	                },
	                "targets": 6
	            }
	         ],
	         "fnCreatedRow": function( nRow, aData, iDataIndex ) {
	        	    if ( String(aData[1]).length > 20 ) {
	        	      $('td:eq(1)', nRow).html( String(aData[1]).substr(0,20) + " . .");
	        	      if(!$('td:eq(1)', nRow).hasClass("tooltipstered")){
							$('td:eq(1)', nRow).tooltipster({
									side: 'top',
									theme: 'tooltipster-noir',
									animation: 'fade',
									contentAsHTML: 'true',
						            content: '<strong>'+aData[1]+'</strong>',
						            trigger: 'custom',
									triggerOpen: {
									        mouseenter: true,
									        tap: true
									},
									triggerClose: {
									        mouseleave: true,
									        tap: true
									}
							});
						}
	        	    }
	          },
	          "rowCallback": function( row, data ) {
	        	    if ( String(data[1]).length > 20 ) {
	        	      $('td:eq(1)', row).html( String(data[1]).substr(0,20) + " . .");
	        	      if(!$('td:eq(1)', row).hasClass("tooltipstered")){
							$('td:eq(1)', row).tooltipster({
									side: 'top',
									theme: 'tooltipster-noir',
									animation: 'fade',
									contentAsHTML: 'true',
						            content: '<strong>'+data[1]+'</strong>',
						            trigger: 'custom',
									triggerOpen: {
									        mouseenter: true,
									        tap: true
									},
									triggerClose: {
									        mouseleave: true,
									        tap: true
									}
							});
						}
	        	    }
	          }
		});
		
		$('#tablaSoliRecientes').DataTable({
			"pageLength": 5,
			"columnDefs": [
				{
					"className": "centrar",
	                "targets": "_all"
	            },
	            {
	                "targets": [ 7 ],
	                "visible": false,
	                "searchable": false
	            },
	            {
	            	 "width": "15%", 
	            	 "targets": [3] 
	            },
	            {
	            	 "width": "10%", 
	            	 "targets": [0,2,4,5,6] 
	            },
	            {
	            	"render": function ( data, type, row ) {
	            		let selectItem = "<select class='accionSolicitud'>"+
	            							"<option value='0' selected>Elige acci&oacute;n..</option>"+
	            							"<option value='1__"+row[7]+"'>Visualizar</option>"+
	            						"</select>";
	                    return selectItem;
	                },
	                "targets": 6
	            }
	         ],
	         "fnCreatedRow": function( nRow, aData, iDataIndex ) {
	        	    if ( String(aData[1]).length > 20 ) {
	        	      $('td:eq(1)', nRow).html( String(aData[1]).substr(0,20) + " . .");
	        	      if(!$('td:eq(1)', nRow).hasClass("tooltipstered")){
							$('td:eq(1)', nRow).tooltipster({
									side: 'top',
									theme: 'tooltipster-noir',
									animation: 'fade',
									contentAsHTML: 'true',
						            content: '<strong>'+aData[1]+'</strong>',
						            trigger: 'custom',
									triggerOpen: {
									        mouseenter: true,
									        tap: true
									},
									triggerClose: {
									        mouseleave: true,
									        tap: true
									}
							});
						}
	        	    }
	          },
	          "rowCallback": function( row, data ) {
	        	    if ( String(data[1]).length > 20 ) {
	        	      $('td:eq(1)', row).html( String(data[1]).substr(0,20) + " . .");
	        	      if(!$('td:eq(1)', row).hasClass("tooltipstered")){
							$('td:eq(1)', row).tooltipster({
									side: 'top',
									theme: 'tooltipster-noir',
									animation: 'fade',
									contentAsHTML: 'true',
						            content: '<strong>'+data[1]+'</strong>',
						            trigger: 'custom',
									triggerOpen: {
									        mouseenter: true,
									        tap: true
									},
									triggerClose: {
									        mouseleave: true,
									        tap: true
									}
							});
						}
	        	    }
	          }
		});
	};
	
	/**
	 * Funcion que ayuda a inicializar las tablas de tipo DataTable que se usaran en la vista de solicitud,
	 * donde se presentan las tablas de cada seccion de solicitudes
	 * @return {void} 
	 * @method cargaTablasSolicitud
	 * @static
	 */
	const cargaTablasSolicitud = () => {
		$('#tablaTemas').DataTable({
			"dom": 'ftpir',
			"pageLength": 6
		  });

		  $('#tablaContenidos').DataTable({
			"dom": 'ftpir',
			"pageLength": 6
		  });
		  
		  $('#tablaRelacionesLic').DataTable({
  			"dom": 'ftpir',
  			"pageLength": 6
  		  });
		  
		  $('#tablaBibliografia').DataTable({
			"dom": 'ftpir',
			"pageLength": 6
		  });
	};		
	
	/**
	 * Funcion que ayuda a inicializar las caracteristicas por default de los elementos de tipo Tooltipster.
	 * @return {void} 
	 * @method defaultTooltipster
	 * @static
	 */
	const defaultTooltipster = () => {
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
	  const $element = $(obj);
	  $element.empty();

	  const $parentModal = $element.closest('.modal');

	  const config = {
	    data: datos,
	    minimumResultsForSearch: search,
	    dropdownAutoWidth: true,
	    width: '100%',
	    language: {
	      noResults: function() { return "Sin coincidencias =("; },
	      searching: function() { return "Buscando..."; }
	    }
	  };

	  // Solo agrega dropdownParent si está dentro de un modal
	  if ($parentModal.length) {
	    config.dropdownParent = $parentModal;
	  }

	  $element.select2(config);
	};
	
	return{
		cargaTablasP1:	cargaTablasP1,
		defaultTooltipster: defaultTooltipster,
		select2:	select2,
		cargaTablasSolicitud:	cargaTablasSolicitud
	}
}();