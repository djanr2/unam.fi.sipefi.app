from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD

class Solicitud(object):
        """
            Clase que ayuda a procesar todo lo necesario para una solicitud de SIPEFI-TOMO II.
            
            - Procesamiento de estatus (guardado y actualizacion)
            
            - Rechazo de estatus
        """
    
        def __init__(self):
            """
                Funcion que ayuda a inicializar parametros y valores necesarios
                para procesar correctamente las solicitudes
            """
            self.idSoli = ""
            self.nomEstatusSol = ""
            self.idEstatusSol = ""
            self.token = ""
            self.rol = ""
            self.infoAdi = {}
            self.resp = {'respuesta': "",
                        'estatus': "" 
                    }
        
        def accionSolicitud(self, obj):
            """
                Funcion inicial que realiza la accion solicitada por el usuario:
                
                accion == 1 ==> Guarda o actualiza solicitud
                
                accion == 2 ==> Procesa solicitud al sig estatus
                
                accion == 3 ==> Rechaza solicitud
                
                :param obj: Objeto que contiene la informacion de la solicitud a procesar
                
                :return: Regresa un Objeto con la respuesta de la solicitud procesada. 
            """
            try:
                accion = int(obj['accionSoli'])
                if accion == 1: #  Crea o actualiza Solicitud 
                    accionGA = int(obj['accionGA'])
                    self.creaSolicitud(obj, accionGA)
                    self.resp['respuesta'] = {'idS': self.idSoli, 'nomES': self.nomEstatusSol, 'idES': self.idEstatusSol, 'infoAdi': self.infoAdi}
                    self.resp['estatus'] = 200
                elif accion == 2: # Procesa solicitud al sig estatus
                    self.guardaSolicitudEstatus(obj)
                    self.resp['estatus'] = 200
                elif accion == 3: #Rechaza solicitud
                    self.rechazaSolicitud(obj)
                    self.resp['estatus'] = 200
            except NameError:
                self.resp['estatus'] = 204
                
            return self.resp
        
        def creaSolicitud(self, obj, accion):
            """
                Funcion que se encarga de preparar la solicitud para poder realizar la creacion
                o actualizacion de esta.
                
                :param obj: Objeto que contiene la informacion de la solicitud a procesar
                :param accion: Define la accion a realizar a la solicitud.
                
                1 - Crea nueva solicitud
                
                2 - Actualiza solicitud
            """
            self.idSoli = obj["numSolicitud"] if str(obj["numSolicitud"]).isnumeric() else 0
            self.idEstatusSol = int(obj["idEstSoli"]) if str(obj["idEstSoli"]).isnumeric() else 1 
            self.nomEstatusSol = self.validaEstatus(self.idEstatusSol)
            self.limpiaSolicitud(self.idSoli,self.idEstatusSol)
            self.generaInsertSolicitud(obj,accion)

        def generaInsertSolicitud(self, obj, accion):
            print("")
        
        def validaEstatus(self, idEstatus):
            """
                Funcion que obtiene el nombre del estatus de la solicitud de acuerdo a su identificador.
                
                :param idEstatus: Identificador del estatus de la solicitud.
                
                :return: Regresa nombre del estatus de la solicitud.
            """
            nomEstatus={
                1:'Elaboraci&oacute;n',
                2:'Revisi&oacute;n',
                3:'Concluida',
                0:'Cancelada'
            }
            return nomEstatus.get(idEstatus,"Elaboraci&oacute;n")
                
        def limpiaSolicitud(self, id_solicitud, estatus_soliciud):
            """
                Funcion que ayuda a limpiar la informacion de la solicitud procesada antes de realizar alguna actualizacion o guardado.
                
                :param id_solicitud: Identificador de la solicitud.
                :param estatus_soliciud: Identificador del estatus de la solicitud. 
            """
            print("")
            
        def guardaSolicitudEstatus(self, obj):
            """
                Funcion que apoya con la gestion para guardar la solicitud y asignarle el estatus correspondiente.
                
                :param obj: Objeto que contiene toda la informacion de la solicitud procesada.
            """
            self.token = obj['token']
            self.rol = obj['rol']
            solicitud = obj["numSolicitud"]
            estatusSoli = obj["idEstSoli"]
            usuario = obj['usuario']
            comentario = obj["comentarios"]
            #se guarda primero solicitud
            self.creaSolicitud(obj,2)
            self.actualizaUsuarioSolicitud(solicitud, estatusSoli, usuario);
            self.actualizaEstatusSoli(solicitud, estatusSoli, usuario, comentario, obj)
        
        def actualizaUsuarioSolicitud(self, solicitud, estatus, usuario):
            """
                Funcion que actualiza en base de datos el usuario que modifico la solicitud procesada.
                
                :param usuario: Usuario que proceso la solicitud.
                :param solicitud: Identificador de la solicitud.
                :param estatus: Identificador del estatus de la solicitud. 
            """
            print("")
        
        def procesaCopiaTabla(self, sql, tabla, solicitud, estatus, newStatus, busuario, insertar):
            """
                Funcion que procesa la copia de informacion de la solicitud para poder gestionar una solicitud con varios estatus.
                
                :param sql: Parametro que contiene una cadena de texto con una sql necesaria para obtener los nombres de columnas de una tabla.
                :param tabla: Nombre de la tabla a la que se desea realizar la copia de informacion.
                :param solicitud: Identificador de solicitud.
                :param estatus: Identificador de la estatus.
                :param newStatus: Identificador del nuevo estatus.
                :param busuario: Usuario que esta procesando la solicitud.
                :param insertar: Boolean que indica si se debe insertar la copia de informacion o solo guardar la consultar sql creada en una variable.
                
                :return: Regresa un arreglo con las consultas sql a ser ejecutadas posteriormente.
            """
            print("")
            
        def actualizaEstatusSoli(self, solicitud, estatus, usuario, comentario, objSol):
            """
                Funcion que realiza la actualizacion o guardado de la solicitud procesada.
                
                :param solicitud: Identificador de la solicitud.
                :param estatus: Identificador del estatus.
                :param usuario: Usuario que esta procesando la solicitud.
                :param comentario: Objeto que contiene los comentarios de la solicitud procesada.
                :param hasRisk: Parametro que indica si la solicitud tiene riesgo y debe ser procesada para la validacion de un validador de riesgos.
                :param objSol: Parametro que contiene la informacion de la solicitud.
            """
            print("")
        
        def actualizaEstatusToken(self, token):
            """
                Funcion que actualiza el estatus del token que se esta usando para la sesion del usuario y asi pueda continuar trabajando.
                
                :param token: Numero de token necesario para ingresar a la sesion de la aplicacion.
            """
            print("")
            
        def rechazaSolicitud(self, obj):
            """
                Funcion que realiza el rechazo a la solicitud procesada.
                
                :param obj: Objeto que contiene la informacion de la solicitud que se desea rechazar.
            """
            print("")
            
        def insertaHistoricoSolicitud(self, solicitud, estatusO, estatusD, comentario, perfil, usuario): 
            """
                Funcion que guarda los comentarios y el flujo de la solicitud entre estatus.
                
                :param solicitud: Identificador de la solicitud.
                :param estatusO: Estatus actual de la solicitud procesada.
                :param estatusD: Estatus al que pasara la solicitud tras procesarla.
                :param comentario: Comentarios de la solicitud.
                :param perfil: Identificador del perfil que tiene el usuario logueado.
                :param usuario: Usuario logueado.
            """
            print("")
            
        def dameDatosSolicitud(self, accion, infoUtil):
            print("")
        
        def cancelaSolicitud(self, idSol, idEst, token, rol, usuario, comentario):
            print("")