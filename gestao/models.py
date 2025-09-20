from django.db import models

# --- MODELOS DE ORGANIZAÇÃO E PRECIFICAÇÃO ---

class Grupo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Grupo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    def __str__(self):
        return self.nome

class TabelaDePreco(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Tamanho(models.Model):
    descricao = models.CharField(max_length=50, unique=True, help_text="Ex: 140g, 300g, Pequena, Média")

    def __str__(self):
        return self.descricao

# --- MODELO PRINCIPAL DE ITENS VENDÁVEIS ---

class Item(models.Model):
    TIPO_CHOICES = [
        ('P', 'Produto'),
        ('S', 'Serviço'),
    ]

    nome = models.CharField(max_length=200, unique=True)
    tipo_item = models.CharField(max_length=1, choices=TIPO_CHOICES, default='P', verbose_name="Tipo do Item")
    grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True)
    tamanho = models.ForeignKey(Tamanho, on_delete=models.SET_NULL, null=True, blank=True)
    pode_ser_vendido = models.BooleanField(default=True)
    pode_ser_comprado = models.BooleanField(default=False)
    controla_estoque = models.BooleanField(default=True)
    codigo_sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código (SKU)")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço de Custo")
    estoque_atual = models.DecimalField(max_digits=10, decimal_places=3, default=0, null=True, blank=True, verbose_name="Estoque Atual")
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=3, default=0, null=True, blank=True, verbose_name="Estoque Mínimo")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nome

# --- MODELOS DE LIGAÇÃO DE PREÇOS (O SISTEMA HÍBRIDO) ---

class RegraDePreco(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.CASCADE)
    tamanho = models.ForeignKey(Tamanho, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de Venda")

    class Meta:
        unique_together = ('grupo', 'tabela_de_preco', 'tamanho')

    def __str__(self):
        return f"Preço para {self.grupo.nome} ({self.tamanho.descricao}) na tabela {self.tabela_de_preco.nome}"

class PrecoItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="precos_especificos")
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor de Venda (Específico)")

    class Meta:
        unique_together = ('item', 'tabela_de_preco')

    def __str__(self):
        return f"{self.item.nome} - {self.tabela_de_preco.nome}: R$ {self.valor}"

# --- MODELO DE CONTATOS (CLIENTES E FORNECEDORES) ---

class Contato(models.Model):
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
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
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
    
    def __str__(self):
        return self.nome_razao_social
    
    class Meta:
        verbose_name = "Cliente / Fornecedor"
        verbose_name_plural = "Clientes & Fornecedores"

# --- NOVOS MODELOS: PEDIDO E ITEMPEDIDO ---

class Pedido(models.Model):
    # ... (os CHOICES continuam os mesmos) ...
    STATUS_CHOICES = [('ORC', 'Orçamento'),('CNF', 'Confirmado'),('FAT', 'Faturado'),('CAN', 'Cancelado'),]
    FORMA_PAGAMENTO_CHOICES = [('PIX', 'PIX'),('CAR', 'Cartão de Crédito/Débito'),('DIN', 'Dinheiro'),('OUT', 'Outro'),]

    numero_pedido = models.PositiveIntegerField(unique=True, verbose_name="Número do Pedido", blank=True, null=True)
    cliente = models.ForeignKey(Contato, on_delete=models.PROTECT, limit_choices_to={'eh_cliente': True})
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='ORC')
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.PROTECT)
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Emissão")
    data_entrega = models.DateField(null=True, blank=True, verbose_name="Data de Entrega")
    forma_pagamento = models.CharField(max_length=3, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True, null=True)
    pago = models.BooleanField(default=False, verbose_name="Pedido Pago?")

    def __str__(self):
        return f"Pedido Nº {self.numero_pedido} - {self.cliente.nome_razao_social}"

    def save(self, *args, **kwargs):
        # Lógica para gerar o número do pedido automaticamente
        if not self.numero_pedido:
            ultimo_pedido = Pedido.objects.all().order_by('numero_pedido').last()
            if ultimo_pedido:
                self.numero_pedido = ultimo_pedido.numero_pedido + 1
            else:
                self.numero_pedido = 1 # Ou um número inicial que definirmos, ex: 1000

        # Lógica para recalcular o total (chamada pelo SINAL)
        # Usamos self.pk para garantir que o cálculo só ocorra em um pedido já existente
        if self.pk:
            total = sum(item.subtotal for item in self.itens.all())
            self.valor_total = total

        super().save(*args, **kwargs)


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, limit_choices_to={'pode_ser_vendido': True})
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.nome} (x{self.quantidade})"

    # --- NOSSA NOVA LÓGICA DE CÁLCULO ---
    def save(self, *args, **kwargs):
        # Este método é chamado toda vez que um Item de Pedido é salvo.
        # Nós calculamos o subtotal antes de salvar.
        self.subtotal = self.quantidade * self.preco_unitario
        # Chamamos o método 'save' original para de fato salvar no banco.
        super().save(*args, **kwargs)