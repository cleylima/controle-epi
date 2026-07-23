from django.db import models

from funcionarios.models import Funcionario


class CredencialBiometrica(models.Model):

    funcionario = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='credencial_biometrica'
    )

    template_base64 = models.TextField()

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    ativo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f'Biometria de {self.funcionario.nome}'