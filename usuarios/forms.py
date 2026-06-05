from django import forms
from django.contrib.auth.models import User, Group


class UsuarioForm(forms.ModelForm):

    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Perfil',
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    class Meta:

        model = User

        fields = [
            'first_name',
            'username',
            'email',
            'is_active'
        ]

        labels = {
            'first_name': 'Nome Completo',
            'username': 'Usuário',
            'email': 'E-mail',
            'is_active': 'Ativo'
        }

        widgets = {

            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }

    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data['password']
        )

        if commit:

            user.save()

            grupo = self.cleaned_data['grupo']

            user.groups.clear()

            user.groups.add(grupo)

        return user