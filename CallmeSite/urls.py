"""
URL configuration for CallmeSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from myapp.views import (
    home, registro_usuario, admin_registro, admin_login,
    admin_dashboard, usuario_editar, usuario_deletar
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin
    path('', home, name='home'),
    path('registro/', registro_usuario, name='registro_usuario'),
    
    # URLs do sistema administrativo personalizado
    path('painel/registro/', admin_registro, name='admin_registro'),
    path('painel/login/', admin_login, name='login'),
    path('painel/logout/', LogoutView.as_view(), name='logout'),
    path('painel/', admin_dashboard, name='admin_dashboard'),
    path('painel/usuario/<int:pk>/editar/', usuario_editar, name='usuario_editar'),
    path('painel/usuario/<int:pk>/deletar/', usuario_deletar, name='usuario_deletar'),
]
