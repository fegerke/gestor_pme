from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ItemPedido

@receiver([post_save, post_delete], sender=ItemPedido)
def atualizar_valor_total_pedido(sender, instance, **kwargs):
    """
    Este sinal é acionado toda vez que um ItemPedido é salvo ou deletado.
    Ele recalcula e salva o valor_total do Pedido pai.
    """
    pedido = instance.pedido
    # Chamamos o método save() do pedido, que agora terá a lógica de recálculo.
    pedido.save()