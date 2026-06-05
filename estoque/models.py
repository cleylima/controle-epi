from django.db import models


class EPI(models.Model):

    nome = models.CharField(
        max_length=150
    )

    ca = models.CharField(
        max_length=50
    )

    fabricante = models.CharField(
        max_length=150
    )

    validade_ca = models.DateField()

    vida_util_dias = models.PositiveIntegerField()

    estoque_minimo = models.PositiveIntegerField(
        default=0
    )

    quantidade_estoque = models.PositiveIntegerField(
        default=0
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nome
    
class MovimentoEstoque(models.Model):

    TIPOS = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
    ]

    epi = models.ForeignKey(
        EPI,
        on_delete=models.CASCADE
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    quantidade = models.PositiveIntegerField()

    observacao = models.TextField(
        blank=True,
        null=True
    )

    data_movimento = models.DateTimeField(
        auto_now_add=True
    )

    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.epi.nome} - {self.tipo}'