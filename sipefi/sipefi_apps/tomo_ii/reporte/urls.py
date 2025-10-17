from django.urls import path

from sipefi_apps.tomo_ii.reporte.views import (
generarPdf
)

urlpatterns = [
    path('generarPdf/', generarPdf, name='generarPdf'),
]