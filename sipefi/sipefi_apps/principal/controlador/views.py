# -*- coding: utf-8 -*-
'''
    Este archivo funciona para conectar al modelo con el controlador y asi poder dar 
    respuesta a la peticion solicitada al servidor desde el cliente.
''' 
from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD

from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

class LoginSipefi(View):
    
    def get(self, request):
        return render(request, 'principal/login.html')

    def post(self, request):
        usuario = request.POST.get('usuario')
        clave = request.POST.get('clave')
        resultado = CBD().validar_credenciales(usuario, clave)

        if resultado:
            token = resultado['token']
            return redirect(f'/SIPEFI/Tomo_II?t={token}')
        else:
            messages.error(request, 'Usuario o contraseña inválidos.')
            return render(request, 'principal/login.html')
        
@never_cache
def cerrarSesionUsuarioSistema(request):
    """
        La funcion sirve para conectar la peticion cliente - servidor, 
        en este caso sirve para procesar el cerrado de la sesion del usuario logueado
    """
    token = request.POST.get('token','')
    resp = CBD().validaSesionUsuario(token, 2)
    if resp != "E":
        CBD().cierraSesionUsuario(token, "", 1)
    return JsonResponse({"resp": "OK" }) 