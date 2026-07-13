from django.urls import path
from . import views
from .views import painel_terminal, confirmar_ajax

urlpatterns = [

    path(
        '',
        views.painel_terminal,
        name='painel_terminal'
    ),

    path(
        "confirmar/",
        confirmar_ajax,
        name="confirmar_ajax"
    ),


]