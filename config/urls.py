from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Funçãozinha rápida para redirecionar a raiz
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('gestao:dashboard') # Manda pro Dashboard novo
    else:
        return redirect('admin:login') # Ou manda pro Login

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Suas URLs do app gestao
    path('gestao/', include('gestao.urls')), 
    
    # A Rota Raiz (Quando acessa o site puro)
    path('', home_redirect, name='home'),
]