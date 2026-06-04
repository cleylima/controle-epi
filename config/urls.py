from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    
    path('estoque/', include('estoque.urls')),
]