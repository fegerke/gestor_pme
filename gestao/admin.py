from django.contrib import admin
from .models import Cliente, TabelaDePreco # 1. Importa nossos modelos

# 2. Registra os modelos para que apareçam no admin
admin.site.register(Cliente)
admin.site.register(TabelaDePreco)