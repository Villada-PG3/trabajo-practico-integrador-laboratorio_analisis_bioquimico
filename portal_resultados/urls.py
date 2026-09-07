from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("historial/", views.historial, name="historial"),
    path("resultados/<int:solicitud_id>/", views.resultados, name="resultados"),
    path("reportes/", views.reportes, name="reportes"),
    path("logout/", views.logout_view, name="logout"),
]