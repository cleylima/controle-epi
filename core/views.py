from django.shortcuts import render
from datetime import date, timedelta
from funcionarios.models import Funcionario
from estoque.models import EPI
from entregas.models import EntregaEPI
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):

    total_funcionarios = Funcionario.objects.count()

    total_epis = EPI.objects.count()

    total_entregas = EntregaEPI.objects.count()

    estoque_baixo = EPI.objects.filter(
        quantidade_estoque__lte=5
    ).count()
    
    hoje = date.today()

    data_limite = hoje + timedelta(days=30)

    epis_vencendo = EntregaEPI.objects.filter(
        data_proxima_troca__gte=hoje,
        data_proxima_troca__lte=data_limite
    ).order_by('data_proxima_troca')

    context = {
        'total_funcionarios': total_funcionarios,
        'total_epis': total_epis,
        'total_entregas': total_entregas,
        'estoque_baixo': estoque_baixo,
        'epis_vencendo': epis_vencendo,
    }

    return render(
        request,
        'core/dashboard.html',
        context
    )