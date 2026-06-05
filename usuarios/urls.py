from django.urls import path

from .views import (
    MeuLoginView,
    MeuLogoutView,
    listar_usuarios,
    novo_usuario,
)

urlpatterns = [

    path(
        'login/',
        MeuLoginView.as_view(),
        name='login'
    ),

    path(
        'logout/',
        MeuLogoutView.as_view(),
        name='logout'
    ),
    
    path(
    '',
    listar_usuarios,
    name='listar_usuarios'
    ),

    path(
        'novo/',
        novo_usuario,
        name='novo_usuario'
    ),

]