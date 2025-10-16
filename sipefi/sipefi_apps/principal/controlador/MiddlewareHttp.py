from django.http import HttpRequest, HttpResponse

from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as conBD

class MiddlewareHttpReqResp:
    
    """
        Clase que apoya a realizar alguna accion antes o despues de cada peticion al servidor.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.token = ""

    def __call__(self, request):
        # Ejecutar la funcion antes de procesar la solicitud
        resp = ""
        # LEONIXGU
        if self.bypass_url_incluida(request.path):
            response = self.get_response(request)
            self.token = request.META.get('HTTP_TOKENSISTEMA', '')
            #LEONIXGU
            print('token')
            print(self.token)
            response["AccesoSistema"] = "OK"
            return response
        if not self.es_url_excluida(request.path):
            resp = self.ejecutar_antes_peticion(request)
        if resp == "NOK":
            response = HttpResponse()
            response["AccesoSistema"] = "NOK"
            return response
        else:
            # Procesar la solicitud
            response = self.get_response(request)
            response["AccesoSistema"] = "OK"
            return response
        # Ejecutar la funcion despues de procesar la solicitud
        #self.ejecutar_despues_peticion(request, response)

    def ejecutar_antes_peticion(self, request: HttpRequest):
        self.token = request.META.get('HTTP_TOKENSISTEMA', '')
        resp = conBD().validaSesionUsuario(self.token, 1)
        return resp
        
    def ejecutar_despues_peticion(self, request: HttpRequest, response: HttpResponse):
        pass
    
    def es_url_excluida(self, url: str) -> bool:
        # URLs que se desean excluir
        urls_excluidas = [
            "/SIPEFI/login/",
            "/SIPEFI/Tomo_II",
            "/SIPEFI/cerrarSesion/",
            "/SIPEFI/recargaPagina/"
        ]
        return url in urls_excluidas
    #LEONIXGU
    def bypass_url_incluida(self, url: str)-> bool:
        var_inclu = [
            #/SIPEFI/reporte/generarPdf/<perfil>/<id_licenciatura>/<id_solicitud>/
            "/SIPEFI/reporte/generarPdf/2/1/4/",
            "/SIPEFI/reporte/generarPdf/3/1/4/"
        ]
        return url in var_inclu