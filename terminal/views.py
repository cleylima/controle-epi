from django.shortcuts import render, get_object_or_404
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

            }

        funcionarios[funcionario.id]['entregas'].append(entrega)

    return render(

        request,

        'terminal/painel.html',

        {

            'funcionarios': funcionarios.values()

        }

    )
    
def confirmar_terminal(request, pk):

    entrega = get_object_or_404(
        EntregaEPI,
        pk=pk
    )

    return render(
        request,
        'terminal/confirmar.html',
        {
            'entrega': entrega
        }
    )