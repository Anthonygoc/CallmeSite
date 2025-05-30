from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf', 'idade', 'cidade', 'pais', 'data_cadastro')
    search_fields = ('nome', 'email', 'cpf')
    list_filter = ('cidade', 'pais', 'data_cadastro')
