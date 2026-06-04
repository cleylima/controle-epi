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