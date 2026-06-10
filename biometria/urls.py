from django.urls import path

from . import views


urlpatterns = [

    path(
        'registrar/<int:funcionario_id>/',
        views.registrar_biometria,
        name='registrar_biometria'
    ),

    path(
        'autenticar/<int:entrega_id>/',
        views.autenticar_biometria,
        name='autenticar_biometria'
    ),
    path(
        'opcoes/<int:funcionario_id>/',
        views.opcoes_registro,
        name='opcoes_registro'
    ),
    path(
        'salvar/',
        views.salvar_biometria,
        name='salvar_biometria'
    ),
]