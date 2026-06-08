from django.shortcuts import (
    render,
    redirect
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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .forms import EntregaForm
from .models import EntregaEPI
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import base64
from django.core.files.base import ContentFile

import qrcode
from io import BytesIO
from django.http import HttpResponse

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
                

                entrega.token_confirmacao = str(
                    uuid.uuid4()
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

    if request.method == 'POST':

        entrega.confirmado = True

        entrega.data_confirmacao = (
            timezone.now()
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