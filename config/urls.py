from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# --- FUNÇÃO DE REDIRECIONAMENTO INTELIGENTE ---
# Essa função é quem decide para onde o usuário vai quando acessa a raiz '/'
def home_redirect(request):
    # Se o cara já logou, joga ele direto pro Dashboard
    if request.user.is_authenticated:
        return redirect('gestao:dashboard')
    # Se não logou, manda fazer login no Admin
    else:
        return redirect('admin:login')

urlpatterns = [
    # Rota do Admin do Django
    path('admin/', admin.site.urls),
    
    # Rotas do seu App (Gestão)
    path('gestao/', include('gestao.urls')),
    
    # Rota Raiz (Vazia) -> Chama a função lá de cima
    path('', home_redirect, name='home'),
]