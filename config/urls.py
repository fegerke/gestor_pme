# config/urls.py
from django.contrib import admin
from django.urls import path, include
# --- NOVAS LINHAS DE IMPORTAÇÃO ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gestao/', include('gestao.urls', namespace='gestao')),
]

# --- ADICIONE ESTA LINHA NO FINAL ---
# Isso só funciona em modo de desenvolvimento (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)