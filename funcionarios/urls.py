from django.urls import path

from .views import (
    listar_funcionarios,
    novo_funcionario,
    editar_funcionario,
    excluir_funcionario
)

urlpatterns = [

    path(
        '',
        listar_funcionarios,
        name='listar_funcionarios'
    ),

    path(
        'novo/',
        novo_funcionario,
        name='novo_funcionario'
    ),

    path(
        'editar/<int:pk>/',
        editar_funcionario,
        name='editar_funcionario'
    ),

    path(
        'excluir/<int:pk>/',
        excluir_funcionario,
        name='excluir_funcionario'
    ),
]