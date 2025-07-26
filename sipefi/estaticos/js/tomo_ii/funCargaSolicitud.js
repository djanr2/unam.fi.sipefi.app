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
			// Cargar combos del tab "Datos generales"
			llenaCombo("area_con", obj.catAreaCon || [], false);
			llenaCombo("modalidad", obj.catModalidad || [], false);
			llenaCombo("tipo_modalidad", obj.catTipoMod || [], false);
			llenaCombo("caracter", obj.catCarAsig || [], false);

			// Cargar combos del tab "Relación con Licenciaturas"
			llenaCombo("rel_licenciatura", obj.catLic || [], false);
			llenaCombo("rel_semestre", [...Array(10).keys()].map(i => [i + 1, `Semestre ${i + 1}`]), false); // del 1 al 10
			llenaCombo("ser_anterior", obj.catAsig || [], true);
			llenaCombo("ser_consecuente", obj.catAsig || [], true);
		}catch(e){console.error("Error al cargar catálogos:", e);}
		cssVistaCaptura();
	};
	
	/**
	 * Llena un select a partir de un catálogo tipo array bidimensional.
	 * @param {string} idSelector - ID del select sin "#"
	 * @param {Array} datos - Array de arrays [valor, texto]
	 * @param {boolean} [conElige=true] - Si se incluye opción por default
	 */
	const llenaCombo = (idSelector, datos, conElige = true) => {
		try {
			let $combo = $("#" + idSelector);
			$combo.empty();
			if (conElige) {
				$combo.append('<option value="">Elige una opción</option>');
			}
			datos.forEach(([val, txt]) => {
				$combo.append(`<option value="${val}">${txt}</option>`);
			});
		} catch (e) {
			console.error("Error llenando combo:", idSelector, e);
		}
	};
	
	/**
	 * Función que agrega una nueva relación con licenciatura si es válida y no duplicada.
	 * @function agregarRelacionLicAsig
	 */
	const agregarRelacionLicAsig = () => {
	  const idLic = $("#rel_licenciatura").val();
	  const txtLic = $("#rel_licenciatura option:selected").text().trim();
	  const semestre = $("#rel_semestre").val();
	  const serAnt = $("#ser_anterior").val();
	  const serCon = $("#ser_consecuente").val();
	  const txtAnt = $("#ser_anterior option:selected").text().trim();
	  const txtCon = $("#ser_consecuente option:selected").text().trim();

	  // Validaciones
	  if (!idLic || idLic === "0") {
	    fComun.mostrarTooltipCampo("#rel_licenciatura", "Selecciona una licenciatura válida");
	    return;
	  }

	  if (!semestre) {
	    fComun.mostrarTooltipCampo("#rel_semestre", "Selecciona el semestre");
	    return;
	  }

	  // Validación de igualdad solo si ambas existen
	  if (serAnt && serCon && serAnt === serCon) {
	    fComun.mostrarTooltipCampo("#ser_consecuente", "No puede ser igual a la seriación anterior");
	    return;
	  }

	  // Evitar duplicados en la tabla
	  let existe = false;
	  $("#tablaRelaciones tr").each(function () {
	    const tdLic = $(this).find("td").eq(0).text().trim();
	    if (tdLic === txtLic) {
	      existe = true;
	      return false;
	    }
	  });

	  if (existe) {
	    fComun.mostrarTooltipCampo("#rel_licenciatura", "Ya existe la relaci&oacute;n de la licenciatura.");
	    return;
	  }
	  
	  // Mostrar texto solo si el valor es distinto de 0
	  const mostrarTexto = (valor, texto) => {
	  	return valor && valor !== "0" ? texto : '';
	  };
	
	  const mostrarAnt = mostrarTexto(serAnt, txtAnt);
	  const mostrarCon = mostrarTexto(serCon, txtCon);

	  // Fila para tabla
	  const fila = `
	    <tr>
	      <td>${txtLic}</td>
	      <td>${semestre}</td>
	      <td>${mostrarAnt}</td>
	      <td>${mostrarCon}</td>
	      <td class="text-center">
	        <button class="btn btn-sm btn-danger" onclick="$(this).closest('tr').remove();">
	          <i class="fas fa-trash-alt"></i>
	        </button>
	      </td>
	    </tr>`;

	  $("#tablaRelaciones").append(fila);

	  // Limpiar campos
	  $("#rel_licenciatura").val("0");
	  $("#rel_semestre").val("1");
	  $("#ser_anterior").val("");
	  $("#ser_consecuente").val("");
	};
	
	return{
		cssVistaCaptura:	cssVistaCaptura,
		cargaCatalogos:	cargaCatalogos,
		agregarRelacionLicAsig: agregarRelacionLicAsig
	}
}();