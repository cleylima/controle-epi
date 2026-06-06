from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView


class MeuLoginView(LoginView):
    template_name = 'usuarios/login.html'


class MeuLogoutView(LogoutView):
    pass

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
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
    
    
@user_passes_test(eh_administrador)
@login_required
def editar_usuario(request, pk):

    usuario = get_object_or_404(
        User,
        pk=pk
    )

    if request.method == 'POST':

        form = UsuarioForm(
            request.POST
        )

        if form.is_valid():

            usuario.first_name = form.cleaned_data['first_name']
            usuario.username = form.cleaned_data['username']
            usuario.email = form.cleaned_data['email']
            usuario.is_active = form.cleaned_data['is_active']

            senha = form.cleaned_data['password']

            if senha:
                usuario.set_password(senha)

            usuario.save()

            grupo = form.cleaned_data['grupo']

            usuario.groups.clear()
            usuario.groups.add(grupo)

            return redirect(
                'listar_usuarios'
            )

    else:

        grupo_atual = None

        if usuario.groups.exists():
            grupo_atual = usuario.groups.first()

        form = UsuarioForm(
            initial={
                'first_name': usuario.first_name,
                'username': usuario.username,
                'email': usuario.email,
                'is_active': usuario.is_active,
                'grupo': grupo_atual,
            }
        )

    return render(
        request,
        'usuarios/form.html',
        {
            'form': form
        }
    )
  
@user_passes_test(eh_administrador)
@login_required
def alternar_status_usuario(request, pk):
    

    usuario = get_object_or_404(
        User,
        pk=pk
    )
    
    if usuario.id == request.user.id:
        return redirect('listar_usuarios')
    
    usuario.is_active = not usuario.is_active

    usuario.save()

    return redirect(
        'listar_usuarios'
    )  
