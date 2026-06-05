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
    
    data_proxima_troca = models.DateField(
        null=True,
        blank=True
    )
    
    @property
    def status_troca(self):

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
    
    