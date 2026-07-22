from django.db import models

from funcionarios.models import Funcionario
from estoque.models import EPI

from datetime import date


class EntregaEPI(models.Model):
    
   

    MOTIVOS = [
        ('primeira', 'Primeira Entrega'),
        ('troca', 'Troca por Desgaste'),
        ('perda', 'Perda'),
        ('danificado', 'Danificado'),
    ]

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE
    )

    epi = models.ForeignKey(
        EPI,
        on_delete=models.CASCADE
    )

    quantidade = models.PositiveIntegerField()

    motivo = models.CharField(
        max_length=20,
        choices=MOTIVOS
    )

    data_entrega = models.DateField()

    criado_em = models.DateTimeField(
        auto_now_add=True
        
    )
    
    ativo = models.BooleanField(
        default=True
    )
    data_proxima_troca = models.DateField(
        null=True,
        blank=True
    )
    
    assinatura = models.ImageField(
        upload_to='assinaturas/',
        null=True,
        blank=True
    )
    
    confirmado = models.BooleanField(
        default=False
    )

    data_confirmacao = models.DateTimeField(
        null=True,
        blank=True
    )

    token_confirmacao = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    metodo_confirmacao = models.CharField(
        max_length=30,
        blank=True,
        null=True
        )

    biometria_confirmada = models.BooleanField(
        default=False
    )
    
    ip_confirmacao = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent_confirmacao = models.TextField(
        null=True,
        blank=True
    )
    
    METODOS_CONFIRMACAO = [
        ('assinatura', 'Assinatura'),
        ('qr_code', 'QR Code'),
        ('biometria', 'Biometria'),
    ]

    metodo_confirmacao = models.CharField(
        max_length=20,
        choices=METODOS_CONFIRMACAO,
        blank=True,
        null=True
    )
    
    @property
    def status_troca(self):

        if not self.data_proxima_troca:
            return 'sem_data'

        hoje = date.today()

        if self.data_proxima_troca < hoje:
            return 'vencido'

        dias_restantes = (
            self.data_proxima_troca - hoje
        ).days

        if dias_restantes <= 30:
            return 'proximo'

        return 'vigente'
    

    def __str__(self):
        return f'{self.funcionario} - {self.epi}'
    
    