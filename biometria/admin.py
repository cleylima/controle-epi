from django.contrib import admin

from .models import CredencialBiometrica


@admin.register(CredencialBiometrica)
class CredencialBiometricaAdmin(
    admin.ModelAdmin
):

    list_display = (
        'id',
        'funcionario',
        'criado_em'
    )

    search_fields = (
        'funcionario__nome',
    )