"""
URL configuration for sipefi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from sipefi_apps.principal.controlador import views
from sipefi_apps.principal.controlador.views import LoginSipefi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('SIPEFI/', include('sipefi_apps.tomo_ii.controlador.urls')),
    path("SIPEFI/login/", LoginSipefi.as_view(), name="login"),
    path('SIPEFI/cerrarSesion/', views.cerrarSesionUsuarioSistema, name='logOut'),
]
