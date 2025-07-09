from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    # Rotas Públicas e de Clientes
    path('', views.home, name='home'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('pagamento/processar/', views.processar_pagamento, name='processar_pagamento'),
    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('meus-pedidos/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('pagamento/regerar/<int:pedido_id>/', views.regerar_pagamento, name='regerar_pagamento'),
    path('webhook/mercado-pago/', views.webhook_mercado_pago, name='webhook_mercado_pago'),
    path('pedido/status/<int:pedido_id>/', views.verificar_status_pedido, name='verificar_status_pedido'),

    # Rotas do Painel de Administração
    path('painel/admin/', admin.site.urls),
    path('painel/registro/', views.admin_registro, name='admin_registro'),
    path('painel/login/', views.admin_login, name='painel_login'),
    path('painel/logout/', views.logout_usuario, name='painel_logout'),
    path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/usuario/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('painel/usuario/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
]

# --- LINHA ADICIONADA PARA SERVIR IMAGENS EM DESENVOLVIMENTO ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
