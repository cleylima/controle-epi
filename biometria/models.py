import uuid

from django.db import models
from django.utils import timezone

from funcionarios.models import Funcionario
from entregas.models import EntregaEPI


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


class SessaoValidacaoBiometrica(models.Model):

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        APROVADA = 'aprovada', 'Aprovada'
        REJEITADA = 'rejeitada', 'Rejeitada'
        EXPIRADA = 'expirada', 'Expirada'
        UTILIZADA = 'utilizada', 'Utilizada'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    entrega = models.ForeignKey(
        EntregaEPI,
        on_delete=models.CASCADE,
        related_name='sessoes_biometricas'
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='sessoes_biometricas'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )

    criada_em = models.DateTimeField(
        auto_now_add=True
    )

    expira_em = models.DateTimeField()

    concluida_em = models.DateTimeField(
        null=True,
        blank=True
    )

    ip_solicitante = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True
    )

    mensagem = models.CharField(
        max_length=255,
        blank=True
    )

    def expirou(self):
        return timezone.now() >= self.expira_em

    def __str__(self):
        return (
            f'{self.funcionario.nome} - '
            f'{self.get_status_display()}'
        )