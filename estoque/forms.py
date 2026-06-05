from django import forms
from .models import EPI


class EPIForm(forms.ModelForm):

    class Meta:
        model = EPI

        fields = [
            'nome',
            'ca',
            'fabricante',
            'validade_ca',
            'vida_util_dias',
            'estoque_minimo',
            'quantidade_estoque',
            'ativo'
        ]

        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ca': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'validade_ca': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'vida_util_dias': forms.NumberInput(attrs={'class': 'form-control'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade_estoque': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
