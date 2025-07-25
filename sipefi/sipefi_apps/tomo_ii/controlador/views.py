# -*- coding: utf-8 -*-
"""
    Este archivo funciona para conectar al modelo con el controlador y asi poder dar
    respuesta a la peticion solicitada al servidor desde el cliente.
"""

from django.template.response import TemplateResponse
from django.http.response import HttpResponsePermanentRedirect
from django.http import JsonResponse

from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD

from django.views.generic import (
    TemplateView,
)

class Vista_Principal_TomoII(TemplateView):
    """
        Clase en donde se hace uso de un TemplateView para mapear la url inicial del sistema.
        
        :param TemplateView: Objeto de la clase TemplateView que es usada para presentar la vista principal del sistema.
    """
    def __init__(self):
        self.template_name = "tomo_ii/indexTomoII.html"  #nombre del archivo html que se desea mostrar inicialmente
        self.usuario = ""
        self.rol = ""
        self.urlSIPEFI = ""
        self.token = ""
    
    def get_context_data(self, **kwargs):
        """
            Funcion que genera informacion util como argumentos para ser transferidos a la vista
            del template usado, definido en variable **template_name**.
            
            :return: Regresa como contexto de la peticion la informacion que se genero como argumentos del contexto. 
        """
        context = super().get_context_data(**kwargs)
        context['idsValidador'] = CBD().buscaRolXNombre("Validador")
        context['usuario'] = self.usuario
        context['rol'] = self.rol
        context['sipefi_login'] = self.urlSIPEFI
        context['token'] = self.token
        context['universo'] = 1 # id_universo = 1 = TOMO II
        return context
    
    
    def get(self, request):
        """
            Funcion que nos ayuda a validar la peticion de acceso al sistema.
            
            :return: Regresa la pagina principal del sistema o impide el acceso a la aplicacion.
        """
        self.token = request.GET.get("t",'')
        resp = CBD().validaTokenAcceso(self.token)
        id_usuario = ""
        if resp['estatus'] == 200: #Token correcto
            self.usuario = resp['acceso'][0][1]
            id_usuario = resp['acceso'][0][3]
            respMap = CBD().mapeoRolUsuario(resp['acceso'][0][2])
            if respMap['estatus'] == 200: #Rol correcto y habilitado
                self.rol = respMap
                self.urlSIPEFI = resp['badAccess']
                response = TemplateResponse(request, self.template_name, self.get_context_data())
                CBD().quemaTokenAcceso(self.token)
                CBD().cierraSesionUsuario(self.token, id_usuario, 2)
            else:
                response = HttpResponsePermanentRedirect(resp['badAccess'])
                CBD().cierraSesionUsuario(self.token, id_usuario, 1)
        else:
            response = HttpResponsePermanentRedirect(resp['badAccess'])
            CBD().cierraSesionUsuario(self.token, id_usuario, 1)
        return response
 
def requestTablasSoli(request):
    """
        La funcion sirve para conectar la peticion cliente - servidor, 
        en este caso consulta informacion de las solicitudes en las que ha participado
        el usuario logueado.
        
        :return: Nos da como respuesta una estructura JSON con la informacion solicitada en la peticion.
    """
    usuario = request.POST.get('user','')
    rol = request.POST.get('rol','')
    return JsonResponse(CBD().buscaSolicitudesUsuario(usuario,rol))

def requestRecargaPagina(request):
    """
        La funcion sirve para conectar la peticion cliente - servidor, 
        en este caso se desea actualizar la pagina, por lo cual se reinicia token de acceso.
        
        :return: Nos da como respuesta una estructura JSON con la informacion solicitada en la peticion.
    """
    token = request.POST.get('token', '')
    CBD().actualizaEstatusToken(token)
    return JsonResponse({"resp": "OK" }) 