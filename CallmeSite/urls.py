from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    # --- Client-Facing Routes ---
    path('', views.home, name='home'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('pagamento/processar/', views.processar_pagamento, name='processar_pagamento'),
    path('webhook/mercado-pago/', views.webhook_mercado_pago, name='webhook_mercado_pago'),
    path('pedido/status/<int:pedido_id>/', views.verificar_status_pedido, name='verificar_status_pedido'),
    path('pagamento/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),

    # --- Administration Panel Routes ---
    path('painel/admin/', admin.site.urls),

    # --- THE MISSING LINE IS ADDED BELOW ---
    path('painel/registro/', views.admin_registro, name='admin_registro'),

    path('painel/login/', views.admin_login, name='painel_login'),
    path('painel/logout/', views.logout_usuario, name='painel_logout'),
    path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/usuario/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('painel/usuario/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
]

# This is for serving media files (like product images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)