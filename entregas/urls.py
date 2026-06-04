from django.urls import path

from .views import (
    listar_entregas,
    nova_entrega
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

]