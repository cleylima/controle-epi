from django.shortcuts import render, redirect
from .models import Funcionario
from .forms import FuncionarioForm
from django.shortcuts import render, redirect, get_object_or_404
from entregas.models import EntregaEPI
from django.contrib.auth.decorators import login_required

@login_required
def listar_funcionarios(request):

    funcionarios = Funcionario.objects.all()

    return render(
        request,
        'funcionarios/listar.html',
        {
            'funcionarios': funcionarios
        }
    )

@login_required
def novo_funcionario(request):

    if request.method == 'POST':

        form = FuncionarioForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')

    else:
        form = FuncionarioForm()

    return render(
        request,
        'funcionarios/form.html',
        {
            'form': form
        }
    )

@login_required
def editar_funcionario(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    if request.method == 'POST':

        form = FuncionarioForm(
            request.POST,
            instance=funcionario
        )

        if form.is_valid():
            form.save()
            return redirect('listar_funcionarios')

    else:

        form = FuncionarioForm(
            instance=funcionario
        )

    return render(
        request,
        'funcionarios/form.html',
        {
            'form': form
        }
    )


@login_required
def excluir_funcionario(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    funcionario.delete()

    return redirect(
        'listar_funcionarios'
    )
    

@login_required
def historico_funcionario(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    entregas = EntregaEPI.objects.filter(
        funcionario=funcionario
    ).order_by('-data_entrega')

    return render(
        request,
        'funcionarios/historico.html',
        {
            'funcionario': funcionario,
            'entregas': entregas
        }
    )