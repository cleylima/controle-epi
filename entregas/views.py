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
    Image
)

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

import qrcode
from io import BytesIO

@login_required
def listar_entregas(request):

    entregas = EntregaEPI.objects.all()

    if request.GET.get('pendentes'):
        entregas = entregas.filter(confirmado=False)
    
    pendentes = entregas.count()

    return render(
        request,
        'entregas/listar.html',
        {
            'entregas': entregas,
            'pendentes': pendentes,
        }
    )

@login_required
def nova_entrega(request):

    print(request.POST.get("itens_entrega"))
    
    if request.method == 'POST':
        
        itens = json.loads(
        request.POST.get("itens_entrega")
        )

        print(itens)

        form = EntregaForm(request.POST)

        if form.is_valid():

            funcionario = form.cleaned_data["funcionario"]
            data_entrega = form.cleaned_data["data_entrega"]

            token = str(uuid.uuid4())

            from estoque.models import EPI

            for item in itens:

                epi = EPI.objects.get(pk=item["epi_id"])
                quantidade = int(item["quantidade"])

                # Validação de estoque
                if quantidade > epi.quantidade_estoque:
                    continue

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

    entrega = get_object_or_404(
        EntregaEPI,
        pk=pk
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'inline; filename=entrega_{entrega.id}.pdf'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(
            'COMPROVANTE DE ENTREGA DE EPI',
            styles['Title']
        )
    )

    elementos.append(
        Spacer(1, 20)
    )

    elementos.append(
        Paragraph(
            f'<b>Funcionário:</b> {entrega.funcionario.nome}',
            styles['Normal']
        )
    )

    elementos.append(
        Paragraph(
            f'<b>Setor:</b> {entrega.funcionario.setor}',
            styles['Normal']
        )
    )

    elementos.append(
        Paragraph(
            f'<b>Função:</b> {entrega.funcionario.funcao}',
            styles['Normal']
        )
    )

    elementos.append(
        Spacer(1, 20)
    )

    dados = [

        ['Campo', 'Informação'],

        ['EPI', entrega.epi.nome],

        ['Quantidade', str(entrega.quantidade)],

        ['Motivo', entrega.get_motivo_display()],

        ['Data Entrega',
         entrega.data_entrega.strftime('%d/%m/%Y')],

        ['Próxima Troca',
         entrega.data_proxima_troca.strftime('%d/%m/%Y')],
    ]

    tabela = Table(
        dados,
        colWidths=[150, 300]
    )

    tabela.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0),
             colors.lightgrey),

            ('GRID', (0, 0), (-1, -1),
             1, colors.black),

            ('FONTNAME', (0, 0), (-1, 0),
             'Helvetica-Bold'),
        ])
    )

    elementos.append(tabela)
    
    elementos.append(
        Spacer(1, 20)   
    )

    status = (
        'SIM'
        if entrega.confirmado
        else 'NÃO'
    )

    elementos.append(
        Paragraph(
            f'<b>Recebimento Confirmado:</b> {status}',
            styles['Normal']
        )
    )

    if entrega.data_confirmacao:

        elementos.append(
            Paragraph(
                (
                    '<b>Data da Confirmação:</b> '
                    f'{entrega.data_confirmacao.strftime("%d/%m/%Y %H:%M")}'
                ),
                styles['Normal']
            )
        )

    if entrega.metodo_confirmacao:

        elementos.append(
            Paragraph(
                (
                    '<b>Método de Confirmação:</b> '
                    f'{entrega.get_metodo_confirmacao_display()}'
                ),
                styles['Normal']
            )
        )

    if entrega.token_confirmacao:

        elementos.append(
            Paragraph(
                (
                    '<b>Token:</b> '
                    f'{entrega.token_confirmacao}'
                ),
                styles['Normal']
            )
        )

    if entrega.assinatura:

        elementos.append(
            Spacer(1, 30)
        )

        elementos.append(
            Paragraph(
                '<b>Assinatura do Colaborador</b>',
                styles['Normal']
            )
        )

        assinatura = Image(
            entrega.assinatura.path,
            width=180,
            height=80
        )

        assinatura.hAlign = 'LEFT'

        elementos.append(
            assinatura
        )

    doc.build(elementos)

    return response

def confirmar_recebimento(request, token):

    entrega = get_object_or_404(
        EntregaEPI,
        token_confirmacao=token
    )
    
    if entrega.token_confirmacao is None:
        return render(
            request,
            'entregas/token_expirado.html'
        )

    if request.method == 'POST':

        entrega.confirmado = True

        entrega.data_confirmacao = (
            timezone.now()
        )
        entrega.metodo_confirmacao = 'biometria'
        entrega.token_confirmacao = None
        
        entrega.ip_confirmacao = (
            request.META.get(
                'REMOTE_ADDR'
            )
        )

        entrega.user_agent_confirmacao = (
            request.META.get(
                'HTTP_USER_AGENT'
            )
        )

        entrega.save()

        return render(
            request,
            'entregas/confirmado.html',
            {
                'entrega': entrega
            }
        )

    return render(
        request,
        'entregas/confirmar.html',
        {
            'entrega': entrega
        }
    )
    
@login_required
def qr_confirmacao(request, pk):

    entrega = get_object_or_404(
        EntregaEPI,
        pk=pk
    )

    url = (
        request.build_absolute_uri('/')
        .rstrip('/')
        + f'/entregas/confirmar/{entrega.token_confirmacao}/'
    )

    qr = qrcode.make(url)

    buffer = BytesIO()

    qr.save(buffer, format='PNG')

    return HttpResponse(
        buffer.getvalue(),
        content_type='image/png'
    )