"""
Configuração Django — GabTech (multi-tenant via schemas PostgreSQL).
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-only-change-before-production',
)

DEBUG = _env_bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]


# ---------------------------------------------------------------------------
# django-tenants: apps compartilhados (schema public) vs por tenant
# ---------------------------------------------------------------------------

SHARED_APPS = [
    'django_tenants',
    'corsheaders',
    'core',
    'plataforma',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'rest_framework_simplejwt',
]

TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'usuarios',
    'crm',
    'atendimentos',
    'agenda',
    'documentos',
    'cerimonial',
    'analytics',
    'servicos',
    'auditoria',
]

INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

TENANT_MODEL = 'core.Gabinete'
TENANT_DOMAIN_MODEL = 'core.Dominio'

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
PUBLIC_SCHEMA_URLCONF = 'config.urls_public'

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Banco de dados (PostgreSQL + backend django-tenants)
# ---------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.environ.get('POSTGRES_DB', 'gabtech'),
        'USER': os.environ.get('POSTGRES_USER', 'gabtech'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'gabtech'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)


# ---------------------------------------------------------------------------
# Autenticação (User por tenant + JWT)
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = 'usuarios.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# ---------------------------------------------------------------------------
# i18n / arquivos estáticos
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Desenvolvimento: responde no schema public se o host não casar com nenhum domínio
SHOW_PUBLIC_IF_NO_TENANT_FOUND = _env_bool('SHOW_PUBLIC_IF_NO_TENANT_FOUND', default=True)

# ---------------------------------------------------------------------------
# CORS (frontend Vite em localhost:5173)
# ---------------------------------------------------------------------------

_default_cors_origins = (
    'http://localhost:5173,http://127.0.0.1:5173,'
    'http://localhost:5174,http://127.0.0.1:5174,'
    'http://demo.localhost:5173,http://demo.localhost:5174'
)
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CORS_ALLOWED_ORIGINS', _default_cors_origins).split(',')
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = _env_bool('CORS_ALLOW_CREDENTIALS', default=False)

CORS_ALLOWED_ORIGIN_REGEXES = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGIN_REGEXES',
        r'^http://[\w-]+\.localhost:\d+$',
    ).split(',')
    if origin.strip()
]

# ---------------------------------------------------------------------------
# Self-service (cadastro de gabinetes — schema public)
# ---------------------------------------------------------------------------

GABTECH_SIGNUP_ENABLED = _env_bool('GABTECH_SIGNUP_ENABLED', default=True)
GABTECH_SIGNUP_CODIGO_CONVITE = os.environ.get('GABTECH_SIGNUP_CODIGO_CONVITE', '').strip()
GABTECH_SIGNUP_RATE_LIMIT = int(os.environ.get('GABTECH_SIGNUP_RATE_LIMIT', '5'))
GABTECH_SIGNUP_RATE_WINDOW_SECONDS = int(os.environ.get('GABTECH_SIGNUP_RATE_WINDOW_SECONDS', '3600'))

GABTECH_TENANT_DOMAIN_SUFFIX = os.environ.get('GABTECH_TENANT_DOMAIN_SUFFIX', 'localhost')
GABTECH_TENANT_URL_SCHEME = os.environ.get('GABTECH_TENANT_URL_SCHEME', 'http')
GABTECH_TENANT_API_PORT = os.environ.get('GABTECH_TENANT_API_PORT', '8800')
GABTECH_TENANT_APP_PORT = os.environ.get('GABTECH_TENANT_APP_PORT', '5174')

GABTECH_SLUGS_RESERVADOS = frozenset(
    s.strip().lower()
    for s in os.environ.get(
        'GABTECH_SLUGS_RESERVADOS',
        'www,api,app,admin,public,demo,static,media,health',
    ).split(',')
    if s.strip()
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
