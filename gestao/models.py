# Arquivo: gestao/models.py (Com campo nome_beneficiario_pix)

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import re
from unicodedata import normalize # Importação adicionada para a limpeza do nome PIX

# --- MODELO DA CONTA DO ASSINANTE ---
class Empresa(models.Model):
    TIPO_PESSOA_CHOICES = [('PF', 'Pessoa Física'),('PJ', 'Pessoa Jurídica'),]
    TIPO_CHAVE_PIX_CHOICES = [('CPF', 'CPF'),('CNPJ', 'CNPJ'),('CEL', 'Celular'),('EMAIL', 'E-mail'),('ALE', 'Chave Aleatória'),]
    dono = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empresa')
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, default='PJ', verbose_name="Tipo de Pessoa")
    nome_fantasia = models.CharField(max_length=200, verbose_name="Nome Fantasia / Nome Completo")
    razao_social = models.CharField(max_length=200, blank=True, null=True, verbose_name="Razão Social")
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True, verbose_name="CPF")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, verbose_name="CNPJ")
    inscricao_estadual = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Inscrição Estadual")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    telefone_fixo = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone Fixo")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail Principal")
    site = models.URLField(blank=True, null=True, verbose_name="Website")
    rede_social = models.CharField(max_length=100, blank=True, null=True, verbose_name="Rede Social (Instagram, etc.)")
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    observacoes = models.TextField(blank=True, null=True)
    tipo_chave_pix = models.CharField(max_length=5, choices=TIPO_CHAVE_PIX_CHOICES, blank=True, null=True, verbose_name="Tipo de Chave PIX")
    chave_pix = models.CharField(max_length=200, blank=True, null=True, verbose_name="Chave PIX")
    
    # --- **** NOVO CAMPO ADICIONADO AQUI **** ---
    nome_beneficiario_pix = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name="Nome do Beneficiário (PIX)",
        help_text="Nome exato que aparece ao receber um PIX nesta chave (máx. 25 caracteres)."
    )

    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return self.nome_fantasia
    
    def save(self, *args, **kwargs):
        # Limpeza de campos normais
        if self.telefone_fixo: self.telefone_fixo = re.sub(r'\D', '', self.telefone_fixo)
        if self.celular: self.celular = re.sub(r'\D', '', self.celular)
        if self.cpf: self.cpf = re.sub(r'\D', '', self.cpf)
        if self.cnpj: self.cnpj = re.sub(r'\D', '', self.cnpj)
        if self.uf: self.uf = self.uf.upper()

        # Limpeza da Chave PIX
        if self.chave_pix:
            if self.tipo_chave_pix in ['CPF', 'CNPJ', 'CEL']:
                numeros = re.sub(r'\D', '', self.chave_pix)
                if self.tipo_chave_pix == 'CEL':
                    if len(numeros) == 12 and numeros.startswith('0'):
                        numeros = numeros[1:]
                    if not numeros.startswith('+55'):
                        if len(numeros) == 10 or len(numeros) == 11:
                            self.chave_pix = f"+55{numeros}"
                        else:
                            if len(numeros) == 12 or len(numeros) == 13:
                                self.chave_pix = f"+{numeros}"
                            else:
                                self.chave_pix = numeros
                    else:
                        self.chave_pix = numeros
                else:
                    self.chave_pix = numeros
            elif self.tipo_chave_pix == 'EMAIL':
                self.chave_pix = self.chave_pix.strip().lower()
            elif self.tipo_chave_pix == 'ALE':
                self.chave_pix = self.chave_pix.strip()

        # --- **** LIMPEZA DO NOVO CAMPO **** ---
        if self.nome_beneficiario_pix:
            s = normalize('NFD', self.nome_beneficiario_pix).encode('ascii', 'ignore').decode('utf-8')
            s = re.sub(r'[^A-Z0-9 ]', '', s.upper()) # Permite espaços, remove acentos/especiais
            self.nome_beneficiario_pix = s[:25].strip() # Garante limite de 25
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Minha Empresa"
        verbose_name_plural = "Minhas Empresas"


# --- MODELOS DE ORGANIZAÇÃO E PRECIFICAÇÃO ---
class Grupo(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='grupos')
    nome = models.CharField(max_length=100, verbose_name="Nome do Grupo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    def __str__(self): return self.nome
    class Meta: unique_together = ('empresa', 'nome')

class TabelaDePreco(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='tabelas_de_preco')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.nome
    class Meta: unique_together = ('empresa', 'nome')

class Tamanho(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='tamanhos')
    descricao = models.CharField(max_length=50, help_text="Ex: 140g, 300g, Pequena, Média")
    def __str__(self): return self.descricao
    class Meta: unique_together = ('empresa', 'descricao')

# --- MODELO PRINCIPAL DE ITENS VENDÁVEIS ---
class Item(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='itens')
    TIPO_CHOICES = [('P', 'Produto'),('S', 'Serviço'),]
    nome = models.CharField(max_length=200)
    tipo_item = models.CharField(max_length=1, choices=TIPO_CHOICES, default='P', verbose_name="Tipo do Item")
    grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True)
    tamanho = models.ForeignKey(Tamanho, on_delete=models.SET_NULL, null=True, blank=True)
    pode_ser_vendido = models.BooleanField(default=True)
    pode_ser_comprado = models.BooleanField(default=False)
    controla_estoque = models.BooleanField(default=True)
    codigo_sku = models.CharField(max_length=50, blank=True, null=True, verbose_name="Código (SKU)")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço de Custo")
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=3, default=0, null=True, blank=True, verbose_name="Estoque Atual")
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=3, default=0, null=True, blank=True, verbose_name="Estoque Mínimo")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True)
    def __str__(self): return self.nome
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'nome', 'tamanho'], name='unique_produto_tamanho_empresa', condition=Q(tamanho__isnull=False)),
            models.UniqueConstraint(fields=['empresa', 'nome'], name='unique_servico_sem_tamanho_empresa', condition=Q(tamanho__isnull=True)),
            models.UniqueConstraint(fields=['empresa', 'codigo_sku'], name='unique_sku_empresa', condition=Q(codigo_sku__isnull=False)),
        ]

