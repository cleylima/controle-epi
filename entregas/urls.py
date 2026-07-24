from django.urls import path

from .views import (
    listar_entregas,
    nova_entrega,
    gerar_entrega_pdf,
)

urlpatterns = [

    path(
        '',
        listar_entregas,
        name='listar_entregas'
    ),

    path(
        'nova/',
        nova_entrega,
        name='nova_entrega'
    ),
    
    path(
        'pdf/<int:pk>/',
        gerar_entrega_pdf,
        name='gerar_entrega_pdf'
    ),
]