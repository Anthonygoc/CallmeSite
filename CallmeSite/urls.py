from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    # --- ROTAS PÚBLICAS E DE CLIENTES ---
    path('', views.home, name='home'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),  # Logout para clientes
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('pagamento/processar/', views.processar_pagamento, name='processar_pagamento'),

    # --- ROTAS DO PAINEL DE ADMINISTRAÇÃO ---
    path('painel/admin/', admin.site.urls),
    path('painel/registro/', views.admin_registro, name='admin_registro'),
    path('painel/login/', views.admin_login, name='painel_login'),

    # --- ROTA CORRIGIDA ABAIXO ---
    # Adicionando a rota que o seu dashboard está procurando.
    path('painel/logout/', views.logout_usuario, name='painel_logout'),

    path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/usuario/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('painel/usuario/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)