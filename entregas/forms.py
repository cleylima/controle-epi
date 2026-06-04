from django import forms

from .models import EntregaEPI


class EntregaForm(forms.ModelForm):

    class Meta:

        model = EntregaEPI

        fields = [
            'funcionario',
            'epi',
            'quantidade',
            'motivo',
            'data_entrega'
        ]

        widgets = {
            'funcionario': forms.Select(attrs={'class': 'form-control'}),
            'epi': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'motivo': forms.Select(attrs={'class': 'form-control'}),
            'data_entrega': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
        }