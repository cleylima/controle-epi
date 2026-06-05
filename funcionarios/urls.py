from django.urls import path


from .views import (
    listar_funcionarios,
    novo_funcionario,
    editar_funcionario,
    excluir_funcionario,
    historico_funcionario,
    gerar_ficha_epi_pdf,
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
    path(
        'historico/<int:pk>/',
        historico_funcionario,
        name='historico_funcionario'
    ),
    
    path(
        'ficha-pdf/<int:pk>/',
        gerar_ficha_epi_pdf,
        name='gerar_ficha_epi_pdf'
    ),
]