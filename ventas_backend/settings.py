"""
Django settings for ventas_backend project.
Minimal version: Token auth + CORS (no JWT, no CSRF, no sessions for API)
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Local
    'core',  # ← tu app principal (ajusta si se llama distinto)
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 👈 primero
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ⚠️ CSRF desactivado para APIs (no lo usaremos en /api/)
    'django.middleware.csrf.CsrfViewMiddleware',  # sigue estando, pero no afecta a DRF si no se usa SessionAuth
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ventas_backend.urls'
WSGI_APPLICATION = 'ventas_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ventas',
        'USER': 'postgres',
        'PASSWORD': 'Dragonxt1',  # ⚠️ cámbiala
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # puedes añadir rutas si usas templates propios
        'APP_DIRS': True,  # ← esto es clave para que el admin funcione
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------- REST Framework: Token Auth (sin JWT, sin CSRF) ----------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # ⚠️ No incluimos SessionAuthentication → evita CSRF y cookies
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ---------- CORS ----------
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",   # VS Code Live Server
    "http://localhost:5500",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]



# 👇 IMPORTANTE: Define tu modelo personalizado como usuario por defecto
AUTH_USER_MODEL = 'core.User'