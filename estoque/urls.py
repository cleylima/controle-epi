from django.urls import path

from .views import (
    listar_epis,
    novo_epi,
    editar_epi,
    excluir_epi,
    controle_estoque
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
]