from django.urls import path

from sipefi_apps.formacion_complementaria.reporte.views import generar_pdf

urlpatterns = [
    path("generarPdf/", generar_pdf, name="fc_generar_pdf"),
]
