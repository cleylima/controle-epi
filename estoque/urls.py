from django.urls import path

from .views import (
    listar_epis,
    novo_epi,
    editar_epi,
    excluir_epi,
    controle_estoque,
    nova_movimentacao,
    historico_movimentacoes,
)

urlpatterns = [

    path(
        '',
        listar_epis,
        name='listar_epis'
    ),

    path(
        'novo/',
        novo_epi,
        name='novo_epi'
    ),

    path(
        'editar/<int:pk>/',
        editar_epi,
        name='editar_epi'
    ),

    path(
        'excluir/<int:pk>/',
        excluir_epi,
        name='excluir_epi'
    ),
    
    path(
        'controle/',
        controle_estoque,
        name='controle_estoque'
    ),
    
    path(
        'movimentacao/nova/',
        nova_movimentacao,
        name='nova_movimentacao'
    ),
    
    path(
        'historico/',
        historico_movimentacoes,
        name='historico_movimentacoes'
    ),
]