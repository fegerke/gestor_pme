from django.urls import path
from . import views

app_name = 'gestao'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('api/alterar-status/<int:pedido_id>/', views.alterar_status_pedido, name='alterar_status_pedido'),
    path('api/alterar-data/<int:pedido_id>/', views.alterar_data_entrega, name='alterar_data_entrega'),
    path('api/toggle-pago/<int:pedido_id>/', views.toggle_pago_pedido, name='toggle_pago_pedido'),
    path('pedidos/acao-em-massa/', views.acao_em_massa, name='acao_em_massa'),
    path('teste/', views.home, name='home'),
    path('api/get-item-price/', views.get_item_price, name='get_item_price'),
    path('pedido/<int:pedido_id>/gerar-pix/', views.gerar_pix_pedido, name='gerar_pix_pedido'),
    path('pedido/<int:pedido_id>/imprimir/', views.imprimir_pedido_pdf, name='imprimir_pedido_pdf'),
    path('pedido/<int:pedido_id>/clonar/', views.clonar_pedido, name='clonar_pedido'),
    path('relatorios/vendas/', views.relatorio_vendas_periodo, name='relatorio_vendas_periodo'),
    path('pedidos/novo/', views.pedido_novo, name='pedido_novo'),
    path('pedidos/editar/<int:pedido_id>/', views.pedido_editar, name='pedido_editar'),
    path('api/get-item-price/', views.get_item_price, name='get_item_price'),
]