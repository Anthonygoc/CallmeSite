from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings # Importe 'settings'
import mercadopago
from django.http import JsonResponse, HttpResponse # Importe JsonResponse e HttpResponse
import json

from .forms import (
    ClienteRegistroForm, ClienteLoginForm, UsuarioForm,
    AdminRegistrationForm, AdminLoginForm
)
from .models import Usuario, Administrador, Produto, Pedido, ItemPedido


# --- VIEWS FOR SITE CLIENTS ---

def home(request):
    produtos = Produto.objects.filter(disponivel=True)
    return render(request, 'home.html', {'produtos': produtos})


def registro_usuario(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('home')
    else:
        form = ClienteRegistroForm()
    return render(request, 'registro.html', {'form': form})


def login_usuario(request):
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
                messages.error(request, 'Invalid username or password.')
    else:
        form = ClienteLoginForm()
    return render(request, 'login.html', {'form': form})


def logout_usuario(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def carrinho(request):
    carrinho_session = request.session.get('carrinho', {})
    total_carrinho = sum(float(item['preco']) * item['quantidade'] for item in carrinho_session.values())

    # This loop is to calculate subtotal for each item, needed by the template
    for item in carrinho_session.values():
        item['subtotal'] = float(item['preco']) * item['quantidade']

    context = {'carrinho': carrinho_session, 'total_carrinho': total_carrinho}
    return render(request, 'carrinho.html', context)


@login_required
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho_session = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    if produto_id_str in carrinho_session:
        carrinho_session[produto_id_str]['quantidade'] += 1
    else:
        carrinho_session[produto_id_str] = {
            'quantidade': 1, 'preco': str(produto.preco),
            'nome': produto.nome, 'imagem_url': produto.imagem.url if produto.imagem else ''
        }
    request.session['carrinho'] = carrinho_session
    messages.success(request, f'"{produto.nome}" has been added to your cart!')
    return redirect('carrinho')


@login_required
def checkout(request):
    carrinho_session = request.session.get('carrinho', {})
    if not carrinho_session:
        messages.info(request, "Your cart is empty.")
        return redirect('home')
    total_carrinho = sum(float(item['preco']) * item['quantidade'] for item in carrinho_session.values())

    for item in carrinho_session.values():
        item['subtotal'] = float(item['preco']) * item['quantidade']

    context = {'carrinho': carrinho_session, 'total_carrinho': total_carrinho}
    return render(request, 'checkout.html', context)


@login_required
def processar_pagamento(request):
    carrinho_session = request.session.get('carrinho', {})
    if not carrinho_session:
        return redirect('home')

    try:
        with transaction.atomic():
            # 1. Cria o Pedido com status inicial
            valor_total_pedido = sum(float(item['preco']) * item['quantidade'] for item in carrinho_session.values())
            pedido = Pedido.objects.create(usuario=request.user, valor_total=valor_total_pedido, status='em_revisao')

            # 2. Salva os itens do pedido
            itens_para_salvar = [
                ItemPedido(pedido=pedido, produto_id=produto_id, quantidade=item_data['quantidade'],
                           preco_unitario=float(item_data['preco']),
                           subtotal=float(item_data['preco']) * item_data['quantidade'])
                for produto_id, item_data in carrinho_session.items()
            ]
            ItemPedido.objects.bulk_create(itens_para_salvar)

        # 3. Cria o pagamento PIX no Mercado Pago
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        payment_data = {
            "transaction_amount": float(pedido.valor_total),
            "description": f"Pedido #{pedido.id} da loja CallMeSite",
            "payment_method_id": "pix",
            "payer": {"email": request.user.email}
        }

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        # 4. Guarda o ID do pagamento no nosso Pedido e limpa o carrinho
        pedido.pagamento_id = payment.get('id')
        pedido.save()
        del request.session['carrinho']

        # 5. Prepara os dados para a página de pagamento
        context = {
            'pedido': pedido,
            'pix_qr_code_base64': payment['point_of_interaction']['transaction_data']['qr_code_base64'],
            'pix_qr_code_text': payment['point_of_interaction']['transaction_data']['qr_code']
        }
        return render(request, 'pagamento_pix.html', context)

    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao processar seu pedido: {e}")
        return redirect('checkout')


# --- VIEWS FOR ADMINISTRATION PANEL ---

# THE MISSING FUNCTION IS ADDED BELOW
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
            messages.success(request, 'Administrator account created successfully!')
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin/registro.html', {'form': form})


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'administrador'):
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access permitted for administrators only.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin/login.html', {'form': form})


@login_required
def admin_dashboard(request):
    if not hasattr(request.user, 'administrador'):
        messages.error(request, 'Access Denied.')
        return redirect('home')
    usuarios = Usuario.objects.all().order_by('-data_cadastro')
    admin = request.user.administrador
    return render(request, 'admin/dashboard.html', {'usuarios': usuarios, 'admin': admin})


@login_required
def usuario_editar(request, pk):
    if not hasattr(request.user, 'administrador'):
        messages.error(request, 'Access Denied.')
        return redirect('home')
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'admin/usuario_editar.html', {'form': form, 'usuario': usuario})


