from django.shortcuts import (
    render,
    redirect
)

from .forms import EntregaForm
from .models import EntregaEPI
from datetime import timedelta


def listar_entregas(request):

    entregas = EntregaEPI.objects.all()

    return render(
        request,
        'entregas/listar.html',
        {
            'entregas': entregas
        }
    )


def nova_entrega(request):

    if request.method == 'POST':

        form = EntregaForm(request.POST)

        if form.is_valid():

            print("FORMULÁRIO VÁLIDO")

            entrega = form.save(commit=False)

            epi = entrega.epi

            if epi.quantidade_estoque <= 0:

                form.add_error(
                    'epi',
                    'Este EPI está sem estoque.'
                )

            elif entrega.quantidade > epi.quantidade_estoque:

                form.add_error(
                    'quantidade',
                    f'Estoque insuficiente. Disponível: {epi.quantidade_estoque}'
                )

            else:

                epi.quantidade_estoque -= entrega.quantidade
                epi.save()

                entrega.data_proxima_troca = (
                    entrega.data_entrega +
                    timedelta(days=epi.vida_util_dias)
                )

                entrega.save()

                print("ENTREGA SALVA")

                return redirect('listar_entregas')

        else:

            print("ERROS DO FORMULÁRIO:")
            print(form.errors)

    else:

        form = EntregaForm()

    return render(
        request,
        'entregas/form.html',
        {
            'form': form
        }
    )