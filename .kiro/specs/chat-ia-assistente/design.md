# Design Document - Chat IA Assistente (Sophie)

## Overview

Este documento descreve o design técnico para implementação de um sistema de chat ao vivo com inteligência artificial chamado Sophie. O sistema fornecerá suporte em tempo real aos usuários, ajudando-os a navegar no site, encontrar serviços e resolver problemas comuns.

Sophie será integrada ao site existente de serviços domésticos (Job Finder), utilizando a arquitetura Django existente e adicionando novos componentes para processamento de linguagem natural e gerenciamento de conversas.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Widget  │  │ Chat Window  │  │ Message UI   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Layer                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Django Channels (WebSocket Consumer)         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Manager │  │ AI Processor │  │ Context      │      │
│  │              │  │              │  │ Manager      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Session │  │ AI Messages  │  │ Knowledge    │      │
│  │ Database     │  │ Database     │  │ Base         │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ OpenAI API   │  │ Redis Cache  │  │ Analytics    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: Vanilla JavaScript (integração com base.html existente)
- **WebSocket**: Django Channels 4.x com Redis channel layer
- **Backend**: Django 4.x (framework existente)
- **AI Engine**: OpenAI GPT-4 API
- **Database**: PostgreSQL/SQLite (existente) para persistência de sessões
- **Cache**: Redis para sessões ativas e rate limiting
- **Message Queue**: Redis para processamento assíncrono

### Design Decisions

1. **WebSocket vs HTTP Polling**: Escolhemos WebSocket (Django Channels) para comunicação em tempo real, proporcionando latência mínima e melhor experiência do usuário.

2. **OpenAI GPT-4**: Utilizaremos a API da OpenAI para processamento de linguagem natural, oferecendo respostas contextuais e compreensão avançada.

3. **Redis para Cache**: Implementaremos cache de respostas frequentes e gerenciamento de sessões ativas para reduzir custos de API e melhorar performance.

4. **Integração com Sistema Existente**: O widget será injetado no template base.html existente, mantendo consistência visual e aproveitando a infraestrutura atual.

## Components and Interfaces

### Frontend Components

#### 1. Chat Widget Button
**Responsabilidade**: Botão flutuante que abre/fecha a janela de chat

**Interface**:
```javascript
class ChatWidget {
  constructor(options)
  show()
  hide()
  toggle()
  setUnreadCount(count)
  updatePosition()
}
```

**Propriedades**:
- Posicionamento: fixed, bottom-right, acima do botão de acessibilidade
- Z-index: 999 (abaixo do botão de acessibilidade que tem 1000)
- Responsivo: adapta-se a diferentes tamanhos de tela
- Badge de notificação para mensagens não lidas

#### 2. Chat Window
**Responsabilidade**: Interface principal de conversação

**Interface**:
```javascript
class ChatWindow {
  constructor(websocketUrl)
  open()
  close()
  minimize()
  maximize()
  sendMessage(text)
  receiveMessage(message)
  displayTypingIndicator()
  hideTypingIndicator()
  loadHistory()
  clearHistory()
}
```

**Características**:
- Dimensões: 380px x 600px (desktop), fullscreen (mobile)
- Header com nome "Sophie" e controles (minimizar/fechar)
- Área de mensagens com scroll automático
- Input de texto com botão de envio
- Indicador de digitação
- Suporte a markdown nas respostas

#### 3. Message Component
**Responsabilidade**: Renderização individual de mensagens

**Interface**:
```javascript
class Message {
  constructor(data)
  render()
  formatTimestamp()
  renderLinks()
  renderMarkdown()
}
```

**Tipos de Mensagem**:
- Mensagem do usuário (alinhada à direita)
- Mensagem de Sophie (alinhada à esquerda)
- Mensagem do sistema (centralizada)
- Mensagem com ações/botões

### Backend Components

#### 1. ChatConsumer (WebSocket Handler)
**Responsabilidade**: Gerenciar conexões WebSocket e roteamento de mensagens

**Interface**:
```python
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self)
    async def disconnect(self, close_code)
    async def receive(self, text_data)
    async def send_message(self, event)
    async def send_typing_indicator(self, event)
    async def authenticate_user(self)
    async def load_session(self)
```

**Funcionalidades**:
- Autenticação de usuário via session
- Gerenciamento de grupos de chat por sessão
- Rate limiting por usuário
- Logging de todas as interações

#### 2. ChatManager
**Responsabilidade**: Lógica de negócio para gerenciamento de conversas

