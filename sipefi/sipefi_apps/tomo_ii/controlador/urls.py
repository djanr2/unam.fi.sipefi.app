"""
    Este archivo funciona para mapear las peticiones Cliente - Servidor
    para el sistema que contiene todos los procesos que han sido automatizados, ya sea a traves de consultas por Ajax o 
    directamente por url en el navegador.   
    
    **url** ([nombre contenido en url o peticion Ajax], [vista que dara respuesta a la peticion], [nombre corto de peticion o url])
    
    **path** : en la seccion de path se debe de poner el nombre de la url del sistema inicial.
"""
from django.urls import path
from sipefi_apps.tomo_ii.controlador.views import (
    Vista_Principal_TomoII,
    requestTablasSoli,
    requestRecargaPagina,
    requestAccionSolicitud,
    requestCargaSolicitud
)

urlpatterns = [
    path("Tomo_II", Vista_Principal_TomoII.as_view(), name="indexTomoII"),
    path("llenaTablasSoli", requestTablasSoli, name='tablasSoli'),
    path("recargaPagina/", requestRecargaPagina, name='recargaIdx'),
    path('accionSolicitud/', requestAccionSolicitud, name='accionSoli'),
    path('cargaSolicitud/', requestCargaSolicitud, name='cargaSoli'),
]