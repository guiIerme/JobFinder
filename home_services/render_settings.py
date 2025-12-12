# render_settings.py - Configurações específicas para o Render
import os
from .settings import *

# Forçar DEBUG = False em produção
DEBUG = False

# Hosts permitidos
ALLOWED_HOSTS = [
    'jobfinder-b3at.onrender.com',
    'localhost',
    '127.0.0.1',
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://jobfinder-b3at.onrender.com',
]

# Configuração de arquivos estáticos para produção
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuração
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações de segurança para produção
SECURE_SSL_REDIRECT = False  # Render já gerencia HTTPS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}