# Configuração do Chat Sophie com OpenAI

## ✅ Status da Implementação

O chat Sophie está **totalmente implementado** e pronto para uso! Agora ele usa a API REST do Django que se conecta à OpenAI para gerar respostas inteligentes.

## 🔧 O que foi implementado:

### Backend (Django)
- ✅ **Models**: `ChatSession`, `ChatMessage`, `ChatAnalytics`, `KnowledgeBaseEntry`
- ✅ **API REST**: Endpoints `/api/chat/message/` e `/api/chat/rating/`
- ✅ **AI Processor**: Integração com OpenAI API
- ✅ **Caching**: Sistema de cache para respostas frequentes
- ✅ **Rate Limiting**: Proteção contra spam
- ✅ **Analytics**: Métricas de uso e satisfação

### Frontend (JavaScript)
- ✅ **Chat Widget**: Botão flutuante
- ✅ **Chat Window**: Interface completa
- ✅ **API Integration**: Comunicação com backend via REST
- ✅ **Typing Indicator**: Indicador de digitação
- ✅ **Message History**: Histórico de conversas
- ✅ **Rating System**: Avaliação de satisfação

## 🚀 Como Configurar a OpenAI API

### Passo 1: Obter a Chave da API

1. Acesse [https://platform.openai.com/](https://platform.openai.com/)
2. Faça login ou crie uma conta
3. Vá em **API Keys** no menu lateral
4. Clique em **Create new secret key**
5. Copie a chave (ela começa com `sk-...`)

### Passo 2: Configurar no Projeto

Abra o arquivo `.env` na raiz do projeto e substitua:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Por:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### Passo 3: Reiniciar o Servidor

```bash
# Pare o servidor (Ctrl+C)
# Inicie novamente
python manage.py runserver
```

## 💰 Custos da OpenAI

### Modelo GPT-4 (Padrão)
- **Input**: ~$0.03 por 1K tokens
- **Output**: ~$0.06 por 1K tokens
- **Estimativa**: ~$0.01 por conversa típica

### Modelo GPT-3.5-Turbo (Econômico)
Para usar o modelo mais barato, altere no `.env`:

```env
OPENAI_MODEL=gpt-3.5-turbo
```

- **Input**: ~$0.0015 por 1K tokens
- **Output**: ~$0.002 por 1K tokens
- **Estimativa**: ~$0.001 por conversa típica

## 🧪 Testando o Chat

### 1. Sem Chave da OpenAI (Modo Fallback)
Se você não configurar a chave, o chat funcionará com respostas pré-programadas:

```python
# O sistema detecta automaticamente e usa fallback
if not self.api_key:
    logger.warning('OpenAI API key not configured. Using fallback mode.')
```

### 2. Com Chave da OpenAI (Modo IA)
Com a chave configurada, Sophie usará IA para:
- Entender contexto da conversa
- Gerar respostas personalizadas
- Adaptar-se ao tipo de usuário (cliente/prestador)
- Lembrar do histórico da conversa

## 📊 Monitoramento

### Ver Logs do Chat
```bash
# Ver logs em tempo real
tail -f django.log | grep chat
```

### Acessar Analytics (Admin)
1. Acesse `/admin/`
2. Vá em **Services** > **Chat Analytics**
3. Veja métricas de:
   - Total de mensagens
   - Tempo médio de resposta
   - Avaliações de satisfação
   - Sessões ativas

## 🔒 Segurança

O sistema já implementa:
- ✅ Rate limiting (10 mensagens/minuto)
- ✅ Validação de entrada
- ✅ Sanitização de HTML
- ✅ Limite de tamanho de mensagem (2000 caracteres)
- ✅ CSRF protection
- ✅ Session validation

## 🎯 Funcionalidades Avançadas

### Cache de Respostas
Respostas similares são cacheadas por 1 hora para:
- Reduzir custos da API
- Melhorar tempo de resposta
- Economizar tokens

### Detecção de Intenção
O sistema detecta automaticamente:
- Saudações
- Pedidos de ajuda
- Perguntas sobre serviços
- Questões de navegação
- Perguntas sobre pagamento
- Agradecimentos
- Despedidas

### Contexto Inteligente
Sophie sabe:
- Tipo de usuário (cliente/prestador/anônimo)
- Página atual do usuário
- Histórico da conversa
- Preferências do usuário

## 🐛 Troubleshooting

### Erro: "OpenAI API key not configured"
**Solução**: Configure a chave no arquivo `.env`

### Erro: "Rate limit exceeded"
**Solução**: Aguarde 1 minuto ou aumente o limite em `settings.py`:
```python
'RATE_LIMIT_MESSAGES_PER_MINUTE': 20,  # Aumentar de 10 para 20
```

### Erro: "Invalid API key"
**Solução**: Verifique se a chave está correta e ativa em [platform.openai.com](https://platform.openai.com/)

### Chat não abre
**Solução**: 
1. Verifique o console do navegador (F12)
2. Certifique-se que os arquivos JS estão carregando
3. Limpe o cache do navegador

## 📝 Exemplos de Uso

### Conversa Típica

**Usuário**: "Oi Sophie!"
**Sophie**: "Olá! 👋 Eu sou a Sophie, sua assistente virtual. Como posso ajudá-lo hoje?"

**Usuário**: "Preciso contratar um eletricista"
**Sophie**: "Ótimo! Posso ajudá-lo a encontrar um eletricista qualificado. Você pode:

1. 🔍 Ir para 'Buscar Profissionais'
2. 🎯 Filtrar por 'Elétrica'
3. 📍 Escolher sua localização
4. ⭐ Ver avaliações e portfólio

Gostaria que eu te direcionasse para a página de busca?"

## 🔄 Próximos Passos

Para melhorar ainda mais o chat:

1. **Adicionar Knowledge Base**: Criar entradas na base de conhecimento
2. **Treinar com FAQs**: Adicionar perguntas frequentes
3. **Integrar com Serviços**: Conectar com busca de profissionais
4. **Adicionar Ações**: Permitir Sophie executar ações (agendar, solicitar)
5. **Multilíngua**: Suporte para outros idiomas

## 📚 Documentação Adicional

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Chat Models Documentation](./services/chat_models.py)
- [AI Processor Documentation](./services/ai_processor.py)

## 💡 Dicas

1. **Desenvolvimento**: Use `gpt-3.5-turbo` para economizar
2. **Produção**: Use `gpt-4` para melhor qualidade
3. **Cache**: Mantenha ativado para economizar
4. **Logs**: Monitore para identificar problemas
5. **Feedback**: Use as avaliações para melhorar

---

**Status**: ✅ Pronto para uso!
**Última atualização**: Dezembro 2024
