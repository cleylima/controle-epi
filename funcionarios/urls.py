from django.urls import path
from .views import listar_funcionarios, novo_funcionario

urlpatterns = [
    path('', listar_funcionarios, name='listar_funcionarios'),
    path('novo/', novo_funcionario, name='novo_funcionario'),
]