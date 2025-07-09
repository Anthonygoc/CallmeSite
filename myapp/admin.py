from django.contrib import admin
from .models import Usuario, Administrador, Produto, Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('produto', 'quantidade', 'preco_unitario', 'subtotal')
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'data_pedido', 'valor_total', 'status')
    list_filter = ('status', 'data_pedido')
    search_fields = ('usuario__username', 'id')
    inlines = [ItemPedidoInline]

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'estoque', 'disponivel')
    list_filter = ('disponivel', 'data_criacao')
    search_fields = ('nome', 'descricao')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf', 'data_cadastro')
    search_fields = ('nome', 'email', 'cpf')

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('user', 'nome_completo')
    search_fields = ('nome_completo',)