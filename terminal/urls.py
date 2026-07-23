from django.urls import path

from . import views


app_name = 'terminal'


urlpatterns = [
    path(
        '',
        views.painel_terminal,
        name='painel'
    ),

    path(
        'validar-biometria/',
        views.validar_biometria_ajax,
        name='validar_biometria'
    ),
]