**Interface**:
```python
class ChatManager:
    def create_session(user, context)
    def get_session(session_id)
    def save_message(session, message, sender)
    def get_history(session, limit=50)
    def update_context(session, context)
    def close_session(session_id)
    def get_active_sessions(user)
```

**Funcionalidades**:
- Criação e recuperação de sessões
- Persistência de mensagens
- Gerenciamento de contexto de navegação
- Limpeza de sessões antigas (>24h)

#### 3. AIProcessor
**Responsabilidade**: Integração com OpenAI e processamento de respostas

**Interface**:
```python
class AIProcessor:
    def __init__(self, api_key)
    async def process_message(self, message, context, history)
    def build_system_prompt(self, user_type, context)
    def extract_intent(self, message)
    def generate_response(self, prompt, history)
    def check_cache(self, message_hash)
    def save_to_cache(self, message_hash, response)
```

**Funcionalidades**:
- Construção de prompts contextuais
- Integração com OpenAI GPT-4
- Cache de respostas frequentes
- Detecção de intenção do usuário
- Fallback para respostas pré-definidas

#### 4. ContextManager
**Responsabilidade**: Gerenciar contexto de navegação e perfil do usuário

**Interface**:
```python
class ContextManager:
    def get_user_context(user)
    def get_navigation_context(current_url, referrer)
    def get_service_context(service_id)
    def build_knowledge_base_context(query)
    def get_user_preferences(user)
```

**Funcionalidades**:
- Extração de informações do perfil do usuário
- Análise da página atual e histórico de navegação
- Consulta à base de conhecimento (serviços, FAQs)
- Personalização baseada em preferências

#### 5. KnowledgeBase
**Responsabilidade**: Armazenar e consultar informações sobre o sistema

**Interface**:
```python
class KnowledgeBase:
    def search(self, query, category=None)
    def get_service_info(self, service_id)
    def get_faq(self, topic)
    def get_navigation_help(self, page)
    def add_entry(self, content, category, metadata)
    def update_entry(self, entry_id, content)
```

**Categorias**:
- Informações de serviços
- FAQs
- Guias de navegação
- Políticas e termos
- Troubleshooting comum

## Data Models

### ChatSession Model
```python
class ChatSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    anonymous_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    context_data = models.JSONField(default=dict)
    user_type = models.CharField(max_length=20, choices=[
        ('client', 'Cliente'),
        ('provider', 'Prestador'),
        ('anonymous', 'Anônimo')
    ])
    satisfaction_rating = models.IntegerField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active', '-updated_at']),
        ]
```

### ChatMessage Model
```python
class ChatMessage(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=[
        ('user', 'Usuário'),
        ('assistant', 'Sophie'),
        ('system', 'Sistema')
    ])
    content = models.TextField()
    metadata = models.JSONField(default=dict)  # intent, confidence, links, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    is_cached_response = models.BooleanField(default=False)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
```

### KnowledgeBaseEntry Model
```python
class KnowledgeBaseEntry(models.Model):
    entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    category = models.CharField(max_length=50, choices=[
        ('service', 'Serviço'),
        ('faq', 'FAQ'),
        ('navigation', 'Navegação'),
        ('policy', 'Política'),
        ('troubleshooting', 'Solução de Problemas')
    ])
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.JSONField(default=list)
    related_services = models.ManyToManyField('services.Service', blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]
```

### ChatAnalytics Model
```python
class ChatAnalytics(models.Model):
    analytics_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE)
    total_messages = models.IntegerField(default=0)
    user_messages = models.IntegerField(default=0)
    assistant_messages = models.IntegerField(default=0)
    average_response_time_ms = models.FloatField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    escalated_to_human = models.BooleanField(default=False)
    topics_discussed = models.JSONField(default=list)
    actions_taken = models.JSONField(default=list)  # links clicked, services viewed, etc.
    created_at = models.DateTimeField(auto_now_add=True)
```

## Error Handling

### Error Categories

1. **Connection Errors**
   - WebSocket connection failure
   - Network timeout
   - Server unavailable

2. **AI Processing Errors**
   - OpenAI API failure
   - Rate limit exceeded
   - Invalid response format

3. **Data Errors**
   - Session not found
   - Invalid message format
   - Database connection failure

### Error Handling Strategy

#### Frontend Error Handling
```javascript
// Reconnection strategy
const reconnectStrategy = {
  maxAttempts: 5,
  baseDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2
};

// User-friendly error messages
const errorMessages = {
  'connection_failed': 'Não foi possível conectar ao chat. Tentando reconectar...',
  'message_send_failed': 'Falha ao enviar mensagem. Tente novamente.',
  'session_expired': 'Sua sessão expirou. Iniciando nova conversa...',
  'ai_unavailable': 'Sophie está temporariamente indisponível. Tente novamente em alguns instantes.'
};
```

