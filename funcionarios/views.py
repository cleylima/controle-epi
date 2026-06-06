from django.shortcuts import render, redirect
from .models import Funcionario
from .forms import FuncionarioForm
from django.shortcuts import render, redirect, get_object_or_404
from entregas.models import EntregaEPI
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import date

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib import colors
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
    from reportlab.platypus import Image
    from django.conf import settings
    import os
    from reportlab.platypus import Image

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
        f'inline; '
        f'filename=ficha_epi_{funcionario.id}.pdf'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elementos = []
    
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'img',
        'logoecocristal.png'
    )

    if os.path.exists(logo_path):

        logo = Image(
            logo_path,
            width=120,
            height=60
        )

        elementos.append(logo)

        elementos.append(
            Spacer(1, 10)
        )


    elementos.append(
        Paragraph(
            'FICHA DE ENTREGA DE EQUIPAMENTO DE PROTEÇÃO INDIVIDUAL',
            styles['Heading2']
        )
    )

    elementos.append(Spacer(1, 20))

    # Dados do funcionário

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

    elementos.append(
        Paragraph(
            f'<b>Data de Emissão:</b> {date.today().strftime("%d/%m/%Y")}',
            styles['Normal']
        )
    )

    elementos.append(Spacer(1, 20))

    # Tabela

    dados = [
        ['EPI', 'Quantidade', 'Data Entrega']
    ]

    for entrega in entregas:

        dados.append([
            entrega.epi.nome,
            str(entrega.quantidade),
            entrega.data_entrega.strftime('%d/%m/%Y')
        ])

    tabela = Table(
        dados,
        colWidths=[250, 100, 120]
    )

    tabela.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D9EAD3')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ])
    )

    elementos.append(tabela)

    elementos.append(Spacer(1, 30))

    # Declaração

    elementos.append(
        Paragraph(
            '''
            Declaro ter recebido os equipamentos de proteção
            individual descritos acima e estar ciente da
            obrigatoriedade de sua utilização.
            ''',
            styles['Normal']
        )
    )

    elementos.append(Spacer(1, 30))
    
    ultima_entrega = entregas.first()
    
    print("ULTIMA ENTREGA:", ultima_entrega)

    if ultima_entrega:
        print("ASSINATURA:", ultima_entrega.assinatura)

    if (
        ultima_entrega and
        ultima_entrega.assinatura
    ):

        # elementos.append(
        #     Paragraph(
        #         '<b>Assinatura do Colaborador</b>',
        #         styles['Normal']
        #     )
        # )

        assinatura_img = Image(
            ultima_entrega.assinatura.path,
            width=180,
            height=80
        )
        assinatura_img.hAlign = 'LEFT'


        elementos.append(assinatura_img)

        elementos.append(Spacer(1, 20))

    # Assinaturas

    assinaturas = Table(
        [
            [
                '________________________',
                '________________________'
            ],
            [
                'Assinatura do Colaborador',
                'Responsável pela Entrega'
            ]
        ],
        colWidths=[250, 250]
    )

    elementos.append(assinaturas)

    doc.build(elementos)

    return response