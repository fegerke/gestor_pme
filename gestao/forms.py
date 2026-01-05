from django import forms
from django.forms import inlineformset_factory
from .models import Pedido, ItemPedido, Item

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente', 'tabela_de_preco', 'data_entrega', 
            'forma_pagamento', 'tipo_desconto', 'valor_desconto', 
            'taxa_entrega', 'observacoes', 'pago', 'status'
        ]
        widgets = {
            # --- A CORREÇÃO ESTÁ AQUI EMBAIXO ---
            # O format='%Y-%m-%d' força o Django a enviar o valor que o input type="date" entende.
            'data_entrega': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            # ------------------------------------
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'tabela_de_preco': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tipo_desconto': forms.Select(attrs={'class': 'form-select'}),
            'valor_desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_entrega': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['item', 'quantidade', 'preco_unitario']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-selector'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control qtd-input', 'step': '0.001'}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas itens vendáveis
        self.fields['item'].queryset = Item.objects.filter(pode_ser_vendido=True).order_by('nome')

# --- O FORMSET (A Mágica dos Itens) ---
# Isso cria um gerenciador para múltiplos itens ligados a um pedido
ItemPedidoFormSet = inlineformset_factory(
    Pedido, 
    ItemPedido, 
    form=ItemPedidoForm,
    extra=1,            # Começa com 1 linha vazia
    can_delete=True     # Permite deletar linhas
)