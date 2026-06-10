from django.http import HttpResponse
import json, base64
from dataclasses import asdict
from webauthn import generate_registration_options
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import CredencialBiometrica
from funcionarios.models import Funcionario

from webauthn import (
    generate_registration_options
)


def registrar_biometria(
    request,
    funcionario_id
):

    funcionario = get_object_or_404(
        Funcionario,
        pk=funcionario_id
    )

    options = generate_registration_options(
        rp_id='localhost',
        rp_name='Controle EPI',
        user_id=str(funcionario.id).encode(),
        user_name=funcionario.nome,
    )

    

    request.session[
        'registration_challenge'
    ] = base64.b64encode(
        options.challenge
    ).decode('utf-8')

    print(
        request.session[
            'registration_challenge'
        ]
    )

    return render(
        request,
        'biometria/registrar.html',
        {
            'funcionario': funcionario
        }
    )
    
def opcoes_registro(
    request,
    funcionario_id
):

    funcionario = get_object_or_404(
        Funcionario,
        pk=funcionario_id
    )

    options = generate_registration_options(
        rp_id='localhost',
        rp_name='Controle EPI',
        user_id=str(funcionario.id).encode(),
        user_name=funcionario.nome,
    )

    request.session[
        'registration_challenge'
    ] = base64.b64encode(
        options.challenge
    ).decode()

    return JsonResponse({
        'challenge':
            base64.b64encode(
                options.challenge
            ).decode(),

        'rp': {
            'name': 'Controle EPI',
            'id': 'localhost'
        },

        'user': {
            'id':
                base64.b64encode(
                    str(funcionario.id).encode()
                ).decode(),

            'name': funcionario.nome,

            'displayName':
                funcionario.nome,
        },

        'pubKeyCredParams': [
            {
                'type': 'public-key',
                'alg': -7
            }
        ],

        'timeout': 60000,

        'attestation': 'none'
    })

def autenticar_biometria(
    request,
    entrega_id
):

    return HttpResponse(
        f'Autenticar biometria da entrega {entrega_id}'
    )
    
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def salvar_biometria(request):
    print("CHEGOU NA VIEW SALVAR")

    if request.method == 'POST':

        dados = json.loads(
            request.body
        )
        print(dados)

        funcionario_id = dados.get(
            'funcionario_id'
        )

        credential_id = dados.get(
            'credential_id'
        )

        funcionario = get_object_or_404(
            Funcionario,
            pk=funcionario_id
        )

        CredencialBiometrica.objects.get_or_create(
            funcionario=funcionario,
            credential_id=credential_id,
            defaults={
                'public_key': 'temporario'
            }
        )

        return JsonResponse({
            'status': 'ok'
        })

    return JsonResponse({
        'status': 'erro'
    })