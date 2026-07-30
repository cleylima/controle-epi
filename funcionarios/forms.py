from django import forms
from .models import Funcionario
from django.core.exceptions import ValidationError

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario

        fields = [
            "nome",
            "email",
            "telefone",
            "cpf",
            "setor",
            "funcao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "000.000.000-00",
                    "maxlength": "14",
                    "autocomplete": "off",
                }
            ),
            "setor": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "funcao": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")

        # Permite registros antigos ou cadastro sem CPF,
        # caso o campo esteja configurado com blank=True.
        if not cpf:
            return cpf

        numeros = "".join(numero for numero in cpf if numero.isdigit())

        if len(numeros) != 11:
            raise ValidationError(
                "Informe um CPF com 11 dígitos."
            )

        # Bloqueia sequências repetidas, como 000.000.000-00.
        if numeros == numeros[0] * 11:
            raise ValidationError(
                "Informe um CPF válido."
            )

        primeiro_digito = self.calcular_digito_cpf(
            numeros[:9],
            peso_inicial=10,
        )

        segundo_digito = self.calcular_digito_cpf(
            numeros[:9] + str(primeiro_digito),
            peso_inicial=11,
        )

        if numeros[-2:] != f"{primeiro_digito}{segundo_digito}":
            raise ValidationError(
                "Informe um CPF válido."
            )

        # Salva o CPF sempre formatado.
        cpf_formatado = (
            f"{numeros[:3]}."
            f"{numeros[3:6]}."
            f"{numeros[6:9]}-"
            f"{numeros[9:]}"
        )

        consulta = Funcionario.objects.filter(cpf=cpf_formatado)

        if self.instance.pk:
            consulta = consulta.exclude(pk=self.instance.pk)

        if consulta.exists():
            raise ValidationError(
                "Já existe um funcionário cadastrado com este CPF."
            )

        return cpf_formatado

    @staticmethod
    def calcular_digito_cpf(numeros, peso_inicial):
        soma = sum(
            int(numero) * peso
            for numero, peso in zip(
                numeros,
                range(peso_inicial, 1, -1),
            )
        )

        resto = soma % 11

        return 0 if resto < 2 else 11 - resto