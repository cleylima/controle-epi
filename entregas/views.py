from django.shortcuts import (
    render,
    redirect
)


from .forms import EntregaForm
from .models import EntregaEPI
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import base64
from django.core.files.base import ContentFile

@login_required
def listar_entregas(request):

    entregas = EntregaEPI.objects.all()

    return render(
        request,
        'entregas/listar.html',
        {
            'entregas': entregas
        }
    )

@login_required
def nova_entrega(request):

    if request.method == 'POST':

        form = EntregaForm(request.POST)

        if form.is_valid():

            print("FORMULÁRIO VÁLIDO")

            entrega = form.save(commit=False)
            
            print(request.POST.keys())
            print(
                "ASSINATURA POST:",
                request.POST.get('assinatura_base64')
            )
            
            assinatura_base64 = request.POST.get(
                'assinatura_base64'
            )
            print("ASSINATURA RECEBIDA:",
                bool(assinatura_base64))

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
                
                if assinatura_base64:

                    formato, imgstr = assinatura_base64.split(';base64,')

                    extensao = formato.split('/')[-1]

                    entrega.assinatura.save(
                        f'assinatura_{entrega.funcionario.id}.{extensao}',
                        ContentFile(
                            base64.b64decode(imgstr)
                        ),
                        save=False
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