from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView


class MeuLoginView(LoginView):
    template_name = 'usuarios/login.html'


class MeuLogoutView(LogoutView):
    pass

from django.shortcuts import (
    render,
    redirect
)

from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import UsuarioForm


def eh_administrador(user):
    return user.groups.filter(
        name='Administrador'
    ).exists()

@user_passes_test(eh_administrador)
@login_required
def listar_usuarios(request):

    usuarios = User.objects.all()

    return render(
        request,
        'usuarios/listar.html',
        {
            'usuarios': usuarios
        }
    )

@user_passes_test(eh_administrador)
@login_required
def novo_usuario(request):

    if request.method == 'POST':

        form = UsuarioForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                'listar_usuarios'
            )

    else:

        form = UsuarioForm()

    return render(
        request,
        'usuarios/form.html',
        {
            'form': form
        }
    )
    
