/**
 * etii es un modulo que hace el trabajo de una Clase, es decir, funciona como Clase.
 * Esta clase nos apoya con los eventos que se estaran usando en el front del sistema SIPEFI-TOMO II.
 * @module etii
 */

const etii = function(){
	
	let listaTemas = [];       // [{ id, nombre, horas, objetivo }]
	let listaContenidos = [];  // [{ idTema, texto }] ... [{ idTema, texto, idContenido }]:  idContenido prop is added on reconstruirDesdeEstructuras
	let contadorTemas = 1;
	let temaForEdit = [];
	let contenidoForEdit = [];
	let isActionEditingTema = false;
	let isActionEditingContenido = false;
	let isActionEditingBibliografia = false;
	
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
	  const totalTeo  = (parseInt($("#h_semestre_teo").val() , 10)
		  						+ parseInt($("#h_semestre_pra").val() , 10)) || 0;
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
			}, 12000);
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
	
	    listaContenidos.push({ idTema, texto });
	
	    $("#contenidoTema").val(""); // Limpiar campo
	    let option = $("#temaContenido").val();
	    reconstruirDesdeEstructuras();
	    $("#temaContenido").val(option);
	  };
	
	  /**
	   * Reconstruye las tablas y el select desde las estructuras de datos.
	   */
	  const reconstruirDesdeEstructuras = () => {
	    const tablaTemasDT = $('#tablaTemas').DataTable();
	    const tablaContenidosDT = $('#tablaContenidos').DataTable();
		const isVisible = parseInt(fComun.getVarLocalS("accionSoli"));
		let visible = '';
		if (isVisible===1){
			visible = 'hidden'; //Se ocultan las acciones si esta en modo visulaizador
		}
	
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
	        `<div ${visible}>
				<button class="btn btn-danger btn-sm" onclick="etii.eliminarTema(${tema.id})">
				   <i class="fas fa-trash-alt"></i>
				 </button>
				 <button class="btn btn-danger btn-sm" onclick="etii.editarTema(${tema.id})" id = "btnEdit-${tema.id}">
				   <i class="fas fa-edit"></i>
				 </button>
				 <button class="btn btn-danger btn-sm" onclick="etii.saveTema(${tema.id})" id = "btnSave-${tema.id}" hidden="true">
				   <i class="fas fa-save"></i>
				 </button>
			</div>`
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
		  const idContenido = numTema + "." + numContenido;

		  contenido.idContenido = idContenido;

	      const fila = [
	        `${numTema}. ${nombreTema}`,
	        `${idContenido}`,
	        contenido.texto,
			`<div ${visible}>
				<button class="btn btn-danger btn-sm" onclick="etii.eliminarContenido(this)">
			     <i class="fas fa-trash-alt"></i>
			   	</button>
				<button class="btn btn-danger btn-sm" onclick="etii.editarContenido(${numTema},${numContenido})" id = "btnEdit-${idContenido}">
					 <i class="fas fa-edit"></i>
				</button>
				<button class="btn btn-danger btn-sm" onclick="etii.saveContenido(${numTema},${numContenido})" id = "btnSave-${idContenido}" hidden="true">
					 <i class="fas fa-save"></i>
				</button>
			</div>`
	      ];
	
	      const row = tablaContenidosDT.row.add(fila).draw(false);
	      $(row.node()).attr("data-idtema", contenido.idTema);
	
	      contadorPorTema[contenido.idTema]++;
	    });
		
		actualizaHorasTeoricasRestantes();
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

	  const editarTema = (id) => {
	    const tieneContenido = listaContenidos.some(c => c.idTema === id);
		if(!isActionEditingTema){
			temaForEdit = listaTemas.find(t => t.id === id);
			var nombre_tema = temaForEdit.nombre;
			var nombre_tema_id = "id_nombre_tema-" + id;
			var horas_tema = temaForEdit.horas;
			var horas_tema_id = "id_horas_tema-" + id;
			var objetivo_tema = temaForEdit.objetivo;
			var objetivo_tema_id = "id_objetivo_tema-" + id;
			temaForEdit.nombre = `<input type="text" class="form-control" value="${nombre_tema}" id = "${nombre_tema_id}">`;
			temaForEdit.horas = `<input type="number" class="form-control" value="${horas_tema}" id = "${horas_tema_id}">`;
			temaForEdit.objetivo = `<input type="text" class="form-control" value="${objetivo_tema}" id = "${objetivo_tema_id}">`;
			reconstruirDesdeEstructuras();
			document.getElementById("btnEdit-"+id).hidden = true;
			document.getElementById("btnSave-"+id).hidden = false;
			$('.menuBotones[target="guardarSolicitud"]').prop('disabled', true);
			isActionEditingTema = !isActionEditingTema;
		}

	  };

	  const saveTema = (id) => {
		  if(isActionEditingTema){
			  temaForEdit = listaTemas.find(t => t.id === id);
			 var input_nombre = document.getElementById("id_nombre_tema-"+id);
			 var input_horas = document.getElementById("id_horas_tema-"+id);
			 var input_objetivo = document.getElementById("id_objetivo_tema-"+id);

			 temaForEdit.nombre = input_nombre.value;
			 temaForEdit.horas = input_horas.value;
			 temaForEdit.objetivo = input_objetivo.value;

			reconstruirDesdeEstructuras();
			document.getElementById("btnEdit-"+id).hidden = false;
			document.getElementById("btnSave-"+id).hidden = true;
			$('.menuBotones[target="guardarSolicitud"]').prop('disabled', false);
			isActionEditingTema = !isActionEditingTema;
		  }
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

	const editarContenido = (numTema, numContenido) => {
		const temaStr = String(numContenido);
		const idContenido = ""+numTema+"."+temaStr;
		if(!isActionEditingContenido){
		  contenidoForEdit = listaContenidos.find(c => c.idContenido === idContenido);
		  var contenido = contenidoForEdit.texto;
		  var contenido_id = "id_contenido-" + idContenido;
		  contenidoForEdit.texto = `<input type="text" class="form-control" value="${contenido}" id = "${contenido_id}">`;
		  reconstruirDesdeEstructuras();
		  document.getElementById("btnEdit-"+idContenido).hidden = true;
		  document.getElementById("btnSave-"+idContenido).hidden = false;
		  $('.menuBotones[target="guardarSolicitud"]').prop('disabled', true);
		  isActionEditingContenido = !isActionEditingContenido;
		}
	};

	const saveContenido = (numTema, numContenido) => {
		const temaStr = String(numContenido);
		const idContenido = ""+numTema+"."+temaStr;
  		if(isActionEditingContenido){
			contenidoFordit = listaContenidos.find(c => c.idContenido === idContenido);
			var input_contenido = document.getElementById("id_contenido-"+idContenido);
			contenidoForEdit.texto = input_contenido.value;
			reconstruirDesdeEstructuras();
			document.getElementById("btnEdit-"+idContenido).hidden = false;
			document.getElementById("btnSave-"+idContenido).hidden = true;
			$('.menuBotones[target="guardarSolicitud"]').prop('disabled', false);
			isActionEditingContenido = !isActionEditingContenido;
		  }
	};

const editarBibliografia = (idBibliografia) => {
		if(!isActionEditingBibliografia) {

			var bibliografiaTable = $('#tablaBibliografia').DataTable();

			var varHandler = bibliografiaTable.cell(idBibliografia - 1, 1).data();
			var autorForEdit = varHandler ? varHandler : "";
			var autorForEdit_input = `<span class="text-start">${autorForEdit}</span>`;

			varHandler = bibliografiaTable.cell(idBibliografia - 1, 2).data();
			var yearForEdit = (varHandler === '0' || varHandler === 0) ? "" : (varHandler ? varHandler : "");
			var yearForEdit_input = `<span class="text-start">${yearForEdit}</span>`;


			varHandler = bibliografiaTable.cell(idBibliografia - 1, 3).data();
			var isComplementaria = (varHandler === "Complementaria" )? true : false;
			var clasificacionForEdit_input = `<select id = "id-biblio-clasificacion-${idBibliografia}" className="form-select">
				<option value="0" ${(!isComplementaria)? "selected" : ""}>Básica</option>
				<option value="1" ${(isComplementaria)? "selected" : ""}>Complementaria</option>
			</select>`;

			varHandler = bibliografiaTable.cell(idBibliografia - 1, 4).data();
			var tituloForEdit = varHandler ? varHandler : "";
			var tituloForEdit_input = `<span class="text-start">${tituloForEdit}</span>`;


			varHandler = bibliografiaTable.cell(idBibliografia - 1, 5).data();
			var extra1ForEdit = varHandler ? varHandler : "";
			var extra1ForEdit_input = `<span class="text-start">${extra1ForEdit}</span>`;


			varHandler = bibliografiaTable.cell(idBibliografia - 1, 6).data();
			var extra2ForEdit = varHandler ? varHandler : "";
			var extra2ForEdit_input = `<span class="text-start">${extra2ForEdit}</span>`;


			varHandler = bibliografiaTable.cell(idBibliografia - 1, 7).data();
			var extra3ForEdit = varHandler ? varHandler : "";
			var extra3ForEdit_input = `<span class="text-start">${extra3ForEdit}</span>`;


			varHandler = bibliografiaTable.cell(idBibliografia - 1, 8).data();
			var extra4ForEdit = varHandler ? varHandler : "";
			var extra4ForEdit_input = `<span class="text-start">${extra4ForEdit}</span>`;


			varHandler = bibliografiaTable.cell(idBibliografia - 1, 9).data();
			var temasForEdit = varHandler ? varHandler : "";
			var temasForEdit_input = `<input type="text" class="form-control" value="${temasForEdit}" id="id-biblio-temas-${idBibliografia}">`;

			varHandler = bibliografiaTable.cell(idBibliografia - 1, 0).data();
			var tipoNoEdit = varHandler ? varHandler : "";
			var tipoNoEdit_input = `<input type="text" class="border-0 bg-transparent" value="${tipoNoEdit}" disabled>`;

			var buttons = `<div>
						<button class="btn btn-sm btn-danger btn-eliminar-biblio"><i class="fas fa-trash-alt"></i></button>
						<button class="btn btn-sm btn-danger" id = "bibliografia-btnedit-${idBibliografia}" onclick="etii.editarBibliografia(${idBibliografia})" hidden><i class="fas fa-edit"></i></button>
						<button class="btn btn-sm btn-danger" id = "bibliografia-btnsave-${idBibliografia}" onclick="etii.saveBibliografia(${idBibliografia})"><i class="fas fa-save"></i></button>
					</div>`;

			bibliografiaTable.row(idBibliografia-1).data([tipoNoEdit_input,autorForEdit_input,yearForEdit_input,
				clasificacionForEdit_input,tituloForEdit_input,extra1ForEdit_input,extra2ForEdit_input,
				extra3ForEdit_input,extra4ForEdit_input, temasForEdit_input,buttons]).draw(false);

			$('.menuBotones[target="guardarSolicitud"]').prop('disabled', true);
			isActionEditingBibliografia = !isActionEditingBibliografia;

		}
	};

	const saveBibliografia = (idBibliografia) => {
		if (isActionEditingBibliografia) {
			const bibliografiaTable = $('#tablaBibliografia').DataTable();

			var varHandler = $(bibliografiaTable.cell(idBibliografia-1, 0).node()).find('input').val();
			const tipoNoEdit = varHandler ? varHandler : "";

			 varHandler = $(bibliografiaTable.cell(idBibliografia-1, 1).node()).find('input').val();
			const autorForEdit = varHandler ? varHandler : "";

			varHandler = $(bibliografiaTable.cell(idBibliografia-1, 2).node()).find('input').val();
			const yearForEdit = (!varHandler || varHandler === '0') ? "" : varHandler;

			varHandler = $(bibliografiaTable.cell(idBibliografia-1, 4).node()).find('input').val();
			const tituloForEdit = varHandler ? varHandler : "";

			varHandler = $(bibliografiaTable.cell(idBibliografia-1, 5).node()).find('input').val();
			const extra1ForEdit = varHandler ? varHandler : "";

			varHandler= $(bibliografiaTable.cell(idBibliografia-1, 6).node()).find('input').val();
			const extra2ForEdit =  varHandler ? varHandler : "";

			varHandler = $(bibliografiaTable.cell(idBibliografia-1, 7).node()).find('input').val();
			const extra3ForEdit = varHandler ? varHandler : "";

			varHandler = $(bibliografiaTable.cell(idBibliografia-1, 8).node()).find('input').val();
			const extra4ForEdit = varHandler ? varHandler : "";

			varHandler = $(bibliografiaTable.cell(idBibliografia-1, 9).node()).find('input').val();
			const temasForEdit = varHandler ? varHandler : "";


			const clasificacionForEdit_selected = document.getElementById("id-biblio-clasificacion-"+idBibliografia).value;
			const clasificacionForEdit_input = (clasificacionForEdit_selected === "0")? "B&aacute;sica" : "Complementaria";

			var buttons = `<div>
						<button class="btn btn-sm btn-danger btn-eliminar-biblio"><i class="fas fa-trash-alt"></i></button>
						<button class="btn btn-sm btn-danger" id = "bibliografia-btnedit-${idBibliografia}" onclick="etii.editarBibliografia(${idBibliografia})"><i class="fas fa-edit"></i></button>
						<button class="btn btn-sm btn-danger" id = "bibliografia-btnsave-${idBibliografia}" onclick="etii.saveBibliografia(${idBibliografia})" hidden><i class="fas fa-save"></i></button>
					</div>`;


			bibliografiaTable.row(idBibliografia-1).data([tipoNoEdit,autorForEdit,yearForEdit,
				clasificacionForEdit_input,tituloForEdit,extra1ForEdit,extra2ForEdit,
				extra3ForEdit,extra4ForEdit, temasForEdit,buttons]).draw(false);

			$('.menuBotones[target="guardarSolicitud"]').prop('disabled', false);
			isActionEditingBibliografia = !isActionEditingBibliografia;
		}
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