#### Backend Error Handling
```python
class ChatErrorHandler:
    @staticmethod
    async def handle_ai_error(error, session):
        """Fallback to predefined responses when AI fails"""
        logger.error(f"AI Error in session {session.session_id}: {error}")
        
        # Return fallback response
        return {
            'type': 'fallback',
            'message': 'Desculpe, estou com dificuldades no momento. Posso ajudá-lo com:\n'
                      '- Ver serviços disponíveis\n'
                      '- Acessar meus pedidos\n'
                      '- Falar com suporte humano',
            'actions': [
                {'label': 'Ver Serviços', 'url': '/services/'},
                {'label': 'Meus Pedidos', 'url': '/meus-pedidos/'},
                {'label': 'Contato', 'url': '/contact/'}
            ]
        }
    
    @staticmethod
    async def handle_rate_limit(user):
        """Handle rate limit exceeded"""
        return {
            'type': 'rate_limit',
            'message': 'Você atingiu o limite de mensagens. Por favor, aguarde alguns minutos.',
            'retry_after': 60
        }
    
    @staticmethod
    async def handle_session_error(error):
        """Handle session-related errors"""
        logger.error(f"Session Error: {error}")
        return {
            'type': 'session_error',
            'message': 'Ocorreu um erro com sua sessão. Vamos iniciar uma nova conversa.',
            'action': 'create_new_session'
        }
```

### Logging Strategy
```python
# Structured logging for all chat interactions
import structlog

logger = structlog.get_logger()

# Log levels:
# - INFO: Normal operations (message sent/received)
# - WARNING: Fallback responses, cache misses
# - ERROR: AI failures, connection issues
# - CRITICAL: System-wide failures

logger.info(
    "message_processed",
    session_id=session.session_id,
    user_id=user.id,
    processing_time_ms=processing_time,
    intent=intent,
    cached=is_cached
)
```

## Testing Strategy

### Unit Tests

#### Frontend Tests
```javascript
// Test suite for Chat Widget
describe('ChatWidget', () => {
  test('should initialize with correct position', () => {});
  test('should toggle visibility on click', () => {});
  test('should update unread count badge', () => {});
  test('should maintain position above accessibility button', () => {});
});

// Test suite for Chat Window
describe('ChatWindow', () => {
  test('should establish WebSocket connection', () => {});
  test('should send and receive messages', () => {});
  test('should display typing indicator', () => {});
  test('should load message history', () => {});
  test('should handle connection errors gracefully', () => {});
});
```

#### Backend Tests
```python
# Test suite for ChatManager
class ChatManagerTests(TestCase):
    def test_create_session(self):
        """Test session creation for authenticated and anonymous users"""
        pass
    
    def test_save_message(self):
        """Test message persistence"""
        pass
    
    def test_get_history(self):
        """Test history retrieval with pagination"""
        pass
    
    def test_session_cleanup(self):
        """Test automatic cleanup of old sessions"""
        pass

# Test suite for AIProcessor
class AIProcessorTests(TestCase):
    def test_process_message_with_cache(self):
        """Test cached response retrieval"""
        pass
    
    def test_process_message_with_api(self):
        """Test OpenAI API integration"""
        pass
    
    def test_fallback_on_api_failure(self):
        """Test fallback to predefined responses"""
        pass
    
    def test_intent_extraction(self):
        """Test intent detection from user messages"""
        pass

# Test suite for ContextManager
class ContextManagerTests(TestCase):
    def test_user_context_client(self):
        """Test context building for client users"""
        pass
    
    def test_user_context_provider(self):
        """Test context building for provider users"""
        pass
    
    def test_navigation_context(self):
        """Test navigation context extraction"""
        pass
```

### Integration Tests

```python
class ChatIntegrationTests(TestCase):
    def test_full_conversation_flow(self):
        """Test complete conversation from connection to closure"""
        # 1. Establish WebSocket connection
        # 2. Send user message
        # 3. Receive AI response
        # 4. Verify message persistence
        # 5. Close connection
        pass
    
    def test_session_persistence_across_reconnections(self):
        """Test session recovery after disconnect"""
        pass
    
    def test_concurrent_sessions(self):
        """Test multiple simultaneous chat sessions"""
        pass
    
    def test_rate_limiting(self):
        """Test rate limit enforcement"""
        pass
```

### Performance Tests

