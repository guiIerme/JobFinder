# Chat IA Assistente (Sophie)

Sistema de chat ao vivo com inteligência artificial para auxiliar usuários do Job Finder.

## Estrutura do Módulo

```
services/chat/
├── __init__.py              # Inicialização do pacote
├── consumers.py             # WebSocket consumer para conexões de chat
├── manager.py               # Gerenciamento de sessões e mensagens
├── ai_processor.py          # Integração com OpenAI API
├── context_manager.py       # Gerenciamento de contexto do usuário
├── knowledge_base.py        # Base de conhecimento e FAQs
├── models.py                # Modelos de banco de dados
├── error_handler.py         # Tratamento de erros e fallbacks
└── README.md                # Esta documentação
```

## Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

As seguintes dependências foram adicionadas:
- `openai==1.54.0` - SDK da OpenAI para integração com GPT-4
- `redis==5.0.1` - Cliente Redis para cache e channel layer

### 2. Configurar Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```env
# OpenAI API Key (obrigatório)
OPENAI_API_KEY=sk-your-api-key-here

# Redis (opcional para desenvolvimento)
USE_REDIS=false  # true para produção com Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Executar Migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Iniciar Redis (Produção)

Para ambiente de produção, instale e inicie o Redis:

```bash
# Windows (usando Chocolatey)
choco install redis-64

# Ou baixe de: https://github.com/microsoftarchive/redis/releases

# Iniciar Redis
redis-server
```

## Modelos de Dados

### ChatSession
Representa uma sessão de conversa entre usuário e Sophie.

### ChatMessage
Armazena mensagens individuais em uma sessão.

### KnowledgeBaseEntry
Contém informações sobre serviços, FAQs e guias de navegação.

### ChatAnalytics
Armazena métricas e analytics de sessões de chat.

## WebSocket Endpoint

```
ws://localhost:8000/ws/chat/
```

## Configurações

Todas as configurações estão em `settings.py` sob `CHAT_CONFIG`:

- `OPENAI_MODEL`: Modelo GPT a usar (padrão: gpt-4)
- `MAX_HISTORY_MESSAGES`: Máximo de mensagens no histórico (padrão: 50)
- `SESSION_TIMEOUT_HOURS`: Timeout de sessão (padrão: 24h)
- `RATE_LIMIT_MESSAGES_PER_MINUTE`: Limite de mensagens por minuto (padrão: 10)
- `CACHE_TTL_SECONDS`: TTL do cache de respostas (padrão: 3600s)
- `MAX_CONCURRENT_SESSIONS`: Máximo de sessões simultâneas (padrão: 100)
- `RESPONSE_TIMEOUT_SECONDS`: Timeout de resposta da API (padrão: 30s)
- `MAX_MESSAGE_LENGTH`: Tamanho máximo de mensagem (padrão: 2000 chars)

## Próximos Passos

Este módulo contém a estrutura base. As próximas tarefas implementarão:

1. **Task 2**: Modelos de dados e migrações
2. **Task 3**: WebSocket consumer e gerenciamento de conexões
3. **Task 4**: ChatManager para lógica de negócio
4. **Task 5**: AIProcessor para integração com OpenAI
5. **Task 6**: ContextManager para contexto do usuário
6. **Task 7**: KnowledgeBase para informações e FAQs
7. **Tasks 8-9**: Frontend (widget e janela de chat)
8. **Tasks 10-15**: Error handling, analytics, testes e deployment

## Desenvolvimento

Para desenvolvimento local sem Redis:
- Mantenha `USE_REDIS=false` no `.env`
- O sistema usará in-memory backends
- Funcional para um único processo/worker

Para produção:
- Configure `USE_REDIS=true`
- Instale e configure Redis
- Suporta múltiplos workers e escalabilidade

## Requisitos Atendidos

Esta implementação atende aos seguintes requisitos:

- **8.1**: Suporte a 100+ sessões simultâneas (com Redis)
- **8.2**: Cache de respostas frequentes
- **8.3**: Rate limiting configurável