# --- MODELOS DE LIGAÇÃO DE PREÇOS (O SISTEMA HÍBRIDO) ---
class RegraDePreco(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='regras_de_preco')
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.CASCADE)
    tamanho = models.ForeignKey(Tamanho, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de Venda")
    class Meta: unique_together = ('empresa', 'grupo', 'tabela_de_preco', 'tamanho')
    def __str__(self): return f"Preço para {self.grupo.nome} ({self.tamanho.descricao}) na tabela {self.tabela_de_preco.nome}"

class PrecoItem(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='precos_item')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="precos_especificos")
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de Venda (Específico)")
    class Meta: unique_together = ('empresa', 'item', 'tabela_de_preco')
    def __str__(self): return f"{self.item.nome} - {self.tabela_de_preco.nome}: R$ {self.valor}"

# --- MODELO DE CONTATOS (CLIENTES E FORNECEDORES) ---
class Contato(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contatos')
    TIPO_PESSOA_CHOICES = [('F', 'Física'),('J', 'Jurídica'),]
    SITUACAO_CHOICES = [('Ativo', 'Ativo'),('Inativo', 'Inativo'),]
    GENERO_CHOICES = [('M', 'Masculino'),('F', 'Feminino'),('O', 'Outro'),('N', 'Prefiro não informar'),]
    eh_cliente = models.BooleanField(default=True)
    eh_fornecedor = models.BooleanField(default=False)
    nome_razao_social = models.CharField(max_length=200)
    tipo_pessoa = models.CharField(max_length=1, choices=TIPO_PESSOA_CHOICES, blank=True, null=True)
    situacao = models.CharField(max_length=10, choices=SITUACAO_CHOICES, default='Ativo')
    data_nascimento = models.DateField(blank=True, null=True)
    rede_social = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")
    email = models.EmailField(blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    telefone_fixo = models.CharField(max_length=20, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True)
    def __str__(self): return self.nome_razao_social
    class Meta:
        verbose_name = "Cliente / Fornecedor"
        verbose_name_plural = "Clientes & Fornecedores"
        unique_together = [('empresa', 'cpf'), ('empresa', 'cnpj'), ('empresa', 'inscricao_estadual')]

# --- MODELOS DE PEDIDO DE VENDA ---
class Pedido(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pedidos')
    STATUS_CHOICES = [('A', 'Em Aberto'),('F', 'Atendido'),('C', 'Cancelado'),]
    FORMA_PAGAMENTO_CHOICES = [('PIX', 'PIX'),('CAR', 'Cartão de Crédito/Débito'),('DIN', 'Dinheiro'),('OUT', 'Outro'),]
    TIPO_DESCONTO_CHOICES = [('P', 'Percentual (%)'),('V', 'Valor Fixo (R$)'),]
    numero_pedido = models.PositiveIntegerField(verbose_name="Número do Pedido", blank=True, null=True)
    cliente = models.ForeignKey(Contato, on_delete=models.PROTECT, limit_choices_to={'eh_cliente': True})
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='A')
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.PROTECT)
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Emissão")
    data_entrega = models.DateField(null=True, blank=True, verbose_name="Data de Entrega")
    forma_pagamento = models.CharField(max_length=3, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True)
    tipo_desconto = models.CharField(max_length=1, choices=TIPO_DESCONTO_CHOICES, blank=True, null=True, verbose_name="Tipo de Desconto")
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desconto")
    taxa_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taxa de Entrega")
    subtotal_itens = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal dos Itens")
    desconto_calculado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor do Desconto (R$)")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True, null=True)
    pago = models.BooleanField(default=False, verbose_name="Pedido Pago?")
    def __str__(self): return f"Pedido Nº {self.numero_pedido} - {self.cliente.nome_razao_social}"
    class Meta: unique_together = ('empresa', 'numero_pedido')
    def save(self, *args, **kwargs):
        if not self.numero_pedido and self.empresa:
            ultimo_pedido = Pedido.objects.filter(empresa=self.empresa).order_by('numero_pedido').last()
            if ultimo_pedido and ultimo_pedido.numero_pedido:
                self.numero_pedido = ultimo_pedido.numero_pedido + 1
            else:
                self.numero_pedido = 1
        if self.pk:
            try:
                old_instance = Pedido.objects.get(pk=self.pk)
                if old_instance.status == 'A' and self.status == 'F':
                    self.pago = True
                elif old_instance.status == 'F' and self.status == 'A':
                    self.pago = False
            except Pedido.DoesNotExist:
                pass
        if self.pk:
            self.subtotal_itens = sum(item.subtotal for item in self.itens.all())
            desconto_aplicado = 0
            if self.tipo_desconto and self.valor_desconto > 0:
                if self.tipo_desconto == 'P':
                    desconto_aplicado = (self.subtotal_itens * self.valor_desconto) / 100
                elif self.tipo_desconto == 'V':
                    desconto_aplicado = self.valor_desconto
            self.desconto_calculado = desconto_aplicado
            taxa_entrega = self.taxa_entrega or 0
            self.valor_total = self.subtotal_itens - self.desconto_calculado + taxa_entrega
        super().save(*args, **kwargs)

class ItemPedido(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='itens_pedido')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, limit_choices_to={'pode_ser_vendido': True})
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f"{self.item.nome} (x{self.quantidade})"
    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)