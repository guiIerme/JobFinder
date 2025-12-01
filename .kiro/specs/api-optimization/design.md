# Design Document - API Optimization

## Overview

Este documento descreve o design técnico para implementação de múltiplas APIs RESTful otimizadas que melhorarão significativamente o desempenho, escalabilidade e experiência do usuário da plataforma. O sistema incluirá cache inteligente, paginação eficiente, busca avançada, compressão de dados, rate limiting, processamento em lote, WebSockets para tempo real, e integração com CDN.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web Browser, Mobile App, Third-party Integrations)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  - Rate Limiting                                             │
│  - Authentication/Authorization                              │
│  - Request Routing                                           │
│  - Response Compression                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│   REST   │  │WebSocket │  │  Batch   │
│   APIs   │  │ Service  │  │   API    │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │              │
     └─────────────┼──────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  - Business Logic                                            │
│  - Data Validation                                           │
│  - Cache Management                                          │
│  - Search Engine Integration                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Cache   │  │ Database │  │   CDN    │
│  (Redis) │  │(SQLite)  │  │          │
└──────────┘  └──────────┘  └──────────┘
```

### Technology Stack

- **Framework**: Django 5.2.6 + Django REST Framework
- **Cache**: Django Cache Framework (LocMem para dev, Redis para produção)
- **Rate Limiting**: Django Ratelimit
- **Compression**: Django GZip Middleware + Brotli
- **WebSockets**: Django Channels + Daphne
- **Search**: Django Q objects + PostgreSQL Full-Text Search (futuro)
- **Monitoring**: Django Debug Toolbar + Custom Analytics
- **CDN**: Cloudflare/AWS CloudFront (configuração)

## Components and Interfaces

### 1. Cache Layer

**Componente**: `services/cache_manager.py`

```python
class CacheManager:
    - get_or_set(key, callback, timeout)
    - invalidate(pattern)
    - invalidate_user_cache(user_id)
    - get_cache_key(prefix, *args)
```

**Estratégia de Cache**:
- Cache de listagens: 15 minutos
- Cache de detalhes: 30 minutos
- Cache de usuário: 5 minutos
- Invalidação automática em updates

**Cache Keys Pattern**:
- `services:list:{category}:{page}`
- `service:detail:{id}`
- `professional:list:{filters}:{page}`
- `user:profile:{user_id}`

### 2. Pagination System

**Componente**: `services/pagination.py`

```python
class OptimizedPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })
```

### 3. Search API

**Endpoint**: `/api/v1/search/`

**Componente**: `services/api/search_views.py`

```python
class AdvancedSearchView(APIView):
    def get(self, request):
        # Parâmetros suportados:
        # - q: texto de busca
        # - category: filtro por categoria
        # - min_price, max_price: range de preço
        # - min_rating: avaliação mínima
        # - lat, lng, radius: busca geográfica
        # - sort: ordenação (relevance, price, rating, distance)
        pass
```

**Índices de Busca**:
- Índice em `CustomService.name` e `description`
- Índice em `UserProfile.bio` e `specialties`
- Índice geoespacial em `latitude` e `longitude`

### 4. Rate Limiting

**Componente**: `services/middleware/rate_limit_middleware.py`

```python
class RateLimitMiddleware:
    LIMITS = {
        'anonymous': '100/hour',
        'authenticated': '1000/hour',
        'premium': '5000/hour'
    }
    
    def process_request(self, request):
        # Verifica limite baseado em user/IP
        # Retorna 429 se excedido
        pass
```

**Headers de Resposta**:
- `X-RateLimit-Limit`: limite total
- `X-RateLimit-Remaining`: requisições restantes
- `X-RateLimit-Reset`: timestamp de reset

### 5. Compression Module

**Configuração**: `home_services/settings.py`

```python
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',  # Adicionar no topo
    'services.middleware.BrotliMiddleware',   # Novo middleware
    # ... outros middlewares
]

# Configuração de compressão
GZIP_COMPRESSION_LEVEL = 6
BROTLI_COMPRESSION_LEVEL = 5
MIN_COMPRESSION_SIZE = 1024  # 1KB
```

### 6. Analytics API

**Endpoints**:
- `GET /api/v1/analytics/performance/` - Métricas de performance
- `GET /api/v1/analytics/errors/` - Log de erros
- `GET /api/v1/analytics/endpoints/` - Estatísticas por endpoint

**Componente**: `services/api/analytics_views.py`

```python
class PerformanceMetrics:
    - average_response_time
    - p95_response_time
    - p99_response_time
    - error_rate
    - requests_per_minute
    - slowest_endpoints
