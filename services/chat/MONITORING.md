# Chat IA Assistente (Sophie) - Monitoring and Alerting Guide

Este documento fornece instruções para configurar monitoramento e alertas para o sistema de Chat IA Assistente.

## Índice

1. [Métricas a Monitorar](#métricas-a-monitorar)
2. [Configuração de Logs](#configuração-de-logs)
3. [Dashboard de Analytics](#dashboard-de-analytics)
4. [Alertas Automáticos](#alertas-automáticos)
5. [Ferramentas de Monitoramento](#ferramentas-de-monitoramento)
6. [Troubleshooting](#troubleshooting)

---

## Métricas a Monitorar

### Métricas Críticas (Requirements 7.1, 7.2)

#### 1. Sessões Ativas
- **Descrição**: Número de sessões de chat ativas no momento
- **Threshold**: Alerta se > 90% da capacidade máxima (90 de 100)
- **Frequência**: Tempo real
- **Ação**: Escalar recursos se necessário

#### 2. Tempo de Resposta
- **Descrição**: Tempo médio de resposta da IA
- **Threshold**: 
  - Warning: > 2 segundos (média)
  - Critical: > 5 segundos (média)
- **Frequência**: A cada minuto
- **Ação**: Investigar performance da API OpenAI

#### 3. Taxa de Erro
- **Descrição**: Porcentagem de requisições com erro
- **Threshold**:
  - Warning: > 5%
  - Critical: > 10%
- **Frequência**: A cada 5 minutos
- **Ação**: Verificar logs e status dos serviços

#### 4. Uso da API OpenAI
- **Descrição**: Tokens consumidos e custos
- **Threshold**:
  - Warning: > 80% do limite mensal
  - Critical: > 95% do limite mensal
- **Frequência**: A cada hora
- **Ação**: Revisar uso e ajustar limites

#### 5. Taxa de Acerto do Cache
- **Descrição**: Porcentagem de respostas servidas do cache
- **Threshold**: Warning se < 30%
- **Frequência**: A cada hora
- **Ação**: Revisar estratégia de cache

#### 6. Conexões WebSocket
- **Descrição**: Número de conexões WebSocket ativas
- **Threshold**: Alerta se > 80% da capacidade
- **Frequência**: Tempo real
- **Ação**: Verificar recursos do servidor

### Métricas Secundárias

#### 7. Satisfação do Usuário
- **Descrição**: Média de avaliações (1-5 estrelas)
- **Threshold**: Warning se < 3.5
- **Frequência**: Diária
- **Ação**: Revisar qualidade das respostas

#### 8. Taxa de Escalação
- **Descrição**: Porcentagem de sessões escaladas para humano
- **Threshold**: Warning se > 20%
- **Frequência**: Diária
- **Ação**: Melhorar base de conhecimento

#### 9. Mensagens por Sessão
- **Descrição**: Média de mensagens por sessão
- **Threshold**: Informativo
- **Frequência**: Diária
- **Ação**: Análise de engajamento

#### 10. Taxa de Reconexão
- **Descrição**: Porcentagem de sessões que precisaram reconectar
- **Threshold**: Warning se > 10%
- **Frequência**: A cada hora
- **Ação**: Verificar estabilidade da rede/servidor

---

## Configuração de Logs

### Estrutura de Logs

```python
# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/chat.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/chat_errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'json_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/chat_json.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'services.chat': {
            'handlers': ['console', 'file', 'error_file', 'json_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'services.chat.consumers': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'services.chat.manager': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'services.chat.ai_processor': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Logs Importantes

#### Logs de Conexão
```python
logger.info(
    "WebSocket connection established",
    extra={
        'user_id': user.id,
        'session_id': session_id,
        'channel_name': channel_name
    }
)
```

#### Logs de Mensagem
```python
logger.info(
    "Message processed",
    extra={
        'session_id': session_id,
        'user_id': user.id,
        'processing_time_ms': processing_time,
        'intent': intent,
        'cached': is_cached
    }
)
```

#### Logs de Erro
```python
logger.error(
    "AI processing error",
    extra={
        'session_id': session_id,
        'error_type': type(error).__name__,
        'error_message': str(error)
    },
    exc_info=True
)
```

### Análise de Logs

```bash
# Ver logs em tempo real
tail -f /var/log/django/chat.log

# Filtrar erros
grep ERROR /var/log/django/chat.log

# Contar sessões por hora
grep "Session initialized" /var/log/django/chat.log | awk '{print $2}' | cut -d: -f1 | sort | uniq -c

# Ver tempos de resposta lentos
grep "processing_time_ms" /var/log/django/chat_json.log | jq 'select(.processing_time_ms > 2000)'

# Taxa de erro por hora
grep ERROR /var/log/django/chat.log | awk '{print $2}' | cut -d: -f1 | sort | uniq -c
```

---

## Dashboard de Analytics

### Acessar Dashboard

URL: `https://yourdomain.com/chat/analytics/`

Requer permissões de administrador.

### Métricas Disponíveis

#### Visão Geral
- Total de sessões (hoje, semana, mês)
- Sessões ativas no momento
- Tempo médio de resposta
- Taxa de satisfação
- Taxa de escalação

#### Gráficos
- Sessões por hora (últimas 24h)
- Tempo de resposta ao longo do tempo
- Distribuição de avaliações
- Tópicos mais discutidos
- Taxa de cache hit/miss

#### Tabelas
- Sessões recentes
- Mensagens com erro
- Sessões escaladas
- Top usuários por mensagens

### Exportar Dados

```python
# Via Django Admin
python manage.py export_chat_analytics --start-date 2025-01-01 --end-date 2025-01-31 --format csv

# Via API
curl -H "Authorization: Token your-token" \
     https://yourdomain.com/api/chat/analytics/export/?start_date=2025-01-01&end_date=2025-01-31
```

---

## Alertas Automáticos

### Configuração de Alertas

#### 1. Alerta de Alta Taxa de Erro

```python
# services/chat/monitoring.py

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ChatMonitor:
    @staticmethod
    def check_error_rate():
        """Check error rate and send alert if threshold exceeded"""
        from services.chat_models import ChatAnalytics
        from datetime import datetime, timedelta
        
        # Get sessions from last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_sessions = ChatAnalytics.objects.filter(
            created_at__gte=one_hour_ago
        )
        
        total = recent_sessions.count()
        if total == 0:
            return
        
        # Count sessions with errors (escalated or with issues)
        errors = recent_sessions.filter(escalated_to_human=True).count()
        error_rate = (errors / total) * 100
        
        if error_rate > 10:  # Critical threshold
            ChatMonitor.send_alert(
                subject='[CRITICAL] High Chat Error Rate',
                message=f'Error rate is {error_rate:.1f}% (threshold: 10%)\n'
                       f'Total sessions: {total}\n'
                       f'Sessions with errors: {errors}\n'
                       f'Time period: Last hour',
                level='critical'
            )
        elif error_rate > 5:  # Warning threshold
            ChatMonitor.send_alert(
                subject='[WARNING] Elevated Chat Error Rate',
                message=f'Error rate is {error_rate:.1f}% (threshold: 5%)\n'
                       f'Total sessions: {total}\n'
                       f'Sessions with errors: {errors}\n'
                       f'Time period: Last hour',
                level='warning'
            )
    
    @staticmethod
    def check_response_time():
        """Check average response time and alert if slow"""
        from services.chat_models import ChatAnalytics
        from datetime import datetime, timedelta
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_sessions = ChatAnalytics.objects.filter(
            created_at__gte=one_hour_ago,
            average_response_time_ms__isnull=False
        )
        
        if not recent_sessions.exists():
            return
        
        avg_response_time = recent_sessions.aggregate(
            avg=models.Avg('average_response_time_ms')
        )['avg']
        
        if avg_response_time > 5000:  # Critical: > 5s
            ChatMonitor.send_alert(
                subject='[CRITICAL] Slow Chat Response Time',
                message=f'Average response time is {avg_response_time:.0f}ms (threshold: 5000ms)\n'
                       f'Time period: Last hour',
                level='critical'
            )
        elif avg_response_time > 2000:  # Warning: > 2s
            ChatMonitor.send_alert(
                subject='[WARNING] Elevated Chat Response Time',
                message=f'Average response time is {avg_response_time:.0f}ms (threshold: 2000ms)\n'
                       f'Time period: Last hour',
                level='warning'
            )
    
    @staticmethod
    def check_active_sessions():
        """Check number of active sessions"""
        from services.chat_models import ChatSession
        
        active_count = ChatSession.objects.filter(is_active=True).count()
        max_sessions = settings.CHAT_CONFIG['MAX_CONCURRENT_SESSIONS']
        
        usage_pct = (active_count / max_sessions) * 100
        
        if usage_pct > 90:  # Critical: > 90%
            ChatMonitor.send_alert(
                subject='[CRITICAL] High Chat Session Usage',
                message=f'Active sessions: {active_count}/{max_sessions} ({usage_pct:.1f}%)\n'
                       f'Consider scaling resources',
                level='critical'
            )
        elif usage_pct > 80:  # Warning: > 80%
            ChatMonitor.send_alert(
                subject='[WARNING] Elevated Chat Session Usage',
                message=f'Active sessions: {active_count}/{max_sessions} ({usage_pct:.1f}%)',
                level='warning'
            )
    
    @staticmethod
    def send_alert(subject, message, level='info'):
        """Send alert via email and log"""
        logger.log(
            logging.CRITICAL if level == 'critical' else logging.WARNING,
            f"ALERT: {subject}\n{message}"
        )
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.CHAT_ALERT_EMAILS,
            fail_silently=False,
        )
```

#### 2. Configurar Cron Job

```bash
# /etc/cron.d/chat-monitoring

# Check every 5 minutes
*/5 * * * * www-data cd /path/to/project && /path/to/venv/bin/python manage.py check_chat_health

# Generate daily report
0 9 * * * www-data cd /path/to/project && /path/to/venv/bin/python manage.py generate_chat_report --email
```

#### 3. Management Command

```python
# services/chat/management/commands/check_chat_health.py

from django.core.management.base import BaseCommand
from services.chat.monitoring import ChatMonitor

class Command(BaseCommand):
    help = 'Check chat system health and send alerts if needed'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking chat system health...')
        
        ChatMonitor.check_error_rate()
        ChatMonitor.check_response_time()
        ChatMonitor.check_active_sessions()
        
        self.stdout.write(self.style.SUCCESS('Health check complete'))
```

### Configurar Emails de Alerta

```python
# settings.py

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'alerts@yourdomain.com'

# Alert recipients
CHAT_ALERT_EMAILS = [
    'admin@yourdomain.com',
    'devops@yourdomain.com',
]
```

---

## Ferramentas de Monitoramento

### 1. Prometheus + Grafana

#### Instalar Prometheus

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Configure
cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'chat_metrics'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Run
./prometheus --config.file=prometheus.yml
```

#### Exportar Métricas do Django

```python
# Install django-prometheus
pip install django-prometheus

# settings.py
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# urls.py
urlpatterns = [
    path('', include('django_prometheus.urls')),
    # ... other urls
]
```

#### Métricas Customizadas

```python
# services/chat/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Counters
chat_messages_total = Counter(
    'chat_messages_total',
    'Total number of chat messages',
    ['sender_type', 'user_type']
)

chat_sessions_total = Counter(
    'chat_sessions_total',
    'Total number of chat sessions',
    ['user_type']
)

chat_errors_total = Counter(
    'chat_errors_total',
    'Total number of chat errors',
    ['error_type']
)

# Histograms
chat_response_time = Histogram(
    'chat_response_time_seconds',
    'Chat response time in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Gauges
chat_active_sessions = Gauge(
    'chat_active_sessions',
    'Number of active chat sessions'
)

chat_websocket_connections = Gauge(
    'chat_websocket_connections',
    'Number of active WebSocket connections'
)
```

#### Dashboard Grafana

```json
{
  "dashboard": {
    "title": "Chat IA Assistente Monitoring",
    "panels": [
      {
        "title": "Active Sessions",
        "targets": [
          {
            "expr": "chat_active_sessions"
          }
        ]
      },
      {
        "title": "Response Time (95th percentile)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, chat_response_time_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(chat_errors_total[5m])"
          }
        ]
      },
      {
        "title": "Messages per Second",
        "targets": [
          {
            "expr": "rate(chat_messages_total[1m])"
          }
        ]
      }
    ]
  }
}
```

### 2. Sentry para Error Tracking

```bash
pip install sentry-sdk
```

```python
# settings.py

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment=os.environ.get('ENVIRONMENT', 'production'),
)
```

### 3. New Relic APM

```bash
pip install newrelic
```

```bash
# Run with New Relic
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program daphne home_services.asgi:application
```

---

## Troubleshooting

### Dashboard não carrega

**Sintomas**: Erro 500 ao acessar /chat/analytics/

**Soluções**:
1. Verificar permissões do usuário
2. Verificar logs: `tail -f /var/log/django/chat_errors.log`
3. Verificar conexão com banco de dados

### Alertas não estão sendo enviados

**Sintomas**: Nenhum email de alerta recebido

**Soluções**:
1. Verificar configuração de email no settings.py
2. Testar envio manual:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```
3. Verificar cron job está rodando:
   ```bash
   sudo systemctl status cron
   ```

### Métricas não aparecem no Prometheus

**Sintomas**: Prometheus não coleta métricas

**Soluções**:
1. Verificar endpoint /metrics está acessível
2. Verificar configuração do prometheus.yml
3. Verificar firewall não está bloqueando

---

## Checklist de Monitoramento

- [ ] Logs configurados e rotacionando
- [ ] Dashboard de analytics acessível
- [ ] Alertas de erro configurados
- [ ] Alertas de performance configurados
- [ ] Alertas de capacidade configurados
- [ ] Emails de alerta testados
- [ ] Cron jobs configurados
- [ ] Prometheus instalado (opcional)
- [ ] Grafana configurado (opcional)
- [ ] Sentry configurado (opcional)
- [ ] Documentação atualizada
- [ ] Time treinado em troubleshooting

---

**Última atualização**: 2025-11-26
**Versão**: 1.0.0
