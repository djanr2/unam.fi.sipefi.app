from django.urls import path

from sipefi_apps.tomo_ii.reporte.views import (
generarPdf
)

urlpatterns = [
    path('generarPdf/<int:perfil>/<int:licenciatura>/<int:asignatura>/', generarPdf, name='generarPdf'),
]