@login_required
@require_POST
def usuario_deletar(request, pk):
    if not hasattr(request.user, 'administrador'):
        messages.error(request, 'Access Denied.')
        return redirect('home')
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('admin_dashboard')


@csrf_exempt
def webhook_mercado_pago(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get("type") == "payment":
            payment_id = data["data"]["id"]

            print(f"Webhook recebido para o pagamento: {payment_id}")

            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info.get("response")

            if payment:
                status = payment.get("status")

                try:
                    pedido = Pedido.objects.get(pagamento_id=str(payment_id))

                    if status == "approved" and pedido.status == "em_revisao":
                        print(f"Status do pagamento APROVADO. Atualizando pedido #{pedido.id}...")

                        # --- CAPTURANDO E SALVANDO OS NOVOS DETALHES ---
                        pedido.status = "pago"

                        # Captura a data de aprovação e converte para um formato que o Django entende
                        data_aprovacao_str = payment.get("date_approved")
                        if data_aprovacao_str:
                            pedido.data_pagamento = parse_datetime(data_aprovacao_str)

                        pedido.metodo_pagamento = payment.get("payment_method_id")

                        pedido.save()

                        # Lógica de envio de e-mail de confirmação (já existente)
                        # ...

                except Pedido.DoesNotExist:
                    print(f"Pedido com pagamento_id {payment_id} não encontrado.")
                    pass

    return HttpResponse(status=200)
@login_required
def verificar_status_pedido(request, pedido_id):
    """
    Uma view de API que retorna o status de um pedido em formato JSON.
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
        return JsonResponse({'status': pedido.status, 'status_display': pedido.get_status_display()})
    except Pedido.DoesNotExist:
        return JsonResponse({'status': 'nao_encontrado'}, status=404)

@login_required
def pagamento_sucesso(request):
    pedido_id = request.GET.get('pedido_id')
    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
        context = {'pedido': pedido}
        return render(request, 'pagamento_sucesso.html', context)
    except Pedido.DoesNotExist:
        messages.error(request, "Pedido não encontrado.")
        return redirect('home')

@login_required
def meus_pedidos(request):
        """
        Busca e exibe todos os pedidos feitos pelo usuário logado.
        """
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
        context = {
            'pedidos': pedidos
        }
        return render(request, 'meus_pedidos.html', context)


@login_required
def regerar_pagamento(request, pedido_id):
    """
    Pega um pedido existente que está 'em_revisao' e gera um novo
    pagamento PIX para ele.
    """
    # Garante que o usuário só possa pagar pelo seu próprio pedido
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # Se o pedido já foi pago ou cancelado, não permite gerar novo pagamento
    if pedido.status != 'em_revisao':
        messages.error(request, "Este pedido não está mais aguardando pagamento.")
        return redirect('meus_pedidos')

    try:
        # Gera um novo pagamento PIX para o pedido existente
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        payment_data = {
            "transaction_amount": float(pedido.valor_total),
            "description": f"Pagamento para o Pedido #{pedido.id} da loja CallMeSite",
            "payment_method_id": "pix",
            "payer": {"email": request.user.email}
        }

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response.get("response")

        if not payment:
            error_message = payment_response.get('message', 'Erro desconhecido na API do Mercado Pago.')
            messages.error(request, f"Erro ao gerar pagamento: {error_message}")
            return redirect('meus_pedidos')

        # Atualiza o pedido com o NOVO ID de pagamento
        pedido.pagamento_id = payment.get('id')
        pedido.save()

        # Reutiliza a mesma página de pagamento PIX
        context = {
            'pedido': pedido,
            'pix_qr_code_base64': payment['point_of_interaction']['transaction_data']['qr_code_base64'],
            'pix_qr_code_text': payment['point_of_interaction']['transaction_data']['qr_code']
        }
        return render(request, 'pagamento_pix.html', context)

    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao tentar gerar o pagamento: {e}")
        return redirect('meus_pedidos')


@login_required
def detalhes_pedido(request, pedido_id):
    """
    Busca e exibe os detalhes de um único pedido específico do usuário logado.
    """
    # get_object_or_404 garante que o usuário só possa ver seus próprios pedidos
    # e que o pedido exista, evitando erros.
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    context = {
        'pedido': pedido
    }
    return render(request, 'detalhes_pedido.html', context)