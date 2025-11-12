# Arquivo: gestao/urls.py (Com URL clonar_pedido)

from django.urls import path
from . import views

app_name = 'gestao'

urlpatterns = [
    path('api/get-item-price/', views.get_item_price, name='get_item_price'),
    path('pedido/<int:pedido_id>/gerar-pix/', views.gerar_pix_pedido, name='gerar_pix_pedido'),
    path('pedido/<int:pedido_id>/imprimir/', views.imprimir_pedido_pdf, name='imprimir_pedido_pdf'),
    path('pedido/<int:pedido_id>/clonar/', views.clonar_pedido, name='clonar_pedido'),
    path('relatorios/vendas/', views.relatorio_vendas_periodo, name='relatorio_vendas_periodo')
]