```python
class ChatPerformanceTests(TestCase):
    def test_response_time_under_load(self):
        """Test response time with 100 concurrent sessions"""
        # Target: <2s for 95% of requests
        pass
    
    def test_websocket_connection_limit(self):
        """Test maximum concurrent WebSocket connections"""
        # Target: 100+ concurrent connections
        pass
    
    def test_cache_effectiveness(self):
        """Test cache hit rate for common queries"""
        # Target: >70% cache hit rate
        pass
    
    def test_database_query_performance(self):
        """Test database query performance under load"""
        pass
```

### End-to-End Tests

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

class ChatE2ETests(TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
    
    def test_chat_widget_visibility(self):
        """Test chat widget appears on all pages"""
        pass
    
    def test_send_message_and_receive_response(self):
        """Test complete user interaction flow"""
        pass
    
    def test_mobile_responsiveness(self):
        """Test chat interface on mobile viewport"""
        pass
    
    def test_navigation_with_active_chat(self):
        """Test chat persistence during page navigation"""
        pass
    
    def tearDown(self):
        self.driver.quit()
```

### Test Data

```python
# Sample test messages for different intents
TEST_MESSAGES = {
    'service_inquiry': [
        'Quais serviços de limpeza vocês oferecem?',
        'Quanto custa um encanador?',
        'Preciso de um eletricista urgente'
    ],
    'navigation_help': [
        'Como faço para solicitar um serviço?',
        'Onde vejo meus pedidos?',
        'Como atualizo meu perfil?'
    ],
    'provider_questions': [
        'Como aceito uma solicitação?',
        'Onde vejo meus pagamentos?',
        'Como atualizo minha disponibilidade?'
    ],
    'general': [
        'Olá',
        'Preciso de ajuda',
        'Obrigado'
    ]
}

# Sample knowledge base entries
TEST_KNOWLEDGE_BASE = [
    {
        'category': 'service',
        'title': 'Serviços de Limpeza',
        'content': 'Oferecemos limpeza residencial, comercial e pós-obra...',
        'keywords': ['limpeza', 'faxina', 'cleaning']
    },
    {
        'category': 'faq',
        'title': 'Como solicitar um serviço',
        'content': 'Para solicitar um serviço: 1. Navegue até a página de serviços...',
        'keywords': ['solicitar', 'pedir', 'contratar']
    }
]
```

## Implementation Notes

### Phase 1: Core Infrastructure (Week 1)
- Setup Django Channels and Redis
- Create data models and migrations
- Implement WebSocket consumer
- Basic frontend widget and window

### Phase 2: AI Integration (Week 2)
- Integrate OpenAI API
- Implement AIProcessor with caching
- Build ContextManager
- Create KnowledgeBase system

### Phase 3: Features & Polish (Week 3)
- Session persistence and recovery
- Rate limiting and error handling
- Analytics and admin dashboard
- Mobile responsiveness

### Phase 4: Testing & Optimization (Week 4)
- Comprehensive testing
- Performance optimization
- Load testing
- Documentation

### Configuration

```python
# settings.py additions
CHAT_CONFIG = {
    'OPENAI_API_KEY': env('OPENAI_API_KEY'),
    'OPENAI_MODEL': 'gpt-4',
    'MAX_HISTORY_MESSAGES': 50,
    'SESSION_TIMEOUT_HOURS': 24,
    'RATE_LIMIT_MESSAGES_PER_MINUTE': 10,
    'CACHE_TTL_SECONDS': 3600,
    'MAX_CONCURRENT_SESSIONS': 100,
    'RESPONSE_TIMEOUT_SECONDS': 30,
    'ENABLE_ANALYTICS': True,
    'FALLBACK_RESPONSES': True
}

# Redis configuration for Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}
```

### Security Considerations

1. **Authentication**: Verificar autenticação do usuário via Django session
2. **Rate Limiting**: Implementar rate limiting por usuário e IP
3. **Input Validation**: Sanitizar todas as entradas do usuário
4. **API Key Protection**: Armazenar chaves de API em variáveis de ambiente
5. **XSS Prevention**: Escapar conteúdo HTML nas mensagens
6. **CORS**: Configurar CORS apropriadamente para WebSocket
7. **Message Size Limits**: Limitar tamanho de mensagens (max 2000 caracteres)

### Monitoring and Observability

```python
# Metrics to track
CHAT_METRICS = {
    'active_sessions': 'Gauge',
    'messages_sent': 'Counter',
    'messages_received': 'Counter',
    'ai_api_calls': 'Counter',
    'cache_hits': 'Counter',
    'cache_misses': 'Counter',
    'response_time': 'Histogram',
    'error_rate': 'Counter',
    'satisfaction_rating': 'Histogram'
}
```
