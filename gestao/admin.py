from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q, F, Case, When

# Import models
from .models import (
    Contato, TabelaDePreco, Item, PrecoItem,
    Grupo, RegraDePreco, Tamanho, Pedido, ItemPedido, Empresa
)

# --- INLINES ---
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    autocomplete_fields = ['item']
    can_delete = True
    exclude = ('empresa',)

class PrecoItemInline(admin.TabularInline):
    model = PrecoItem
    extra = 1
    # exclude = ('empresa',)

# --- FORMS ---
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = '__all__'
        widgets = {
            'valor_desconto': forms.NumberInput(attrs={'step': '0.01'}),
            'taxa_entrega': forms.NumberInput(attrs={'step': '0.01'}),
        }

# --- ADMINS ---
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'codigo_sku')
    list_display = ('nome', 'grupo', 'tamanho', 'tipo_item', 'estoque_atual', 'pode_ser_vendido')
    list_filter = ('tipo_item', 'grupo', 'pode_ser_vendido', 'pode_ser_comprado')
    inlines = [PrecoItemInline]
    list_editable = ('estoque_atual', 'pode_ser_vendido')
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa:
                obj.empresa = user_empresa
        super().save_model(request, obj, form, change)
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        user_empresa = getattr(request.user, 'empresa', None)
        for obj in instances:
            if isinstance(obj, PrecoItem) and not obj.pk and user_empresa:
                 obj.empresa = user_empresa
            obj.save()
        formset.save_m2m()
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa: return qs.filter(empresa=user_empresa)
        return qs.none()

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    search_fields = ('nome_razao_social', 'apelido', 'cpf', 'cnpj', 'email')
    list_display = ('nome_razao_social', 'apelido', 'email', 'celular', 'situacao', 'eh_cliente', 'eh_fornecedor')
    list_filter = ('situacao', 'tipo_pessoa', 'eh_cliente', 'eh_fornecedor')
    list_editable = ('apelido', 'situacao', 'eh_cliente', 'eh_fornecedor')
    class Media: js = ('gestao/js/jquery.mask.min.js', 'gestao/js/contato_admin.js',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa:
                obj.empresa = user_empresa
        super().save_model(request, obj, form, change)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa: return qs.filter(empresa=user_empresa)
        return qs.none()

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoForm
    save_on_top = True
    
    # --- **** ALTERAÇÃO AQUI: BARRA DE PESQUISA **** ---
    # Permite buscar pelo nome ou apelido do cliente (usando __ para acessar o relacionamento)
    # e também pelo número do pedido.
    search_fields = ('cliente__nome_razao_social', 'cliente__apelido', 'numero_pedido')
    # --- FIM DA ALTERAÇÃO ---

    list_display = (
        'get_numero_pedido',
        'get_data_emissão',
        'get_data_entrega',
        'cliente',
        'valor_total',
        'get_pago',
        'status',
        'gerar_pix_link',
        'imprimir_pedido_link',
        'clonar_pedido_link',
    )

    list_editable = ('status',)
    list_filter = ('status', 'pago', 'data_emissao', 'data_entrega', 'cliente')
    autocomplete_fields = ['cliente']
    inlines = [ItemPedidoInline]
    readonly_fields = ('gerar_pix_button', 'imprimir_pedido_button')
    fieldsets = (
        ('Dados Principais', {'fields': ('numero_pedido', 'cliente', 'status', 'tabela_de_preco')}),
        ('Entrega & Pagamento', {'fields': ('data_entrega', 'forma_pagamento', 'pago')}),
        ('Valores Adicionais', {'fields': (('tipo_desconto', 'valor_desconto'), 'taxa_entrega')}),
        ('Resumo Financeiro e Ações', {'fields': ('valor_total', 'observacoes', 'gerar_pix_button', 'imprimir_pedido_button')}),
    )
    class Media:
        js = ('gestao/js/pedido_admin.js',)

    @admin.display(description="PEDIDO")
    def get_numero_pedido(self, obj): return obj.numero_pedido
    @admin.display(description="PAGO?", boolean=True)
    def get_pago(self, obj): return obj.pago
    @admin.display(description="EMISSÃO")
    def get_data_emissão(self, obj): return obj.data_emissao.strftime('%d/%m/%Y')

    @admin.display(description="DT ENTREGA")
    def get_data_entrega(self, obj):
        if obj.data_entrega:
            return obj.data_entrega.strftime('%d/%m/%Y')
        return "N/A"

    @admin.display(description="PIX")
    def gerar_pix_link(self, obj):
        if obj.forma_pagamento == 'PIX' and not obj.pago and obj.valor_total > 0:
            url = reverse('gestao:gerar_pix_pedido', args=[obj.id])
            icon_url = staticfiles_storage.url('gestao/img/pix.svg')
            return format_html(f'<a href="{url}" target="_blank" title="Gerar PIX"><img src="{icon_url}" alt="PIX" width="16" height="16"></a>')
        return "N/A"

    @admin.display(description="PDF")
    def imprimir_pedido_link(self, obj):
        url = reverse('gestao:imprimir_pedido_pdf', args=[obj.id])
        icon_url = staticfiles_storage.url('gestao/img/pdf.svg')
        return format_html(f'<a href="{url}" target="_blank" title="Gerar PDF"><img src="{icon_url}" alt="PDF" width="16" height="16"></a>')

    @admin.display(description="Clonar")
    def clonar_pedido_link(self, obj):
        url = reverse('gestao:clonar_pedido', args=[obj.id])
        icon_url = staticfiles_storage.url('gestao/img/clonar.svg')
        return format_html(f'<a href="{url}" title="Clonar Pedido"><img src="{icon_url}" alt="Clonar" width="16" height="16"></a>')

    def gerar_pix_button(self, obj):
        if obj.id and obj.forma_pagamento == 'PIX' and not obj.pago and obj.valor_total > 0:
            url = reverse('gestao:gerar_pix_pedido', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank" class="button">Gerar PIX e Copia/Cola</a>')
        return "Não aplicável ou pedido já pago."
    gerar_pix_button.short_description = "Pagamento PIX"

    def imprimir_pedido_button(self, obj):
        if obj.id:
            url = reverse('gestao:imprimir_pedido_pdf', args=[obj.id])
            return format_html(f'<a href="{url}" target="_blank" class="button">Imprimir Pedido</a>')
        return "Salve o pedido para poder imprimir."
    imprimir_pedido_button.short_description = "Ações do Pedido"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa:
                obj.empresa = user_empresa
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        user_empresa = getattr(request.user, 'empresa', None)
        for instance in instances:
            if isinstance(instance, ItemPedido) and not instance.pk and user_empresa:
                instance.empresa = user_empresa
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user_empresa = getattr(request.user, 'empresa', None)
        if not request.user.is_superuser:
            if user_empresa:
                qs = qs.filter(empresa=user_empresa)
            else:
                return qs.none()
        
        ordem_abertos = Case(
            When(status='A', then=F('data_entrega')),
            default=None
        ).asc(nulls_last=True)

        ordem_outros = Case(
            When(status='A', then=None),
            default=F('data_entrega')
        ).desc(nulls_last=True)
        
        qs = qs.order_by(
            'status',
            ordem_abertos,
            ordem_outros,
            '-numero_pedido'
        )
        return qs

    def get_changeform_initial_data(self, request):
        proximo_numero = 1
        tabela_padrao_id = 1
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa:
            ultimo_pedido = Pedido.objects.filter(empresa=user_empresa).order_by('numero_pedido').last()
            if ultimo_pedido and ultimo_pedido.numero_pedido:
                proximo_numero = ultimo_pedido.numero_pedido + 1
        return {
            'numero_pedido': proximo_numero,
            'tabela_de_preco': tabela_padrao_id
        }

# ... (Resto do arquivo admin.py sem alterações: EmpresaAdmin, GrupoAdmin, etc.) ...
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'dono', 'tipo_pessoa', 'cnpj', 'cpf')
    search_fields = ('nome_fantasia', 'cnpj', 'cpf', 'dono__username')
    list_filter = ('tipo_pessoa',)
    fieldsets = (
        ('Informações Principais', {'fields': ('dono', 'logo', 'tipo_pessoa', 'nome_fantasia', 'razao_social')}),
        ('Dados Fiscais', {'fields': ('cpf', 'cnpj', 'inscricao_estadual')}),
        ('Endereço', {'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf')}),
        ('Contato & Redes', {'fields': ('celular', 'telefone_fixo', 'email', 'site', 'rede_social')}),
        ('Dados de Pagamento (PIX)', {'fields': ('tipo_chave_pix', 'chave_pix', 'nome_beneficiario_pix')}),
        ('Outras Informações', {'fields': ('observacoes',)})
    )
    class Media:
        js = ('gestao/js/jquery.mask.min.js', 'gestao/js/empresa_admin.js',)

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa: obj.empresa = user_empresa
        super().save_model(request, obj, form, change)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa: return qs.filter(empresa=user_empresa)
        return qs.none()

@admin.register(Tamanho)
class TamanhoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa: obj.empresa = user_empresa
        super().save_model(request, obj, form, change)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa: return qs.filter(empresa=user_empresa)
        return qs.none()

@admin.register(TabelaDePreco)
class TabelaDePrecoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'data_criacao')
    search_fields = ('nome',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa: obj.empresa = user_empresa
        super().save_model(request, obj, form, change)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa: return qs.filter(empresa=user_empresa)
        return qs.none()

@admin.register(RegraDePreco)
class RegraDePrecoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'valor')
    list_filter = ('grupo', 'tamanho', 'tabela_de_preco')
    search_fields = ('grupo__nome', 'tamanho__descricao', 'tabela_de_preco__nome')
    list_editable = ('valor',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            user_empresa = getattr(request.user, 'empresa', None)
            if user_empresa: obj.empresa = user_empresa
        super().save_model(request, obj, form, change)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        user_empresa = getattr(request.user, 'empresa', None)
        if user_empresa: return qs.filter(empresa=user_empresa)
        return qs.none()