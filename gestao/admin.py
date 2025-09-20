from django.contrib import admin
from .models import (
    Contato, TabelaDePreco, Item, PrecoItem, 
    Grupo, RegraDePreco, Tamanho, Pedido, ItemPedido
)

# --- INLINES ---
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    autocomplete_fields = ['item']
    can_delete = False 

class PrecoItemInline(admin.TabularInline):
    model = PrecoItem
    extra = 1

# --- ADMINS CUSTOMIZADOS ---
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'codigo_sku')
    list_display = ('nome', 'grupo', 'tamanho', 'tipo_item', 'estoque_atual', 'pode_ser_vendido')
    list_filter = ('tipo_item', 'grupo', 'pode_ser_vendido', 'pode_ser_comprado')
    inlines = [PrecoItemInline]

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    search_fields = ('nome_razao_social', 'cpf', 'cnpj', 'email')
    list_display = ('nome_razao_social', 'email', 'celular', 'situacao', 'eh_cliente', 'eh_fornecedor')
    list_filter = ('situacao', 'tipo_pessoa', 'eh_cliente', 'eh_fornecedor')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'cliente', 'status', 'valor_total', 'data_emissao')
    list_filter = ('status', 'data_emissao', 'cliente')
    autocomplete_fields = ['cliente']
    inlines = [ItemPedidoInline]

    # Deixa o campo 'valor_total' como apenas leitura no formulário
    # readonly_fields = ('valor_total',)

    # NOVA ORDEM DOS CAMPOS E ADIÇÃO DO CAMPO 'pago'
    fieldsets = (
        ('Dados Principais', {
            'fields': ('numero_pedido', 'cliente', 'status', 'tabela_de_preco')
        }),
        ('Entrega & Pagamento', {
            'fields': ('data_entrega', 'forma_pagamento', 'pago') # <-- 'pago' adicionado aqui
        }),
        ('Resumo Financeiro e Observações', {
            'fields': ('valor_total', 'observacoes') # <-- 'valor_total' agora está aqui
        }),
    )

    class Media:
        js = ('gestao/js/pedido_admin.js',)

# --- REGISTRO DOS OUTROS MODELOS ---
admin.site.register(TabelaDePreco)
admin.site.register(Grupo)
admin.site.register(RegraDePreco)
admin.site.register(Tamanho)