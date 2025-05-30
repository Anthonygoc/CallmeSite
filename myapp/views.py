from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import UsuarioForm, AdminRegistrationForm, AdminLoginForm
from .models import Usuario, Administrador

def home(request):
    return render(request, 'home.html')

def registro_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save()
                messages.success(request, f'Cadastro realizado com sucesso! Usuário {usuario.nome} foi registrado.')
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

def admin_registro(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            nome_completo = form.cleaned_data['nome_completo']
            
            # Criar usuário do Django
            user = User.objects.create_user(username=email, email=email, password=password)
            
            # Criar perfil de administrador
            admin = Administrador.objects.create(user=user, nome_completo=nome_completo)
            
            # Fazer login
            login(request, user)
            messages.success(request, 'Conta de administrador criada com sucesso!')
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin/registro.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None and Administrador.objects.filter(user=user).exists():
                login(request, user)
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Email ou senha inválidos.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin/login.html', {'form': form})

@login_required
def admin_dashboard(request):
    if not Administrador.objects.filter(user=request.user).exists():
        messages.error(request, 'Acesso negado. Você precisa ser um administrador.')
        return redirect('login')
    
    usuarios = Usuario.objects.all().order_by('-data_cadastro')
    admin = Administrador.objects.get(user=request.user)
    return render(request, 'admin/dashboard.html', {
        'usuarios': usuarios,
        'admin': admin
    })

@login_required
def usuario_editar(request, pk):
    if not Administrador.objects.filter(user=request.user).exists():
        messages.error(request, 'Acesso negado. Você precisa ser um administrador.')
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('admin_dashboard')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'admin/usuario_editar.html', {'form': form, 'usuario': usuario})

@login_required
@require_POST
def usuario_deletar(request, pk):
    if not Administrador.objects.filter(user=request.user).exists():
        messages.error(request, 'Acesso negado. Você precisa ser um administrador.')
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('admin_dashboard')
