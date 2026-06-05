from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from .models import EPI, MovimentoEstoque
from .forms import EPIForm
from .forms_movimento import MovimentoEstoqueForm
from django.contrib.auth.decorators import login_required


@login_required
def listar_epis(request):

    epis = EPI.objects.all()

    return render(
        request,
        'estoque/listar.html',
        {
            'epis': epis
        }
    )

@login_required
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

@login_required
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


@login_required
def excluir_epi(request, pk):

    epi = get_object_or_404(
        EPI,
        pk=pk
    )

    epi.delete()

    return redirect(
        'listar_epis'
    )
    
@login_required
def controle_estoque(request):

    epis = EPI.objects.all()

    return render(
        request,
        'estoque/controle_estoque.html',
        {
            'epis': epis
        }
    )
    
@login_required
def nova_movimentacao(request):

    if request.method == 'POST':

        form = MovimentoEstoqueForm(request.POST)

        if form.is_valid():

            movimento = form.save(commit=False)

            movimento.usuario = request.user

            epi = movimento.epi

            if movimento.tipo == 'entrada':

                epi.quantidade_estoque += movimento.quantidade

            elif movimento.tipo == 'saida':

                if movimento.quantidade > epi.quantidade_estoque:

                    form.add_error(
                        'quantidade',
                        'Quantidade maior que o estoque disponível.'
                    )

                    return render(
                        request,
                        'estoque/movimentacao_form.html',
                        {'form': form}
                    )

                epi.quantidade_estoque -= movimento.quantidade

            elif movimento.tipo == 'ajuste':

                epi.quantidade_estoque = movimento.quantidade

            epi.save()

            movimento.save()

            return redirect('controle_estoque')

    else:

        form = MovimentoEstoqueForm()

    return render(
        request,
        'estoque/movimentacao_form.html',
        {
            'form': form
        }
    )
    
@login_required
def historico_movimentacoes(request):

    movimentacoes = (
        MovimentoEstoque.objects
        .select_related('epi', 'usuario')
        .order_by('-data_movimento')
    )

    epi_id = request.GET.get('epi')

    tipo = request.GET.get('tipo')

    if epi_id:
        movimentacoes = movimentacoes.filter(
            epi_id=epi_id
        )

    if tipo:
        movimentacoes = movimentacoes.filter(
            tipo=tipo
        )

    epis = EPI.objects.all()

    return render(
        request,
        'estoque/historico_movimentacoes.html',
        {
            'movimentacoes': movimentacoes,
            'epis': epis,
        }
    )
    
from django.http import HttpResponse
from openpyxl import Workbook

@login_required
def exportar_movimentacoes_excel(request):

    wb = Workbook()

    ws = wb.active

    ws.title = 'Movimentações'

    ws.append([
        'Data',
        'EPI',
        'Tipo',
        'Quantidade',
        'Usuário',
        'Observação'
    ])

    movimentacoes = (
        MovimentoEstoque.objects
        .select_related('epi', 'usuario')
        .order_by('-data_movimento')
    )

    for mov in movimentacoes:

        ws.append([
            mov.data_movimento.strftime('%d/%m/%Y %H:%M'),
            mov.epi.nome,
            mov.get_tipo_display(),
            mov.quantidade,
            mov.usuario.username if mov.usuario else '',
            mov.observacao or '',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=historico_estoque.xlsx'

    wb.save(response)

    return response