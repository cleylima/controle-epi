from django.db import models

from funcionarios.models import Funcionario


class CredencialBiometrica(models.Model):

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE
    )

    credential_id = models.TextField(
        unique=True
    )

    public_key = models.TextField()

    sign_count = models.IntegerField(
        default=0
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    ativo = models.BooleanField(
        default=True
    )

    def __str__(self):

        return (
            f'{self.funcionario.nome}'
        )