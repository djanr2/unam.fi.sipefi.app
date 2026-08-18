from django.http import HttpRequest, HttpResponse

from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as conBD


class MiddlewareHttpReqResp:
    
    """
        Clase que apoya a realizar alguna accion antes o despues de cada peticion al servidor.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resp = ""
        if not self.es_url_excluida(request.path):
            resp = self.ejecutar_antes_peticion(request)

        if resp == "NOK":
            response = HttpResponse()
            response["AccesoSistema"] = "NOK"
            return response
        else:
            response = self.get_response(request)
            response["AccesoSistema"] = "OK"
            return response

    def ejecutar_antes_peticion(self, request: HttpRequest):
        # La sesion del servidor es la fuente de verdad. Se conserva el header
        # como respaldo temporal para compatibilidad con llamadas antiguas.
        token = request.session.get("sipefi_token", "")
        if not token:
            token = request.META.get("HTTP_TOKENSISTEMA", "")
        return conBD().validaSesionUsuario(token, 1)
        
    def ejecutar_despues_peticion(self, request: HttpRequest, response: HttpResponse):
        pass
    
    def es_url_excluida(self, url: str) -> bool:
        urls_excluidas = [
            "/SIPEFI/login/",
            "/SIPEFI/Tomo_II",
            "/SIPEFI/cerrarSesion/",
            "/SIPEFI/logout/",
            "/SIPEFI/seleccion-perfil/",
            "/SIPEFI/seleccionarPerfil/",
            "/SIPEFI/recargaPagina/",
            "/SIPEFI/formacion-complementaria/"
        ]
        return url in urls_excluidas