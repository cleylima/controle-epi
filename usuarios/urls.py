from django.urls import path

from .views import (
    MeuLoginView,
    MeuLogoutView
)

urlpatterns = [

    path(
        'login/',
        MeuLoginView.as_view(),
        name='login'
    ),

    path(
        'logout/',
        MeuLogoutView.as_view(),
        name='logout'
    ),

]