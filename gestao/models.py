from django.db import models

# Nossa primeira tabela: o catálogo de Tabelas de Preço.
class TabelaDePreco(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# Nossa tabela principal de Clientes - VERSÃO DEFINITIVA 1.0
class Cliente(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('F', 'Física'),
        ('J', 'Jurídica'),
    ]
    SITUACAO_CHOICES = [
        ('Ativo', 'Ativo'),
        ('Inativo', 'Inativo'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]

    # --- Campo Obrigatório ---
    nome_razao_social = models.CharField(max_length=200)

    # --- Campos de Preenchimento Controlado ---
    tipo_pessoa = models.CharField(max_length=1, choices=TIPO_PESSOA_CHOICES, blank=True, null=True)
    situacao = models.CharField(max_length=10, choices=SITUACAO_CHOICES, default='Ativo')

    # --- Dados Pessoais (Opcional) ---
    data_nascimento = models.DateField(blank=True, null=True)
    rede_social = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)

    # --- Campos Opcionais ---
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    telefone_fixo = models.CharField(max_length=20, blank=True, null=True)
    
    # Endereço (TUDO OPCIONAL)
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)

    # Outros
    observacoes = models.TextField(blank=True, null=True)

    # Metadados de Auditoria (gerenciados pelo Django e pelo Banco)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.nome_razao_social