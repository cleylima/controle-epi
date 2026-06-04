from django.contrib import admin

from .models import EntregaEPI


@admin.register(EntregaEPI)
class EntregaAdmin(admin.ModelAdmin):

    list_display = (
        'funcionario',
        'epi',
        'quantidade',
        'data_entrega'
    )