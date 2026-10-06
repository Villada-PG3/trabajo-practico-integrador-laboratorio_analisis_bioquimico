from django.urls import path
from . import views

app_name= "analisis_bioquimico"
urlpatterns = [
    path("",views.home,name="home"),
    # Rutas del Integrante 3 (Portal del Paciente)
    path('portal/login/', views.login_paciente, name='login_paciente'),
    path('portal/logout/', views.logout_paciente, name='logout_paciente'),
    path('portal/historial/', views.historial_solicitudes, name='portal_historial'),
    path('recepcion/pacientes/', views.login_paciente, name='login'),
]