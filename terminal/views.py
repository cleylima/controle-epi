import json
import secrets

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from biometria.models import (
    CredencialBiometrica,
    SessaoValidacaoBiometrica
)
from entregas.models import EntregaEPI


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
def iniciar_validacao_biometrica(request):

    entrega_id = request.POST.get('entrega')

    if not entrega_id:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Entrega não informada.'
            },
            status=400
        )

    entrega = get_object_or_404(
        EntregaEPI.objects.select_related(
            'funcionario'
        ),
        pk=entrega_id,
        confirmado=False
    )

    funcionario = entrega.funcionario

    existe_biometria = (
        CredencialBiometrica.objects
        .filter(
            funcionario=funcionario,
            ativo=True
        )
        .exists()
    )

    if not existe_biometria:
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

    SessaoValidacaoBiometrica.objects.filter(
        entrega=entrega,
        status=SessaoValidacaoBiometrica.Status.PENDENTE
    ).update(
        status=SessaoValidacaoBiometrica.Status.EXPIRADA
    )

    sessao = SessaoValidacaoBiometrica.objects.create(
        entrega=entrega,
        funcionario=funcionario,
        expira_em=timezone.now() + timedelta(minutes=2),
        ip_solicitante=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get(
            'HTTP_USER_AGENT',
            ''
        )
    )

    return JsonResponse(
        {
            'sucesso': True,
            'sessao': str(sessao.id),
            'funcionario': funcionario.nome
        }
    )

@csrf_exempt
@require_GET
def dados_validacao_biometrica(request, sessao_id):

    chave_recebida = request.headers.get(
        'X-Biometria-Key',
        ''
    )

    chave_esperada = settings.BIOMETRIA_SERVICE_KEY

    if (
        not chave_esperada
        or not secrets.compare_digest(
            chave_recebida,
            chave_esperada
        )
    ):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Serviço biométrico não autorizado.'
            },
            status=403
        )

    sessao = get_object_or_404(
        SessaoValidacaoBiometrica.objects.select_related(
            'funcionario'
        ),
        pk=sessao_id
    )

    if sessao.status != (
        SessaoValidacaoBiometrica.Status.PENDENTE
    ):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Sessão biométrica indisponível.'
            },
            status=409
        )

    if sessao.expirou():
        sessao.status = (
            SessaoValidacaoBiometrica.Status.EXPIRADA
        )
        sessao.save(
            update_fields=['status']
        )

        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Sessão biométrica expirada.'
            },
            status=410
        )

    credencial = get_object_or_404(
        CredencialBiometrica,
        funcionario=sessao.funcionario,
        ativo=True
    )

    return JsonResponse(
        {
            'sucesso': True,
            'sessao': str(sessao.id),
            'template': credencial.template_base64,
            'funcionario': sessao.funcionario.nome
        }
    )

@csrf_exempt
@require_POST
def concluir_validacao_biometrica(request, sessao_id):

    chave_recebida = request.headers.get(
        'X-Biometria-Key',
        ''
    )

    chave_esperada = settings.BIOMETRIA_SERVICE_KEY

    if (
        not chave_esperada
        or not secrets.compare_digest(
            chave_recebida,
            chave_esperada
        )
    ):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Serviço biométrico não autorizado.'
            },
            status=403
        )

    try:
        dados = json.loads(
            request.body.decode('utf-8')
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError
    ):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'JSON inválido.'
            },
            status=400
        )

    corresponde = dados.get('corresponde')

    if not isinstance(corresponde, bool):
        return JsonResponse(
            {
                'sucesso': False,
                'erro': (
                    'O campo corresponde deve ser '
                    'verdadeiro ou falso.'
                )
            },
            status=400
        )

    with transaction.atomic():

        sessao = (
            SessaoValidacaoBiometrica.objects
            .select_for_update()
            .select_related(
                'entrega',
                'funcionario'
            )
            .get(pk=sessao_id)
        )

        if sessao.status != (
            SessaoValidacaoBiometrica.Status.PENDENTE
        ):
            return JsonResponse(
                {
                    'sucesso': False,
                    'erro': 'Sessão já processada.'
                },
                status=409
            )

        if sessao.expirou():
            sessao.status = (
                SessaoValidacaoBiometrica.Status.EXPIRADA
            )
            sessao.save(
                update_fields=['status']
            )

            return JsonResponse(
                {
                    'sucesso': False,
                    'erro': 'Sessão expirada.'
                },
                status=410
            )

        sessao.concluida_em = timezone.now()

        if corresponde:
            sessao.status = (
                SessaoValidacaoBiometrica.Status.APROVADA
            )
            sessao.mensagem = 'Biometria confirmada.'
        else:
            sessao.status = (
                SessaoValidacaoBiometrica.Status.REJEITADA
            )
            sessao.mensagem = (
                'A digital não corresponde ao funcionário.'
            )

        sessao.save(
            update_fields=[
                'status',
                'concluida_em',
                'mensagem'
            ]
        )

    return JsonResponse(
        {
            'sucesso': True,
            'corresponde': corresponde
        }
    )
    
@require_GET
def status_validacao_biometrica(
    request,
    sessao_id
):

    sessao = get_object_or_404(
        SessaoValidacaoBiometrica.objects.select_related(
            'entrega',
            'funcionario'
        ),
        pk=sessao_id
    )

    if sessao.expirou() and sessao.status == (
        SessaoValidacaoBiometrica.Status.PENDENTE
    ):
        sessao.status = (
            SessaoValidacaoBiometrica.Status.EXPIRADA
        )
        sessao.save(
            update_fields=['status']
        )

    if sessao.status == (
        SessaoValidacaoBiometrica.Status.APROVADA
    ):

        agora = timezone.now()

        with transaction.atomic():

            sessao = (
                SessaoValidacaoBiometrica.objects
                .select_for_update()
                .select_related(
                    'entrega',
                    'funcionario'
                )
                .get(pk=sessao.pk)
            )

            if sessao.status == (
                SessaoValidacaoBiometrica.Status.UTILIZADA
            ):
                return JsonResponse(
                    {
                        'sucesso': True,
                        'status': 'utilizada',
                        'mensagem': (
                            'Entrega já confirmada.'
                        )
                    }
                )

            entrega = sessao.entrega

            if entrega.token_confirmacao:
                entregas = EntregaEPI.objects.filter(
                    token_confirmacao=(
                        entrega.token_confirmacao
                    ),
                    funcionario=sessao.funcionario,
                    confirmado=False
                )
            else:
                entregas = EntregaEPI.objects.filter(
                    pk=entrega.pk,
                    funcionario=sessao.funcionario,
                    confirmado=False
                )

            quantidade = entregas.update(
                confirmado=True,
                biometria_confirmada=True,
                metodo_confirmacao='biometria',
                data_confirmacao=agora,
                ip_confirmacao=sessao.ip_solicitante,
                user_agent_confirmacao=(
                    sessao.user_agent
                )
            )

            sessao.status = (
                SessaoValidacaoBiometrica.Status.UTILIZADA
            )
            sessao.save(
                update_fields=['status']
            )

        return JsonResponse(
            {
                'sucesso': True,
                'status': 'confirmada',
                'mensagem': (
                    f'Biometria de '
                    f'{sessao.funcionario.nome} confirmada. '
                    f'{quantidade} EPI(s) confirmado(s).'
                )
            }
        )

    return JsonResponse(
        {
            'sucesso': True,
            'status': sessao.status,
            'mensagem': sessao.mensagem
        }
    )