from django.shortcuts import render, redirect
from .models import Funcionario
from .forms import FuncionarioForm
from django.shortcuts import render, redirect, get_object_or_404
from entregas.models import EntregaEPI
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from entregas.models import EntregaEPI

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

@login_required
def gerar_ficha_epi_pdf(request, pk):

    funcionario = get_object_or_404(
        Funcionario,
        pk=pk
    )

    entregas = (
        EntregaEPI.objects
        .filter(funcionario=funcionario)
        .order_by('-data_entrega')
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; '
        f'filename=ficha_epi_{funcionario.id}.pdf'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(
            'FICHA DE ENTREGA DE EPI',
            styles['Title']
        )
    )

    elementos.append(Spacer(1, 20))

    elementos.append(
        Paragraph(
            f'<b>Funcionário:</b> {funcionario.nome}',
            styles['Normal']
        )
    )

    elementos.append(
        Paragraph(
            f'<b>Setor:</b> {funcionario.setor}',
            styles['Normal']
        )
    )

    elementos.append(
        Paragraph(
            f'<b>Função:</b> {funcionario.funcao}',
            styles['Normal']
        )
    )

    elementos.append(Spacer(1, 20))

    for entrega in entregas:

        elementos.append(
            Paragraph(
                f'''
                {entrega.epi.nome}
                - Qtd: {entrega.quantidade}
                - Data: {entrega.data_entrega.strftime("%d/%m/%Y")}
                ''',
                styles['Normal']
            )
        )

    elementos.append(Spacer(1, 40))

    elementos.append(
        Paragraph(
            '''
            Declaro ter recebido os EPIs acima
            e estar ciente da obrigatoriedade
            de sua utilização.
            ''',
            styles['Normal']
        )
    )

    elementos.append(Spacer(1, 50))

    elementos.append(
        Paragraph(
            '__________________________________',
            styles['Normal']
        )
    )

    elementos.append(
        Paragraph(
            'Assinatura do Colaborador',
            styles['Normal']
        )
    )

    doc.build(elementos)

    return response