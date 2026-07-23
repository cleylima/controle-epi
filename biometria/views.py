import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from funcionarios.models import Funcionario

from .models import CredencialBiometrica


@login_required
def registrar_biometria(request, funcionario_id):

    funcionario = get_object_or_404(
        Funcionario,
        pk=funcionario_id
    )

    credencial = (
        CredencialBiometrica.objects
        .filter(
            funcionario=funcionario,
            ativo=True
        )
        .first()
    )

    return render(
        request,
        'biometria/registrar.html',
        {
            'funcionario': funcionario,
            'credencial': credencial,
            'possui_biometria': credencial is not None,
        }
    )


@login_required
@require_POST
def salvar_biometria(request, funcionario_id):

    funcionario = get_object_or_404(
        Funcionario,
        pk=funcionario_id
    )

    try:
        dados = json.loads(
            request.body.decode('utf-8')
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Dados inválidos.'
            },
            status=400
        )

    template_base64 = dados.get(
        'template',
        ''
    ).strip()

    if not template_base64:
        return JsonResponse(
            {
                'sucesso': False,
                'erro': 'Template biométrico não recebido.'
            },
            status=400
        )

    credencial, criada = (
        CredencialBiometrica.objects.update_or_create(
            funcionario=funcionario,
            defaults={
                'template_base64': template_base64,
                'ativo': True,
            }
        )
    )

    return JsonResponse({
        'sucesso': True,
        'criada': criada,
        'mensagem': (
            'Biometria cadastrada com sucesso.'
            if criada
            else 'Biometria atualizada com sucesso.'
        )
    })


@login_required
@require_POST
def excluir_biometria(request, funcionario_id):

    funcionario = get_object_or_404(
        Funcionario,
        pk=funcionario_id
    )

    CredencialBiometrica.objects.filter(
        funcionario=funcionario
    ).delete()

    return redirect(
        'registrar_biometria',
        funcionario_id=funcionario.id
    )