from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import EPI
from .forms import EPIForm


def listar_epis(request):

    epis = EPI.objects.all()

    return render(
        request,
        'estoque/listar.html',
        {
            'epis': epis
        }
    )


def novo_epi(request):

    if request.method == 'POST':

        form = EPIForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('listar_epis')

    else:

        form = EPIForm()

    return render(
        request,
        'estoque/form.html',
        {
            'form': form
        }
    )


def editar_epi(request, pk):

    epi = get_object_or_404(
        EPI,
        pk=pk
    )

    if request.method == 'POST':

        form = EPIForm(
            request.POST,
            instance=epi
        )

        if form.is_valid():
            form.save()
            return redirect('listar_epis')

    else:

        form = EPIForm(
            instance=epi
        )

    return render(
        request,
        'estoque/form.html',
        {
            'form': form
        }
    )


def excluir_epi(request, pk):

    epi = get_object_or_404(
        EPI,
        pk=pk
    )

    epi.delete()

    return redirect(
        'listar_epis'
    )