# Chat IA Assistente (Sophie) - Deployment Guide

Este documento fornece instruções completas para implantação do sistema de Chat IA Assistente (Sophie) em ambiente de produção.

## Índice

1. [Requisitos do Sistema](#requisitos-do-sistema)
2. [Configuração do Redis](#configuração-do-redis)
3. [Configuração da API OpenAI](#configuração-da-api-openai)
4. [Variáveis de Ambiente](#variáveis-de-ambiente)
5. [Configuração do Django](#configuração-do-django)
6. [Deployment com Daphne](#deployment-com-daphne)
7. [Monitoramento e Logs](#monitoramento-e-logs)
8. [Troubleshooting](#troubleshooting)

---

## Requisitos do Sistema

### Software Necessário

- **Python**: 3.10 ou superior
- **Django**: 4.x
- **Django Channels**: 4.x
- **Redis**: 6.x ou superior
- **Daphne**: 4.x (ASGI server)
- **PostgreSQL**: 13.x ou superior (recomendado para produção)

### Dependências Python

Instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

Principais dependências do chat:
- `channels[daphne]>=4.0.0`
- `channels-redis>=4.0.0`
- `openai>=1.0.0`
- `redis>=4.5.0`

---

## Configuração do Redis

O Redis é essencial para o funcionamento do chat, sendo usado para:
- Channel layers (comunicação WebSocket)
- Cache de respostas
- Rate limiting
- Gerenciamento de sessões ativas

### Instalação do Redis

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows
Baixe e instale o Redis para Windows:
https://github.com/microsoftarchive/redis/releases

Ou use Docker:
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### Configuração do Redis

Edite o arquivo de configuração do Redis (`/etc/redis/redis.conf`):

```conf
# Bind to localhost (ou seu IP específico)
bind 127.0.0.1

# Porta padrão
port 6379

# Senha (recomendado para produção)
requirepass your_secure_password_here

# Persistência de dados
save 900 1
save 300 10
save 60 10000

# Memória máxima (ajuste conforme necessário)
maxmemory 256mb
maxmemory-policy allkeys-lru

# Log
loglevel notice
logfile /var/log/redis/redis-server.log
```

### Teste a Conexão Redis

```bash
redis-cli ping
# Deve retornar: PONG

# Se configurou senha:
redis-cli -a your_secure_password_here ping
```

### Configuração do Redis no Django

No arquivo `settings.py`:

```python
# Redis Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# Channel Layers (para WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT)],
            'password': REDIS_PASSWORD if REDIS_PASSWORD else None,
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'PASSWORD': REDIS_PASSWORD if REDIS_PASSWORD else None,
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'chat',
        'TIMEOUT': 3600,  # 1 hora
    }
}
```

---

## Configuração da API OpenAI

### Obter Chave da API

1. Acesse https://platform.openai.com/
2. Faça login ou crie uma conta
3. Navegue até API Keys
4. Clique em "Create new secret key"
5. Copie e guarde a chave em local seguro

### Configurar Limites e Billing

1. Configure limites de uso em https://platform.openai.com/account/billing/limits
2. Recomendado para produção:
   - Soft limit: $50/mês
   - Hard limit: $100/mês
3. Configure alertas de uso

### Modelos Disponíveis

O sistema suporta os seguintes modelos:
- `gpt-4` (recomendado, mais preciso)
- `gpt-4-turbo` (mais rápido e econômico)
- `gpt-3.5-turbo` (mais econômico, menos preciso)

### Custos Estimados

Baseado em uso médio:
- **gpt-4**: ~$0.03 por 1K tokens (input) + $0.06 por 1K tokens (output)
- **gpt-3.5-turbo**: ~$0.0015 por 1K tokens (input) + $0.002 por 1K tokens (output)

Estimativa para 1000 conversas/mês (média 10 mensagens cada):
- Com gpt-4: ~$150-200/mês
- Com gpt-3.5-turbo: ~$15-20/mês

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
# ============================================================================
# CHAT IA ASSISTENTE - ENVIRONMENT VARIABLES
# ============================================================================

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4  # ou gpt-3.5-turbo para economia
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

# Chat Configuration
CHAT_MAX_HISTORY=50
CHAT_SESSION_TIMEOUT=24  # horas
CHAT_CLEANUP_INTERVAL=6  # horas
CHAT_RATE_LIMIT=10  # mensagens por minuto
CHAT_CACHE_TTL=3600  # segundos (1 hora)
CHAT_CACHE_ENABLED=True
CHAT_MAX_SESSIONS=100
CHAT_TIMEOUT=30  # segundos
CHAT_CONN_TIMEOUT=10  # segundos
CHAT_MAX_RETRIES=3

# Security
CHAT_MAX_MSG_LENGTH=2000
CHAT_MIN_MSG_LENGTH=1
CHAT_MAX_FEEDBACK_LENGTH=1000
CHAT_MAX_CONTEXT_SIZE=10000  # bytes

# Features
CHAT_ANALYTICS=True
CHAT_FALLBACK=True
CHAT_TYPING_INDICATOR=True

# Logging
CHAT_LOG_LEVEL=INFO
CHAT_LOG_MESSAGES=True
CHAT_LOG_AI=True

# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Segurança das Variáveis

**IMPORTANTE**: Nunca commite o arquivo `.env` no Git!

Adicione ao `.gitignore`:
```
.env
.env.local
.env.production
```

---

## Configuração do Django

### Settings para Produção

No arquivo `settings.py` ou `settings_production.py`:

```python
# Chat Configuration
CHAT_CONFIG = {
    # OpenAI API Configuration
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
    'OPENAI_MODEL': os.environ.get('OPENAI_MODEL', 'gpt-4'),
    'OPENAI_TEMPERATURE': float(os.environ.get('OPENAI_TEMPERATURE', '0.7')),
    'OPENAI_MAX_TOKENS': int(os.environ.get('OPENAI_MAX_TOKENS', '500')),

    # Session Management
    'MAX_HISTORY_MESSAGES': int(os.environ.get('CHAT_MAX_HISTORY', '50')),
    'SESSION_TIMEOUT_HOURS': int(os.environ.get('CHAT_SESSION_TIMEOUT', '24')),
    'SESSION_CLEANUP_INTERVAL_HOURS': int(os.environ.get('CHAT_CLEANUP_INTERVAL', '6')),

    # Rate Limiting
    'RATE_LIMIT_MESSAGES_PER_MINUTE': int(os.environ.get('CHAT_RATE_LIMIT', '10')),
    'RATE_LIMIT_WINDOW_SECONDS': 60,
    'RATE_LIMIT_BURST_ALLOWANCE': 3,

    # Caching
    'CACHE_TTL_SECONDS': int(os.environ.get('CHAT_CACHE_TTL', '3600')),
    'CACHE_ENABLED': os.environ.get('CHAT_CACHE_ENABLED', 'True').lower() == 'true',
    'CACHE_KEY_PREFIX': 'chat_response',

    # Performance
    'MAX_CONCURRENT_SESSIONS': int(os.environ.get('CHAT_MAX_SESSIONS', '100')),
    'RESPONSE_TIMEOUT_SECONDS': int(os.environ.get('CHAT_TIMEOUT', '30')),
    'CONNECTION_TIMEOUT_SECONDS': int(os.environ.get('CHAT_CONN_TIMEOUT', '10')),
    'MAX_RETRIES': int(os.environ.get('CHAT_MAX_RETRIES', '3')),

    # Features
    'ENABLE_ANALYTICS': os.environ.get('CHAT_ANALYTICS', 'True').lower() == 'true',
    'FALLBACK_RESPONSES': os.environ.get('CHAT_FALLBACK', 'True').lower() == 'true',
    'ENABLE_TYPING_INDICATOR': os.environ.get('CHAT_TYPING_INDICATOR', 'True').lower() == 'true',

    # Security
    'MAX_MESSAGE_LENGTH': int(os.environ.get('CHAT_MAX_MSG_LENGTH', '2000')),
    'MIN_MESSAGE_LENGTH': int(os.environ.get('CHAT_MIN_MSG_LENGTH', '1')),
    'MAX_FEEDBACK_LENGTH': int(os.environ.get('CHAT_MAX_FEEDBACK_LENGTH', '1000')),
    'ALLOWED_MESSAGE_TYPES': ['text', 'system'],
    'SANITIZE_INPUT': True,
    'VALIDATE_SESSION': True,
    'VALIDATE_ORIGIN': True,
    'BLOCK_DANGEROUS_PATTERNS': True,
    'HTML_ESCAPE_MESSAGES': True,
    'MAX_CONTEXT_SIZE_BYTES': int(os.environ.get('CHAT_MAX_CONTEXT_SIZE', '10000')),

    # Logging
    'LOG_LEVEL': os.environ.get('CHAT_LOG_LEVEL', 'INFO'),
    'LOG_ALL_MESSAGES': os.environ.get('CHAT_LOG_MESSAGES', 'True').lower() == 'true',
    'LOG_AI_RESPONSES': os.environ.get('CHAT_LOG_AI', 'True').lower() == 'true',
}
```

### Aplicar Migrações

```bash
python manage.py migrate
```

### Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### Popular Base de Conhecimento

```bash
python manage.py populate_knowledge_base
```

---

## Deployment com Daphne

### Instalação do Daphne

```bash
pip install daphne
```

### Configuração do ASGI

Verifique o arquivo `asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from services.chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### Executar Daphne

#### Desenvolvimento
```bash
daphne -b 0.0.0.0 -p 8000 home_services.asgi:application
```

#### Produção com Systemd

Crie o arquivo `/etc/systemd/system/daphne.service`:

```ini
[Unit]
Description=Daphne ASGI Server for Chat IA
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/daphne \
    -b 0.0.0.0 \
    -p 8000 \
    --proxy-headers \
    home_services.asgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ative e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable daphne
sudo systemctl start daphne
sudo systemctl status daphne
```

### Configuração do Nginx

Crie o arquivo `/etc/nginx/sites-available/chat`:

```nginx
upstream daphne {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Static files
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /path/to/your/project/media/;
        expires 7d;
    }

    # WebSocket for chat
    location /ws/chat/ {
        proxy_pass http://daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Regular HTTP requests
    location / {
        proxy_pass http://daphne;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ative o site:

```bash
sudo ln -s /etc/nginx/sites-available/chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Monitoramento e Logs

### Configuração de Logs

No `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/chat.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'services.chat': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Monitorar Logs

```bash
# Logs do Daphne
sudo journalctl -u daphne -f

# Logs do Django
tail -f /var/log/django/chat.log

# Logs do Redis
tail -f /var/log/redis/redis-server.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Métricas Importantes

Monitore as seguintes métricas:

1. **Sessões Ativas**: Número de sessões de chat ativas
2. **Tempo de Resposta**: Tempo médio de resposta da IA
3. **Taxa de Erro**: Porcentagem de erros nas requisições
4. **Uso de Cache**: Taxa de acerto do cache
5. **Uso da API OpenAI**: Tokens consumidos e custos
6. **Conexões WebSocket**: Número de conexões ativas

### Dashboard de Analytics

Acesse o dashboard em:
```
https://yourdomain.com/chat/analytics/
```

---

## Troubleshooting

### Problema: WebSocket não conecta

**Sintomas**: Chat não abre ou mostra erro de conexão

**Soluções**:
1. Verifique se o Daphne está rodando:
   ```bash
   sudo systemctl status daphne
   ```

2. Verifique se o Redis está rodando:
   ```bash
   redis-cli ping
   ```

3. Verifique os logs do Nginx:
   ```bash
   tail -f /var/log/nginx/error.log
   ```

4. Teste a conexão WebSocket:
   ```bash
   wscat -c ws://localhost:8000/ws/chat/
   ```

### Problema: Erro de API OpenAI

**Sintomas**: Mensagens não recebem resposta ou erro "AI unavailable"

**Soluções**:
1. Verifique a chave da API:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Teste a API diretamente:
   ```python
   import openai
   openai.api_key = "your-key"
   response = openai.ChatCompletion.create(
       model="gpt-4",
       messages=[{"role": "user", "content": "Hello"}]
   )
   print(response)
   ```

3. Verifique limites de uso em https://platform.openai.com/account/usage

### Problema: Rate Limiting muito agressivo

**Sintomas**: Usuários recebem erro de "limite de mensagens"

**Soluções**:
1. Ajuste o limite no `.env`:
   ```bash
   CHAT_RATE_LIMIT=20  # Aumentar de 10 para 20
   ```

2. Limpe o cache do Redis:
   ```bash
   redis-cli FLUSHDB
   ```

### Problema: Sessões não persistem

**Sintomas**: Histórico de chat é perdido ao recarregar página

**Soluções**:
1. Verifique se o banco de dados está acessível
2. Verifique as migrações:
   ```bash
   python manage.py showmigrations services
   ```

3. Verifique os logs para erros de banco de dados

### Problema: Alto uso de memória

**Sintomas**: Servidor fica lento ou trava

**Soluções**:
1. Ajuste o limite de sessões:
   ```bash
   CHAT_MAX_SESSIONS=50  # Reduzir de 100
   ```

2. Configure o Redis para usar menos memória:
   ```conf
   maxmemory 128mb
   maxmemory-policy allkeys-lru
   ```

3. Implemente limpeza automática de sessões antigas:
   ```bash
   python manage.py cleanup_old_chat_sessions
   ```

---

## Checklist de Deployment

- [ ] Redis instalado e configurado
- [ ] Chave da API OpenAI configurada
- [ ] Variáveis de ambiente configuradas
- [ ] Migrações aplicadas
- [ ] Arquivos estáticos coletados
- [ ] Base de conhecimento populada
- [ ] Daphne configurado e rodando
- [ ] Nginx configurado com SSL
- [ ] Logs configurados
- [ ] Monitoramento ativo
- [ ] Backup configurado
- [ ] Testes de carga realizados
- [ ] Documentação atualizada

---

## Suporte

Para problemas ou dúvidas:
- Consulte os logs em `/var/log/django/chat.log`
- Verifique o dashboard de analytics
- Contate o time de desenvolvimento

---

**Última atualização**: 2025-11-26
**Versão**: 1.0.0
