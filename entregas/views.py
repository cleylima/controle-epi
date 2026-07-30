from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import uuid
import json
from django.http import HttpResponse
from .forms import EntregaForm
from .models import EntregaEPI
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from collections import OrderedDict

@login_required
def listar_entregas(request):

    registros = (
        EntregaEPI.objects
        .select_related(
            'funcionario',
            'epi'
        )
        .order_by(
            '-data_entrega',
            '-id'
        )
    )

    grupos = OrderedDict()

    for registro in registros:

        # Entregas novas são agrupadas pelo token.
        # Registros antigos sem token permanecem separados.
        chave = (
            str(registro.token_confirmacao)
            if registro.token_confirmacao
            else f'registro-{registro.id}'
        )

        if chave not in grupos:

            grupos[chave] = {
                'referencia': registro,
                'funcionario': registro.funcionario,
                'data_entrega': registro.data_entrega,
                'token': registro.token_confirmacao,
                'itens': [],
                'quantidade_itens': 0,
                'quantidade_total': 0,
                'confirmado': True,
                'data_confirmacao': registro.data_confirmacao,
                'metodo_confirmacao': (
                    registro.metodo_confirmacao
                ),
            }

        grupos[chave]['itens'].append(registro)

        grupos[chave]['quantidade_itens'] += 1

        grupos[chave]['quantidade_total'] += (
            registro.quantidade
        )

        # O grupo só estará confirmado se todos os itens estiverem.
        if not registro.confirmado:
            grupos[chave]['confirmado'] = False

        if (
            not grupos[chave]['data_confirmacao']
            and registro.data_confirmacao
        ):
            grupos[chave]['data_confirmacao'] = (
                registro.data_confirmacao
            )

    entregas_agrupadas = list(
        grupos.values()
    )

    return render(
        request,
        'entregas/listar.html',
        {
            'entregas_agrupadas': entregas_agrupadas
        }
    )

@login_required
def nova_entrega(request):

    if request.method == 'POST':

        itens_json = request.POST.get(
            "itens_entrega",
            "[]"
        )

        itens = json.loads(itens_json)

        form = EntregaForm(request.POST)

        if form.is_valid():

            funcionario = form.cleaned_data["funcionario"]
            data_entrega = form.cleaned_data["data_entrega"]

            token = str(uuid.uuid4())

            from estoque.models import EPI

            for item in itens:

                epi = get_object_or_404(
                    EPI,
                    pk=item["epi_id"]
                )
                quantidade = int(item["quantidade"])

                # Validação de estoque
                if epi.quantidade_estoque <= 0:

                    form.add_error(
                        None,
                        f'O EPI "{epi.nome}" está sem estoque.'
                    )

                    return render(
                        request,
                        "entregas/form.html",
                        {"form": form}
                    )

                if quantidade > epi.quantidade_estoque:

                    form.add_error(
                        None,
                        (
                            f'O EPI "{epi.nome}" não possui estoque suficiente. '
                            f'Disponível: {epi.quantidade_estoque} unidade(s).'
                        )
                    )

                    return render(
                        request,
                        'entregas/form.html',
                        {
                            'form': form
                        }
                    )
                # Baixa estoque
                epi.quantidade_estoque -= quantidade
                epi.save()

                # Desativa entrega anterior
                EntregaEPI.objects.filter(
                    funcionario=funcionario,
                    epi=epi,
                    ativo=True
                ).update(
                    ativo=False
                )

                # Nova entrega
                EntregaEPI.objects.create(

                    funcionario=funcionario,

                    epi=epi,

                    quantidade=quantidade,

                    motivo=item["motivo"],

                    data_entrega=data_entrega,

                    data_proxima_troca=(
                        data_entrega +
                        timedelta(days=epi.vida_util_dias)
                    ),

                    token_confirmacao=token,

                    confirmado=False,

                    ativo=True

                )

            return redirect("listar_entregas")

        else:

            print("ERROS DO FORMULÁRIO:")
            print(form.errors)

    else:

        funcionario_id = request.GET.get(
            'funcionario'
        )

        epi_id = request.GET.get(
            'epi'
        )

        form = EntregaForm(
            initial={
                'funcionario': funcionario_id,
                'epi': epi_id,
            }
        )

        if funcionario_id and epi_id:

            ultima_entrega = (
                EntregaEPI.objects
                .filter(
                    funcionario_id=funcionario_id,
                    epi_id=epi_id
                )
                .order_by('-data_entrega')
                .first()
            )

            if ultima_entrega:

                form.initial.update({
                    'funcionario': funcionario_id,
                    'epi': epi_id,
                    'quantidade': ultima_entrega.quantidade,
                    'motivo': 'troca'
                })

    return render(
        request,
        'entregas/form.html',
        {
            'form': form
        }
    )
    
