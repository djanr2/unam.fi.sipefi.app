from django.urls import include, path

from sipefi_apps.formacion_complementaria.controlador import views

urlpatterns = [
    path("reporte/", include("sipefi_apps.formacion_complementaria.reporte.urls")),
    path("", views.VistaFormacionComplementaria.as_view(), name="formacion_complementaria"),
    path("datos-iniciales/", views.datos_iniciales, name="fc_datos_iniciales"),
    path("listar/", views.listar, name="fc_listar"),
    path("asignaturas/", views.asignaturas_disponibles, name="fc_asignaturas"),
    path("bibliografias/", views.bibliografias_apoyo, name="fc_bibliografias"),
    path("detalle/", views.detalle, name="fc_detalle"),
    path("guardar/", views.guardar, name="fc_guardar"),
    path("completar/", views.completar, name="fc_completar"),
]
