from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views  # Importe o módulo views

urlpatterns = [
    # --- ROTAS PÚBLICAS E DE CLIENTES ---
    path('', views.home, name='home'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),

    # --- ROTAS DO PAINEL DE ADMINISTRAÇÃO ---
    path('painel/admin/', admin.site.urls), # URL padrão do admin Django (opcional)
    path('painel/registro/', views.admin_registro, name='admin_registro'),
    path('painel/login/', views.admin_login, name='painel_login'),
    # Nota: O logout do admin pode usar a mesma view 'logout_usuario' ou ter uma específica.
    # Usar a mesma é mais simples.
    path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/usuario/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('painel/usuario/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
]

# Adiciona as URLs de mídia em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)