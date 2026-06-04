from django.contrib import admin
from .models import EPI


@admin.register(EPI)
class EPIAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'ca',
        'fabricante',
        'quantidade_estoque',
        'estoque_minimo'
    )