from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioForm
from .models import Usuario

def home(request):
    return render(request, 'home.html')

def registro_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                messages.success(request, f'Cadastro realizado com sucesso! Usuário {usuario.nome} foi registrado.')
                # Você pode escolher redirecionar para a página de sucesso em vez da home
                return render(request, 'registro_sucesso.html', {'usuario': usuario})
            except Exception as e:
                messages.error(request, f'Erro ao salvar no banco de dados: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
    else:
        form = UsuarioForm()
    
    return render(request, 'registro.html', {'form': form})
