import os
import dj_database_url
from pathlib import Path

# --- CAMINHOS DO PROJETO ---
# Como o arquivo está em config/settings.py, voltar 2 níveis (parent.parent) leva à raiz GESTOR_PME
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURANÇA ---
SECRET_KEY = 'django-insecure-=_2+1d(f_lmq(6nn&s3=o4at#pm!&fhe$*j-%78+w3%@5=a-x-'

# DEBUG INTELIGENTE:
# Se a variável RENDER não existir (seu PC), DEBUG = True.
# Se a variável RENDER existir (Nuvem), DEBUG = False.
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*']

# --- APLICATIVOS INSTALADOS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Seu App Principal
    'gestao',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- OBRIGATÓRIO: WhiteNoise (CSS na Nuvem)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- ROTEAMENTO (Baseado na pasta 'config') ---
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Aponta para a pasta 'templates' que aparece na raiz do seu print
        'APP_DIRS': True,                 # Aponta para 'gestao/templates' automaticamente
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# --- BANCO DE DADOS (Configuração Local / Desenvolvimento) ---
# O Render VAI IGNORAR isso e usar a configuração lá do final do arquivo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gestor_db', 
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# --- VALIDAÇÃO DE SENHA ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS ---
STATIC_URL = 'static/'

# Onde o Render vai JUNTAR tudo (admin + seus arquivos)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Armazenamento padrão (Local)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Mídia (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- LOGIN E REDIRECIONAMENTOS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/gestao/' # Manda pro Dashboard novo após login


# ==============================================================================
#  CONFIGURAÇÕES DE PRODUÇÃO (RENDER)
#  Este bloco sobrescreve as configurações acima APENAS quando estiver na nuvem.
# ==============================================================================

if 'RENDER' in os.environ:
    # 1. Debug desligado (Segurança)
    DEBUG = False
    
    # 2. Permite o domínio do Render
    ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME')]

    # 3. Banco de Dados: Usa o PostgreSQL interno do Render automaticamente
    # (Não precisa colar a URL aqui, ele pega sozinho da variável de ambiente)
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }

    # 4. Arquivos Estáticos: Usa WhiteNoise com compressão (Vital para o CSS funcionar)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # 5. Segurança HTTPS (Força cadeado seguro)
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True