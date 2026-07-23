import json
import socket
import urllib.error
import urllib.request

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from biometria.models import CredencialBiometrica
from entregas.models import EntregaEPI


BIOMETRIA_SERVICE_URL = 'http://127.0.0.1:5055/validar'


def painel_terminal(request):

    entregas = (
        EntregaEPI.objects
        .filter(confirmado=False)
        .select_related(
            'funcionario',
            'epi'
        )
        .order_by(
            'funcionario__nome'
        )
    )

    funcionarios = {}

    for entrega in entregas:

        funcionario = entrega.funcionario

        if funcionario.id not in funcionarios:
            funcionarios[funcionario.id] = {
                'funcionario': funcionario,
                'entregas': [],
                'primeira_entrega': entrega,
                'id_entrega': entrega.id,
            }

        funcionarios[funcionario.id]['entregas'].append(
            entrega
        )

    return render(
        request,
        'terminal/painel.html',
        {
            'funcionarios': funcionarios.values()
        }
    )


@require_POST
def validar_biometria_ajax(request):

    entrega_id = request.POST.get('entrega')

    if not entrega_id:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Entrega não informada.'
            },
            status=400
        )

    entrega_referencia = get_object_or_404(
        EntregaEPI.objects.select_related(
            'funcionario'
        ),
        pk=entrega_id,
        confirmado=False
    )

    funcionario = entrega_referencia.funcionario

    try:
        credencial = CredencialBiometrica.objects.get(
            funcionario=funcionario,
            ativo=True
        )
    except CredencialBiometrica.DoesNotExist:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': (
                    f'{funcionario.nome} não possui '
                    'biometria cadastrada.'
                )
            },
            status=400
        )

    payload = json.dumps(
        {
            'template': credencial.template_base64
        }
    ).encode('utf-8')

    requisicao = urllib.request.Request(
        BIOMETRIA_SERVICE_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(
            requisicao,
            timeout=40
        ) as resposta:

            corpo = resposta.read().decode('utf-8')
            resultado_biometria = json.loads(corpo)

    except urllib.error.HTTPError as erro:

        try:
            corpo_erro = erro.read().decode('utf-8')
            dados_erro = json.loads(corpo_erro)
            mensagem = dados_erro.get(
                'erro',
                'Erro no serviço biométrico.'
            )
        except Exception:
            mensagem = 'Erro no serviço biométrico.'

        return JsonResponse(
            {
                'sucesso': False,
                'erro': mensagem
            },
            status=erro.code
        )

    except (
        urllib.error.URLError,
        ConnectionRefusedError
    ):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': (
                    'O serviço biométrico está offline. '
                    'Abra o BiometriaService e tente novamente.'
                )
            },
            status=503
        )

    except socket.timeout:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'O tempo da leitura biométrica expirou.'
            },
            status=408
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': (
                    'O serviço biométrico retornou '
                    'uma resposta inválida.'
                )
            },
            status=502
        )

    except Exception as erro:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': (
                    'Não foi possível realizar a validação: '
                    f'{str(erro)}'
                )
            },
            status=500
        )

    if not resultado_biometria.get('sucesso'):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': resultado_biometria.get(
                    'erro',
                    'Não foi possível validar a biometria.'
                )
            },
            status=400
        )

    if not resultado_biometria.get('corresponde'):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': (
                    'A digital informada não corresponde '
                    f'a {funcionario.nome}.'
                )
            },
            status=403
        )

    agora = timezone.now()

    # A confirmação é feita em transação para impedir
    # confirmação duplicada.
    with transaction.atomic():

        entrega_referencia = (
            EntregaEPI.objects
            .select_for_update()
            .get(pk=entrega_referencia.pk)
        )

        if entrega_referencia.confirmado:
            return JsonResponse(
                {
                    'sucesso': False,
                    'erro': 'Esta entrega já foi confirmada.'
                },
                status=409
            )

        if entrega_referencia.token_confirmacao:

            entregas = EntregaEPI.objects.filter(
                token_confirmacao=(
                    entrega_referencia.token_confirmacao
                ),
                funcionario=funcionario,
                confirmado=False
            )

        else:
            entregas = EntregaEPI.objects.filter(
                pk=entrega_referencia.pk,
                funcionario=funcionario,
                confirmado=False
            )

        quantidade_confirmada = entregas.update(
            confirmado=True,
            biometria_confirmada=True,
            metodo_confirmacao='biometria',
            data_confirmacao=agora,
            ip_confirmacao=request.META.get(
                'REMOTE_ADDR'
            ),
            user_agent_confirmacao=request.META.get(
                'HTTP_USER_AGENT',
                ''
            )
        )

    return JsonResponse(
        {
            'sucesso': True,
            'quantidade_confirmada': quantidade_confirmada,
            'mensagem': (
                f'Biometria de {funcionario.nome} confirmada. '
                f'{quantidade_confirmada} EPI(s) '
                'confirmado(s) com sucesso.'
            )
        }
    )