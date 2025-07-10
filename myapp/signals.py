from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Pedido

@receiver(post_save, sender=Pedido)
def enviar_email_status_pedido(sender, instance, created, **kwargs):
    """
    Este "ouvinte" é ativado sempre que um objeto Pedido é salvo.
    """
    pedido = instance

    # Se o pedido está a ser CRIADO e o status é 'em_revisao'
    if created and pedido.status == 'em_revisao':
        try:
            print(f"SINAL: Pedido #{pedido.id} criado. A enviar e-mail de 'Pedido em Revisão'...")
            assunto = f"Recebemos o seu Pedido #{pedido.id}"
            contexto_email = {'pedido': pedido}
            corpo_html = render_to_string('emails/confirmacao_pedido.html', contexto_email)
            corpo_texto = render_to_string('emails/confirmacao_pedido.txt', contexto_email)
            send_mail(
                assunto, corpo_texto, settings.EMAIL_HOST_USER,
                [pedido.usuario.email], html_message=corpo_html
            )
            print(f"SINAL: E-mail de 'Pedido em Revisão' para o pedido #{pedido.id} enviado com sucesso!")
        except Exception as e:
            print(f"!!! SINAL: ERRO AO ENVIAR E-MAIL DE REVISÃO para o pedido #{pedido.id}: {e}")

    # Se o pedido está a ser ATUALIZADO e o status mudou para 'pago'
    elif not created and pedido.status == 'pago':
        try:
            print(f"SINAL: Pedido #{pedido.id} atualizado para PAGO. A enviar e-mail de confirmação...")
            assunto_confirmacao = f"Pagamento Aprovado para o Pedido #{pedido.id}"
            contexto_email_confirmacao = {'pedido': pedido}
            corpo_html_confirmacao = render_to_string('emails/pagamento_confirmado.html', contexto_email_confirmacao)
            corpo_texto_confirmacao = render_to_string('emails/pagamento_confirmado.txt', contexto_email_confirmacao)
            send_mail(
                assunto_confirmacao, corpo_texto_confirmacao, settings.EMAIL_HOST_USER,
                [pedido.usuario.email], html_message=corpo_html_confirmacao
            )
            print(f"SINAL: E-mail de 'Pagamento Confirmado' para o pedido #{pedido.id} enviado com sucesso!")
        except Exception as e:
            print(f"!!! SINAL: ERRO AO ENVIAR E-MAIL DE CONFIRMAÇÃO para o pedido #{pedido.id}: {e}")
