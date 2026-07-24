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
        'biometria/iniciar/',
        views.iniciar_validacao_biometrica,
        name='iniciar_biometria'
    ),

    path(
        'biometria/<uuid:sessao_id>/dados/',
        views.dados_validacao_biometrica,
        name='dados_biometria'
    ),

    path(
        'biometria/<uuid:sessao_id>/concluir/',
        views.concluir_validacao_biometrica,
        name='concluir_biometria'
    ),

    path(
        'biometria/<uuid:sessao_id>/status/',
        views.status_validacao_biometrica,
        name='status_biometria'
    ),
    
    path(
        'biometria/<uuid:sessao_id>/dados/',
        views.dados_validacao_biometrica,
        name='dados_validacao_biometrica'
    ),

    path(
        'biometria/<uuid:sessao_id>/concluir/',
        views.concluir_validacao_biometrica,
        name='concluir_validacao_biometrica'
    ),
]