```

**Modelo**: `services/models.py`

```python
class APIMetric(models.Model):
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    response_time = models.FloatField()
    status_code = models.IntegerField()
    user = models.ForeignKey(User, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
```

### 7. Batch Processing API

**Endpoint**: `POST /api/v1/batch/`

**Request Format**:
```json
{
  "operations": [
    {
      "method": "POST",
      "url": "/api/v1/orders/",
      "body": {...}
    },
    {
      "method": "PATCH",
      "url": "/api/v1/orders/123/",
      "body": {...}
    }
  ]
}
```

**Response Format**:
```json
{
  "results": [
    {
      "status": 201,
      "data": {...}
    },
    {
      "status": 200,
      "data": {...}
    }
  ]
}
```

### 8. WebSocket Service

**Componente**: `services/consumers.py`

```python
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Autenticação
        # Adicionar ao grupo do usuário
        pass
    
    async def receive(self, text_data):
        # Processar mensagens do cliente
        pass
    
    async def send_notification(self, event):
        # Enviar notificação para cliente
        pass
```

**Routing**: `home_services/routing.py`

```python
websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/chat/<int:chat_id>/', ChatConsumer.as_asgi()),
]
```

### 9. CDN Integration

**Componente**: `services/storage_backends.py`

```python
class CDNStaticStorage(StaticFilesStorage):
    # Configuração para servir estáticos via CDN
    pass

class CDNMediaStorage(FileSystemStorage):
    # Configuração para servir media via CDN
    pass
```

**Settings**:
```python
# CDN Configuration
CDN_ENABLED = True
CDN_URL = 'https://cdn.example.com'
STATIC_URL = CDN_URL + '/static/' if CDN_ENABLED else '/static/'
MEDIA_URL = CDN_URL + '/media/' if CDN_ENABLED else '/media/'
```

### 10. Mobile-Optimized Endpoints

**Endpoints**:
- `/api/v1/mobile/services/` - Listagem compacta
- `/api/v1/mobile/professionals/` - Listagem compacta
- `/api/v1/mobile/orders/` - Pedidos simplificados

**Features**:
- Campos reduzidos por padrão
- Suporte a `?fields=field1,field2` para seleção
- Imagens otimizadas para mobile
- Respostas minificadas com `?compact=true`

### 11. Bulk Admin API

**Endpoints**:
- `POST /api/v1/admin/bulk/orders/update-status/`
- `POST /api/v1/admin/bulk/professionals/approve/`
- `GET /api/v1/admin/export/orders/`
- `GET /api/v1/admin/export/users/`

**Componente**: `services/api/admin_bulk_views.py`

```python
class BulkOrderUpdateView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        # Processar updates em lote
        # Usar Celery para processamento assíncrono
        pass
```

### 12. API Versioning

**URL Structure**:
- `/api/v1/...` - Versão atual
- `/api/v2/...` - Próxima versão (futuro)

**Componente**: `services/api/versioning.py`

```python
class APIVersionMiddleware:
    def process_request(self, request):
        # Extrair versão da URL ou header
        # Rotear para handler correto
        pass
```

## Data Models

### New Models

```python
# services/models.py

class APIMetric(models.Model):
    """Métricas de performance da API"""
    endpoint = models.CharField(max_length=200, db_index=True)
    method = models.CharField(max_length=10)
    response_time = models.FloatField()
    status_code = models.IntegerField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['endpoint', '-timestamp']),
            models.Index(fields=['status_code', '-timestamp']),
        ]

class RateLimitRecord(models.Model):
    """Registro de rate limiting"""
    identifier = models.CharField(max_length=100, db_index=True)  # user_id ou IP
    endpoint = models.CharField(max_length=200)
    request_count = models.IntegerField(default=0)
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    
    class Meta:
        unique_together = ('identifier', 'endpoint', 'window_start')

