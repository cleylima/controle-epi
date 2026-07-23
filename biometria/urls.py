from django.urls import path

from .views import (
    excluir_biometria,
    registrar_biometria,
    salvar_biometria,
)

urlpatterns = [
    path(
        'registrar/<int:funcionario_id>/',
        registrar_biometria,
        name='registrar_biometria'
    ),

    path(
        'salvar/<int:funcionario_id>/',
        salvar_biometria,
        name='salvar_biometria'
    ),

    path(
        'excluir/<int:funcionario_id>/',
        excluir_biometria,
        name='excluir_biometria'
    ),
]