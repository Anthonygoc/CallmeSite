from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout  # Import 'logout'
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Importe os formulários corretos para cada função
from .forms import (
    ClienteRegistroForm,
    ClienteLoginForm,
    UsuarioForm,
    AdminRegistrationForm,
    AdminLoginForm
)
from .models import Usuario, Administrador, Produto


# ===================================================================
# == VIEWS PARA CLIENTES DO SITE (Fluxo Público)
# ===================================================================

def home(request):
    """
    Exibe a página inicial com os produtos disponíveis.
    """
    produtos = Produto.objects.filter(disponivel=True)
    return render(request, 'home.html', {'produtos': produtos})


def registro_usuario(request):
    """
    Registra um novo CLIENTE usando o formulário com senha.
    """
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  # Salva o usuário com senha segura
            login(request, user)  # Loga o usuário automaticamente
            messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a)!')
            return redirect('home')  # Redireciona para a página inicial
        else:
            # Se o formulário for inválido, os erros serão exibidos no template
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ClienteRegistroForm()

    return render(request, 'registro.html', {'form': form})


def login_usuario(request):
    """
    Autentica e loga um CLIENTE existente.
    """
    if request.method == 'POST':
        form = ClienteLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
    else:
        form = ClienteLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_usuario(request):
    """
    Faz o logout do usuário (cliente ou admin) e redireciona para a home.
    """
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')


@login_required
def carrinho(request):
    """
    Exibe os itens do carrinho de compras que estão na sessão.
    """
    carrinho_session = request.session.get('carrinho', {})

    # Adiciona o subtotal para cada item e calcula o total geral
    total_carrinho = 0
    for item in carrinho_session.values():
        item['subtotal'] = float(item['preco']) * item['quantidade']
        total_carrinho += item['subtotal']

    context = {
        'carrinho': carrinho_session,
        'total_carrinho': total_carrinho
    }
    return render(request, 'carrinho.html', context)


@login_required
def adicionar_ao_carrinho(request, produto_id):
    """
    Adiciona um produto ao carrinho de compras armazenado na sessão.
    """
    produto = get_object_or_404(Produto, id=produto_id)
    # Pega o carrinho da sessão atual, ou cria um dicionário vazio se não existir
    carrinho_session = request.session.get('carrinho', {})

    # Converte o ID do produto para string, pois as chaves da sessão devem ser strings
    produto_id_str = str(produto_id)

    # Verifica se o produto já está no carrinho
    if produto_id_str in carrinho_session:
        # Se estiver, incrementa a quantidade
        carrinho_session[produto_id_str]['quantidade'] += 1
    else:
        # Se não estiver, adiciona o produto com quantidade 1
        carrinho_session[produto_id_str] = {
            'quantidade': 1,
            'preco': str(produto.preco),  # Armazena o preço como string
            'nome': produto.nome,
            'imagem_url': produto.imagem.url if produto.imagem else ''
        }

    # Salva o carrinho de volta na sessão
    request.session['carrinho'] = carrinho_session

    messages.success(request, f'"{produto.nome}" foi adicionado ao seu carrinho!')
    return redirect('carrinho')

# ===================================================================
# == VIEWS PARA O PAINEL DE ADMINISTRAÇÃO (Fluxo Interno)
# ===================================================================

def admin_registro(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            nome_completo = form.cleaned_data['nome_completo']
            user = User.objects.create_user(username=email, email=email, password=password, is_staff=True)
            Administrador.objects.create(user=user, nome_completo=nome_completo)
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
            user = form.get_user()
            if Administrador.objects.filter(user=user).exists():
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Acesso permitido apenas para administradores.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin/login.html', {'form': form})


@login_required
def admin_dashboard(request):
    if not hasattr(request.user, 'administrador'):
        messages.error(request, 'Acesso negado. Você precisa ser um administrador.')
        return redirect('home')

    usuarios = Usuario.objects.all().order_by('-data_cadastro')
    admin = request.user.administrador
    return render(request, 'admin/dashboard.html', {'usuarios': usuarios, 'admin': admin})


@login_required
def usuario_editar(request, pk):
    if not hasattr(request.user, 'administrador'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')

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
    if not hasattr(request.user, 'administrador'):
        messages.error(request, 'Acesso negado.')
        return redirect('home')

    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('admin_dashboard')

# myapp/views.py

@login_required
def checkout(request):
    """
    Mostra a página de revisão do pedido antes do pagamento.
    """
    carrinho_session = request.session.get('carrinho', {})
    if not carrinho_session:
        # Se o carrinho estiver vazio, não há o que finalizar. Redireciona para a home.
        messages.info(request, "Seu carrinho está vazio.")
        return redirect('home')

    total_carrinho = 0
    for item in carrinho_session.values():
        item['subtotal'] = float(item['preco']) * item['quantidade']
        total_carrinho += item['subtotal']

    context = {
        'carrinho': carrinho_session,
        'total_carrinho': total_carrinho
    }
    return render(request, 'checkout.html', context)


@login_required
def processar_pagamento(request):
    """
    Processa o pedido, limpa o carrinho e mostra a página de sucesso.
    No futuro, aqui você integraria com um sistema de pagamento real.
    """
    # Lógica para salvar o pedido no banco de dados viria aqui.

    # Limpa o carrinho da sessão
    if 'carrinho' in request.session:
        del request.session['carrinho']

    # Renderiza a página de sucesso
    return render(request, 'pagamento_sucesso.html')