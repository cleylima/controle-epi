from django.shortcuts import render, redirect
from .models import Funcionario
from .forms import FuncionarioForm


def listar_funcionarios(request):

    funcionarios = Funcionario.objects.all()

    return render(
        request,
        'funcionarios/listar.html',
        {
            'funcionarios': funcionarios
        }
    )


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