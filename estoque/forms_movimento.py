from django import forms

from .models import MovimentoEstoque


class MovimentoEstoqueForm(forms.ModelForm):

    class Meta:

        model = MovimentoEstoque

        fields = [
            'epi',
            'tipo',
            'quantidade',
            'observacao'
        ]

        widgets = {

            'epi': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'tipo': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'quantidade': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Digite a quantidade'
                }
            ),

            'observacao': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Observações da movimentação'
                }
            ),
        }