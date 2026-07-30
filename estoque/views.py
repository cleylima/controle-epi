from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.db import models
from .models import EPI, MovimentoEstoque
from .forms import EPIForm
from .forms_movimento import MovimentoEstoqueForm
from django.contrib.auth.decorators import login_required

from io import BytesIO

from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


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


@login_required
def gerar_pdf_estoque_baixo(request):
    epis = EPI.objects.filter(
        quantidade_estoque__lte=models.F("estoque_minimo")
    ).order_by("nome")

    buffer = BytesIO()

    response = HttpResponse(
        content_type="application/pdf"
    )

    nome_arquivo = timezone.localtime().strftime(
        "estoque_baixo_%Y-%m-%d.pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="{nome_arquivo}"'
    )

    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloPersonalizado",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#102239"),
        spaceAfter=8,
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloPersonalizado",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#667085"),
        spaceAfter=18,
    )

    estilo_celula = ParagraphStyle(
        "CelulaTabela",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#101828"),
        alignment=TA_LEFT,
        wordWrap="CJK",
    )

    estilo_celula_centro = ParagraphStyle(
        "CelulaTabelaCentro",
        parent=estilo_celula,
        alignment=TA_CENTER,
    )

    estilo_cabecalho = ParagraphStyle(
        "CabecalhoTabela",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_LEFT,
    )

    estilo_cabecalho_centro = ParagraphStyle(
        "CabecalhoTabelaCentro",
        parent=estilo_cabecalho,
        alignment=TA_CENTER,
    )

    estilo_rodape = ParagraphStyle(
        "RodapePersonalizado",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor("#667085"),
    )

    elementos = []

    elementos.append(
        Paragraph(
            "Relatório de EPIs com Estoque Baixo",
            estilo_titulo,
        )
    )

    elementos.append(
        Paragraph(
            (
                "Itens com quantidade em estoque menor ou igual "
                "ao estoque mínimo cadastrado."
            ),
            estilo_subtitulo,
        )
    )

    data = [
        [
            Paragraph("EPI", estilo_cabecalho),
            Paragraph("CA", estilo_cabecalho_centro),
            Paragraph("Fabricante", estilo_cabecalho),
            Paragraph("Estoque atual", estilo_cabecalho_centro),
            Paragraph("Estoque mínimo", estilo_cabecalho_centro),
        ]
    ]

    for epi in epis:
        data.append(
            [
                Paragraph(
                    str(epi.nome or "-"),
                    estilo_celula,
                ),
                Paragraph(
                    str(epi.ca or "-"),
                    estilo_celula_centro,
                ),
                Paragraph(
                    str(epi.fabricante or "-"),
                    estilo_celula,
                ),
                Paragraph(
                    str(epi.quantidade_estoque),
                    estilo_celula_centro,
                ),
                Paragraph(
                    str(epi.estoque_minimo),
                    estilo_celula_centro,
                ),
            ]
        )

    if len(data) == 1:
        elementos.append(
            Paragraph(
                "Nenhum EPI com estoque baixo foi encontrado.",
                estilos["Normal"],
            )
        )
    else:
        tabela = Table(
            data,
            colWidths=[
                7.0 * cm,
                2.3 * cm,
                7.0 * cm,
                3.0 * cm,
                3.2 * cm,
            ],
            repeatRows=1,
            hAlign="CENTER",
        )

        tabela.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#007D53"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#D0D5DD"),
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#F8FAFC"),
                        ],
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        elementos.append(tabela)

    elementos.append(Spacer(1, 14))

    elementos.append(
        Paragraph(
            (
                "Relatório gerado em "
                f"{timezone.localtime().strftime('%d/%m/%Y às %H:%M')}."
            ),
            estilo_rodape,
        )
    )

    documento.build(elementos)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)

    return response