from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth.views import LogoutView

# Importe TODAS as views, incluindo as que ainda vamos detalhar
from myapp.views import (
    home,
    registro_usuario,
    admin_registro,
    admin_login,
    admin_dashboard,
    usuario_editar,
    usuario_deletar,

    # Views do Carrinho e Pagamento (essas são as que faltam)
    adicionar_ao_carrinho,
    ver_carrinho,
    remover_do_carrinho,
    checkout,
    pagamento_sucesso,
    pagamento_falha,
    pagamento_pendente,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('registro/', registro_usuario, name='registro_usuario'),

    # === ROTAS DO CARRINHO - AQUI ESTÁ A SOLUÇÃO! ===
    path('carrinho/', ver_carrinho, name='ver_carrinho'), # <--- ESTA LINHA RESOLVE O ERRO
    path('carrinho/adicionar/<int:produto_id>/', adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:produto_id>/', remover_do_carrinho, name='remover_do_carrinho'),

    # === ROTAS DO CHECKOUT ===
    path('checkout/', checkout, name='checkout'),
    path('pagamento/sucesso/', pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/falha/', pagamento_falha, name='pagamento_falha'),
    path('pagamento/pendente/', pagamento_pendente, name='pagamento_pendente'),

    # URLs do painel administrativo
    path('painel/registro/', admin_registro, name='admin_registro'),
    path('painel/login/', admin_login, name='login'),
    path('painel/logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('painel/', admin_dashboard, name='admin_dashboard'),
    path('painel/usuario/<int:pk>/editar/', usuario_editar, name='usuario_editar'),
    path('painel/usuario/<int:pk>/deletar/', usuario_deletar, name='usuario_deletar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)