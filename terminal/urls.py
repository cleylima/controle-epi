from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.painel_terminal,
        name='painel_terminal'
    ),

    path(
        'confirmar/<int:pk>/',
        views.confirmar_terminal,
        name='confirmar_terminal'
    ),

]