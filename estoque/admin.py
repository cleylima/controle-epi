from django.contrib import admin

from .models import (
    EPI,
    MovimentoEstoque
)

admin.site.register(EPI)
admin.site.register(MovimentoEstoque)