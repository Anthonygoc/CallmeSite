from django.contrib import admin
from .models import Usuario, Produto, Pedido, ItemPedido

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf', 'idade', 'cidade', 'pais', 'data_cadastro')
    search_fields = ('nome', 'email', 'cpf')
    list_filter = ('cidade', 'pais', 'data_cadastro')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'disponivel', 'estoque')
    list_filter = ('disponivel', 'data_criacao')
    search_fields = ('nome',)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    raw_id_fields = ['produto']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'data_pedido')
    list_filter = ('estado', 'data_pedido')
    inlines = [ItemPedidoInline]