class BatchOperation(models.Model):
    """Operações em lote"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=50)
    total_operations = models.IntegerField()
    completed_operations = models.IntegerField(default=0)
    failed_operations = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_at": "2025-11-11T15:30:00Z"
    }
  }
}
```

### Error Codes

- `RATE_LIMIT_EXCEEDED` (429)
- `INVALID_PAGINATION` (400)
- `SEARCH_QUERY_TOO_COMPLEX` (400)
- `BATCH_SIZE_EXCEEDED` (400)
- `WEBSOCKET_AUTH_FAILED` (401)
- `CDN_UPLOAD_FAILED` (500)

### Error Handling Strategy

1. Validação de entrada com mensagens claras
2. Logging detalhado de erros
3. Retry automático para falhas temporárias
4. Fallback para cache em caso de falha de DB
5. Circuit breaker para serviços externos

## Testing Strategy

### Unit Tests

```python
# tests/test_cache_manager.py
class CacheManagerTests(TestCase):
    def test_cache_set_and_get(self)
    def test_cache_invalidation(self)
    def test_user_cache_isolation(self)

# tests/test_pagination.py
class PaginationTests(TestCase):
    def test_default_page_size(self)
    def test_custom_page_size(self)
    def test_max_page_size_limit(self)

# tests/test_rate_limiting.py
class RateLimitTests(TestCase):
    def test_anonymous_rate_limit(self)
    def test_authenticated_rate_limit(self)
    def test_rate_limit_reset(self)
```

### Integration Tests

```python
# tests/test_api_integration.py
class APIIntegrationTests(TestCase):
    def test_search_with_cache(self)
    def test_paginated_results_cached(self)
    def test_batch_operations_transactional(self)
    def test_websocket_notifications(self)
```

### Performance Tests

```python
# tests/test_performance.py
class PerformanceTests(TestCase):
    def test_search_response_time(self)
    def test_pagination_query_count(self)
    def test_cache_hit_rate(self)
    def test_compression_ratio(self)
```

### Load Tests

- Usar Locust ou Apache JMeter
- Simular 1000 usuários simultâneos
- Testar rate limiting sob carga
- Verificar degradação graceful

## Performance Considerations

### Database Optimization

1. **Índices**:
   - Adicionar índices em campos de busca frequente
   - Índices compostos para queries complexas
   - Índice geoespacial para busca por localização

2. **Query Optimization**:
   - Usar `select_related()` para ForeignKeys
   - Usar `prefetch_related()` para ManyToMany
   - Evitar N+1 queries
   - Usar `only()` e `defer()` quando apropriado

3. **Connection Pooling**:
   - Configurar pool de conexões
   - Timeout adequado
   - Max connections baseado em carga

### Cache Strategy

1. **Cache Warming**: Pre-popular cache de dados frequentes
2. **Cache Stampede Prevention**: Usar locks para evitar múltiplas queries simultâneas
3. **Cache Hierarchy**: Memory → Redis → Database
4. **TTL Strategy**: TTL baseado em frequência de mudança

### CDN Configuration

1. **Cache Headers**:
   - `Cache-Control: public, max-age=2592000` para estáticos
   - `Cache-Control: private, max-age=300` para dados de usuário
   - `ETag` para validação de cache

2. **Image Optimization**:
   - Compressão automática
   - Formatos modernos (WebP, AVIF)
   - Responsive images
   - Lazy loading

### Monitoring Metrics

1. **Response Time**: P50, P95, P99
2. **Throughput**: Requests per second
3. **Error Rate**: 4xx e 5xx por endpoint
4. **Cache Hit Rate**: Percentual de hits
5. **Database Query Time**: Tempo médio de queries
6. **WebSocket Connections**: Conexões ativas

## Security Considerations

1. **Rate Limiting**: Proteção contra DDoS e abuse
2. **Authentication**: JWT tokens para APIs
3. **Authorization**: Permissões granulares por endpoint
4. **Input Validation**: Sanitização de todos os inputs
5. **CORS**: Configuração adequada de origens permitidas
6. **SQL Injection**: Usar ORM, evitar raw queries
7. **XSS Protection**: Escape de outputs
8. **HTTPS Only**: Forçar HTTPS em produção

## Deployment Strategy

### Phase 1: Core APIs (Week 1-2)
- Cache Layer
- Pagination System
- Rate Limiting
- Compression

### Phase 2: Advanced Features (Week 3-4)
- Search API
- Analytics API
- Batch Processing
- Mobile Endpoints

### Phase 3: Real-time & CDN (Week 5-6)
- WebSocket Service
- CDN Integration
- API Versioning
- Bulk Admin APIs

### Rollout Plan

1. Deploy em ambiente de staging
2. Testes de carga e performance
3. Deploy gradual em produção (10% → 50% → 100%)
4. Monitoramento intensivo
5. Rollback plan preparado

## Migration Path

1. **Backward Compatibility**: Manter endpoints antigos funcionando
2. **Deprecation Warnings**: Avisar clientes sobre mudanças
3. **Documentation**: Atualizar docs com novos endpoints
4. **Client Updates**: Coordenar updates de clientes
5. **Monitoring**: Acompanhar uso de endpoints antigos vs novos
