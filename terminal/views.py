from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from entregas.models import EntregaEPI


def painel_terminal(request):

    entregas = (
        EntregaEPI.objects
        .filter(confirmado=False)
        .select_related(
            'funcionario',
            'epi'
        )
        .order_by(
            'funcionario__nome'
        )
    )

    funcionarios = {}

    for entrega in entregas:

        funcionario = entrega.funcionario

        if funcionario.id not in funcionarios:
            funcionarios[funcionario.id] = {
                'funcionario': funcionario,
                'entregas': [],
                'primeira_entrega': entrega,
                'id_entrega': entrega.id,
            }

        funcionarios[funcionario.id]['entregas'].append(entrega)

    return render(
        request,
        'terminal/painel.html',
        {
            'funcionarios': funcionarios.values()
        }
    )
    
@require_POST
def confirmar_ajax(request):

    entrega = EntregaEPI.objects.get(
        pk=request.POST.get("entrega")
    )

    entrega.confirmado = True
    entrega.save()

    return JsonResponse({
        "sucesso": True
    })