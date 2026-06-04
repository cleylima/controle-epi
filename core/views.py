from django.shortcuts import render

from funcionarios.models import Funcionario
from estoque.models import EPI


def dashboard(request):

    total_funcionarios = Funcionario.objects.count()

    total_epis = EPI.objects.count()

    estoque_baixo = EPI.objects.filter(
        quantidade_estoque__lte=0
    ).count()

    context = {
        'total_funcionarios': total_funcionarios,
        'total_epis': total_epis,
        'estoque_baixo': estoque_baixo,
    }

    return render(
        request,
        'dashboard.html',
        context
    )