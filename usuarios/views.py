from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView


class MeuLoginView(LoginView):
    template_name = 'usuarios/login.html'


class MeuLogoutView(LogoutView):
    pass