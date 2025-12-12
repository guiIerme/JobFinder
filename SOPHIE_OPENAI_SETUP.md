# 🤖 Configuração da Sophie com OpenAI - Guia Completo

## 📋 Visão Geral
A Sophie é a assistente virtual do JobFinder que pode funcionar de duas formas:
1. **Modo OpenAI** - Respostas inteligentes usando GPT-4
2. **Modo Fallback** - Respostas pré-definidas baseadas em intenções

## 🔑 Configuração da API OpenAI

### 1. Obter Chave da API
1. Acesse https://platform.openai.com/
2. Faça login ou crie uma conta
3. Vá em "API Keys" no menu
4. Clique em "Create new secret key"
5. Copie a chave (começa com `sk-`)

### 2. Configurar no Projeto
Edite o arquivo `.env` e substitua:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

Por:
```env
OPENAI_API_KEY=sk-sua-chave-real-aqui
```

### 3. Configurações Opcionais
```env
# Modelo (padrão: gpt-4)
OPENAI_MODEL=gpt-4

# Temperatura - criatividade (0.0 a 1.0)
OPENAI_TEMPERATURE=0.7

# Máximo de tokens por resposta
OPENAI_MAX_TOKENS=500
```

## 🚀 Como Testar

### 1. Verificar Configuração
```bash
python manage.py shell
```

```python
from django.conf import settings
print("Chave configurada:", bool(settings.CHAT_CONFIG['OPENAI_API_KEY']))
print("Modelo:", settings.CHAT_CONFIG['OPENAI_MODEL'])
```

### 2. Testar AI Processor
```python
from services.ai_processor import AIProcessor
import asyncio

async def test_ai():
    processor = AIProcessor()
    response, metadata = await processor.process_message(
        "Olá, como você pode me ajudar?",
        {'user_type': 'client'},
        []
    )
    print("Resposta:", response)
    print("Metadata:", metadata)

# Executar teste
asyncio.run(test_ai())
```

### 3. Testar no Chat
1. Acesse o site: http://localhost:8000
2. Clique no botão de chat (canto inferior direito)
3. Digite uma mensagem
4. Verifique se a Sophie responde inteligentemente

## 🔧 Modo Fallback (Sem OpenAI)

Se não configurar a chave da OpenAI, a Sophie funcionará em modo fallback com respostas pré-definidas baseadas em intenções:

### Intenções Suportadas:
- **Saudação**: "Olá", "Oi", "Bom dia"
- **Ajuda**: "Ajuda", "Como", "Não sei"
- **Serviços**: "Serviço", "Contratar", "Preço"
- **Navegação**: "Onde", "Como fazer", "Página"
- **Prestador**: "Solicitação", "Aceitar", "Recusar"
- **Pagamento**: "Pagamento", "Pagar", "Valor"
- **Agradecimento**: "Obrigado", "Valeu"
- **Despedida**: "Tchau", "Adeus", "Até"

### Exemplo de Respostas Fallback:
```
Usuário: "Oi"
Sophie: "Olá! 👋 Eu sou a Sophie, sua assistente virtual. Como posso ajudá-lo hoje?"

Usuário: "Como contratar um serviço?"
Sophie: "Temos diversos profissionais qualificados disponíveis! Você pode:
1. 🔍 Buscar profissionais na página "Buscar Profissionais"
2. 🎯 Filtrar por categoria e localização
3. ⭐ Ver avaliações e portfólio
4. 📝 Solicitar orçamento diretamente"
```

## 💰 Custos da OpenAI

### Preços Aproximados (GPT-4):
- **Input**: $0.03 por 1K tokens
- **Output**: $0.06 por 1K tokens
- **Média por conversa**: $0.01 - $0.05

### Dicas para Economizar:
1. Use `gpt-3.5-turbo` em vez de `gpt-4` (mais barato)
2. Configure `OPENAI_MAX_TOKENS=300` (respostas menores)
3. Ative cache: `CHAT_CACHE_ENABLED=True`

## 🛠️ Troubleshooting

### Erro: "OpenAI library not available"
```bash
pip install openai
```

### Erro: "Invalid API key"
1. Verifique se a chave está correta no `.env`
2. Confirme que a chave não expirou
3. Verifique se tem créditos na conta OpenAI

### Sophie não responde
1. Verifique os logs: `tail -f django.log`
2. Teste o WebSocket: Abra DevTools → Network → WS
3. Verifique se o servidor está rodando

### Respostas muito lentas
1. Use modelo mais rápido: `OPENAI_MODEL=gpt-3.5-turbo`
2. Reduza tokens: `OPENAI_MAX_TOKENS=200`
3. Ative cache: `CHAT_CACHE_ENABLED=True`

## 📊 Monitoramento

### Logs da Sophie
```bash
# Ver logs em tempo real
tail -f django.log | grep -i sophie

# Ver apenas erros
tail -f django.log | grep ERROR
```

### Métricas no Admin
1. Acesse: http://localhost:8000/admin/
2. Vá em "Chat Analytics"
3. Veja estatísticas de uso

## 🔒 Segurança

### Boas Práticas:
1. **Nunca** commite a chave da API no Git
2. Use variáveis de ambiente em produção
3. Configure rate limiting adequado
4. Monitore uso para evitar custos excessivos

### Configurações de Segurança:
```env
# Rate limiting (mensagens por minuto)
CHAT_RATE_LIMIT=10

# Tamanho máximo da mensagem
CHAT_MAX_MSG_LENGTH=2000

# Cache para reduzir chamadas à API
CHAT_CACHE_ENABLED=True
CHAT_CACHE_TTL=3600
```

## ✅ Checklist de Configuração

- [ ] Chave da OpenAI configurada no `.env`
- [ ] Biblioteca `openai` instalada
- [ ] Teste básico funcionando
- [ ] Chat widget respondendo
- [ ] Logs sem erros
- [ ] Rate limiting configurado
- [ ] Cache habilitado

## 🎯 Próximos Passos

1. **Personalizar Prompts**: Edite `ai_processor.py` → `build_system_prompt()`
2. **Adicionar Contexto**: Implemente detecção de página atual
3. **Melhorar Intenções**: Adicione novas categorias em `extract_intent()`
4. **Analytics**: Configure monitoramento de uso
5. **Escalação**: Configure integração com suporte humano

---

**🤖 A Sophie está pronta para ajudar seus usuários!**