@login_required
def gerar_entrega_pdf(request, pk):

    entrega_referencia = get_object_or_404(
        EntregaEPI.objects.select_related(
            'funcionario',
            'epi'
        ),
        pk=pk
    )

    if entrega_referencia.token_confirmacao:

        entregas = list(
            EntregaEPI.objects
            .filter(
                token_confirmacao=(
                    entrega_referencia.token_confirmacao
                )
            )
            .select_related(
                'funcionario',
                'epi'
            )
            .order_by('id')
        )

    else:

        entregas = [entrega_referencia]

    entrega = entregas[0]
    funcionario = entrega.funcionario

    response = HttpResponse(
        content_type='application/pdf'
    )

    nome_arquivo = (
        f'ficha_epi_{funcionario.id}_'
        f'{entrega.data_entrega:%Y%m%d}.pdf'
    )

    response['Content-Disposition'] = (
        f'inline; filename="{nome_arquivo}"'
    )

    documento = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title='Comprovante de Entrega de EPI',
        author='EcoCristal',
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        name='TituloEPI',
        parent=estilos['Title'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    estilo_subtitulo = ParagraphStyle(
        name='SubtituloEPI',
        parent=estilos['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=6,
    )

    estilo_normal = ParagraphStyle(
        name='NormalEPI',
        parent=estilos['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
    )

    estilo_centralizado = ParagraphStyle(
        name='CentralizadoEPI',
        parent=estilo_normal,
        alignment=TA_CENTER,
    )

    elementos = []

    elementos.append(
        Paragraph(
            'COMPROVANTE DE ENTREGA DE EPI',
            estilo_titulo
        )
    )

    dados_funcionario = [
        [
            Paragraph(
                '<b>Funcionário:</b>',
                estilo_normal
            ),
            Paragraph(
                funcionario.nome,
                estilo_normal
            ),
        ],
        [
            Paragraph(
                '<b>Setor:</b>',
                estilo_normal
            ),
            Paragraph(
                str(funcionario.setor),
                estilo_normal
            ),
        ],
        [
            Paragraph(
                '<b>Função:</b>',
                estilo_normal
            ),
            Paragraph(
                str(funcionario.funcao),
                estilo_normal
            ),
        ],
        [
            Paragraph(
                '<b>Data da entrega:</b>',
                estilo_normal
            ),
            Paragraph(
                entrega.data_entrega.strftime(
                    '%d/%m/%Y'
                ),
                estilo_normal
            ),
        ],
    ]

    tabela_funcionario = Table(
        dados_funcionario,
        colWidths=[
            38 * mm,
            142 * mm
        ]
    )

    tabela_funcionario.setStyle(
        TableStyle([
            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                'BACKGROUND',
                (0, 0),
                (0, -1),
                colors.whitesmoke
            ),
            (
                'VALIGN',
                (0, 0),
                (-1, -1),
                'MIDDLE'
            ),
            (
                'LEFTPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'RIGHTPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    elementos.append(tabela_funcionario)
    elementos.append(Spacer(1, 7 * mm))

    elementos.append(
        Paragraph(
            'EPIs ENTREGUES',
            estilo_subtitulo
        )
    )

    dados_epis = [
        [
            Paragraph(
                '<b>EPI</b>',
                estilo_centralizado
            ),
            Paragraph(
                '<b>Qtd.</b>',
                estilo_centralizado
            ),
            Paragraph(
                '<b>Motivo</b>',
                estilo_centralizado
            ),
            Paragraph(
                '<b>Próxima troca</b>',
                estilo_centralizado
            ),
        ]
    ]

    for item in entregas:

        proxima_troca = '-'

        if item.data_proxima_troca:
            proxima_troca = (
                item.data_proxima_troca
                .strftime('%d/%m/%Y')
            )

        dados_epis.append([
            Paragraph(
                item.epi.nome,
                estilo_normal
            ),
            Paragraph(
                str(item.quantidade),
                estilo_centralizado
            ),
            Paragraph(
                item.get_motivo_display(),
                estilo_normal
            ),
            Paragraph(
                proxima_troca,
                estilo_centralizado
            ),
        ])

    tabela_epis = Table(
        dados_epis,
        repeatRows=1,
        colWidths=[
            72 * mm,
            18 * mm,
            55 * mm,
            35 * mm,
        ]
    )

    tabela_epis.setStyle(
        TableStyle([
            (
                'BACKGROUND',
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                'TEXTCOLOR',
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                'VALIGN',
                (0, 0),
                (-1, -1),
                'MIDDLE'
            ),
            (
                'ALIGN',
                (1, 1),
                (1, -1),
                'CENTER'
            ),
            (
                'ALIGN',
                (3, 1),
                (3, -1),
                'CENTER'
            ),
            (
                'LEFTPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
            (
                'RIGHTPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )

    elementos.append(tabela_epis)
    elementos.append(Spacer(1, 8 * mm))

    confirmado = all(
        item.confirmado
        for item in entregas
    )

    biometria_confirmada = any(
        getattr(
            item,
            'biometria_confirmada',
            False
        )
        for item in entregas
    )

    data_confirmacao = next(
        (
            item.data_confirmacao
            for item in entregas
            if item.data_confirmacao
        ),
        None
    )

    metodo_confirmacao = next(
        (
            item.metodo_confirmacao
            for item in entregas
            if item.metodo_confirmacao
        ),
        None
    )

    if metodo_confirmacao == 'biometria':
        metodo_exibicao = 'Biometria'
    elif metodo_confirmacao:
        metodo_exibicao = (
            str(metodo_confirmacao)
            .replace('_', ' ')
            .title()
        )
    else:
        metodo_exibicao = '-'

    data_confirmacao_formatada = '-'

    if data_confirmacao:

        data_confirmacao_local = timezone.localtime(
            data_confirmacao
        )

        data_confirmacao_formatada = (
            data_confirmacao_local.strftime(
                '%d/%m/%Y %H:%M'
            )
        )

    status_confirmacao = (
        'SIM'
        if confirmado
        else 'NÃO'
    )

    status_biometria = (
        'SIM'
        if biometria_confirmada
        else 'NÃO'
    )

    elementos.append(
        Paragraph(
            'CONFIRMAÇÃO DE RECEBIMENTO',
            estilo_subtitulo
        )
    )

    dados_confirmacao = [
        [
            Paragraph(
                '<b>Recebimento confirmado:</b>',
                estilo_normal
            ),
            Paragraph(
                status_confirmacao,
                estilo_normal
            ),
        ],
        [
            Paragraph(
                '<b>Confirmação biométrica:</b>',
                estilo_normal
            ),
            Paragraph(
                status_biometria,
                estilo_normal
            ),
        ],
        [
            Paragraph(
                '<b>Data da confirmação:</b>',
                estilo_normal
            ),
            Paragraph(
                data_confirmacao_formatada,
                estilo_normal
            ),
        ],
        [
            Paragraph(
                '<b>Método:</b>',
                estilo_normal
            ),
            Paragraph(
                metodo_exibicao,
                estilo_normal
            ),
        ],
    ]

    if entrega.ip_confirmacao:

        dados_confirmacao.append([
            Paragraph(
                '<b>IP da confirmação:</b>',
                estilo_normal
            ),
            Paragraph(
                entrega.ip_confirmacao,
                estilo_normal
            ),
        ])

    if entrega.token_confirmacao:

        dados_confirmacao.append([
            Paragraph(
                '<b>Token da entrega:</b>',
                estilo_normal
            ),
            Paragraph(
                str(entrega.token_confirmacao),
                estilo_normal
            ),
        ])

    tabela_confirmacao = Table(
        dados_confirmacao,
        colWidths=[
            55 * mm,
            125 * mm
        ]
    )

    tabela_confirmacao.setStyle(
        TableStyle([
            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                'BACKGROUND',
                (0, 0),
                (0, -1),
                colors.whitesmoke
            ),
            (
                'VALIGN',
                (0, 0),
                (-1, -1),
                'MIDDLE'
            ),
            (
                'LEFTPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'RIGHTPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    elementos.append(tabela_confirmacao)
    elementos.append(Spacer(1, 9 * mm))

    declaracao = (
        'Declaro que recebi os equipamentos de proteção '
        'individual relacionados acima, em boas condições '
        'de uso, e que fui orientado quanto ao uso correto, '
        'guarda, conservação e substituição dos equipamentos.'
    )

    elementos.append(
        Paragraph(
            declaracao,
            estilo_normal
        )
    )

    elementos.append(Spacer(1, 12 * mm))

    rodape = (
        'Documento gerado eletronicamente pelo Sistema '
        'de Controle de EPI.'
    )

    elementos.append(
        Paragraph(
            rodape,
            estilo_centralizado
        )
    )

    documento.build(elementos)

    return response