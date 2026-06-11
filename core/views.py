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

    epis_vencidos = EntregaEPI.objects.filter(
        ativo=True,
        data_proxima_troca__lt=hoje
    ).count()
    
    epis_vencendo_lista = EntregaEPI.objects.filter(
        ativo=True,
        data_proxima_troca__gte=hoje,
        data_proxima_troca__lte=data_limite
    )

    for item in epis_vencendo_lista:

        item.dias_restantes = (
            item.data_proxima_troca - hoje
        ).days

    epis_vencendo = epis_vencendo_lista.count()

    ca_vencidos = EPI.objects.filter(
        validade_ca__lt=hoje
    ).count()

    ca_vencendo = EPI.objects.filter(
        validade_ca__gte=hoje,
        validade_ca__lte=data_limite
    ).count()
    
    entregas_pendentes = (
        EntregaEPI.objects
        .filter(confirmado=False)
        .count()
    )
    
    pendencias = (
        EntregaEPI.objects
        .filter(confirmado=False)
        .order_by('-data_entrega')[:10]
    )

    context = {
        'total_funcionarios': total_funcionarios,
        'total_epis': total_epis,
        'total_entregas': total_entregas,
        'estoque_baixo': estoque_baixo,

        'epis_vencidos': epis_vencidos,
        'epis_vencendo': epis_vencendo,

        'ca_vencidos': ca_vencidos,
        'ca_vencendo': ca_vencendo,
        'epis_vencendo_lista': epis_vencendo_lista,
        
        'entregas_pendentes': entregas_pendentes,
        'pendencias': pendencias,
    }

    return render(
        request,
        'core/dashboard.html',
        context
    )