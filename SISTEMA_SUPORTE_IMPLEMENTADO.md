# 🎧 Sistema de Suporte Completo - JobFinder

## 📋 Resumo

Foi implementado um sistema completo de suporte ao cliente com chat em tempo real entre clientes e agentes de suporte.

---

## ✨ Funcionalidades Implementadas

### 👤 Para Clientes

1. **Dashboard de Suporte**
   - Visualizar todos os tickets criados
   - Estatísticas (total, abertos, resolvidos, fechados)
   - Acesso rápido à base de conhecimento

2. **Criar Tickets**
   - Formulário completo com:
     - Assunto
     - Categoria (Técnico, Conta, Pagamento, Serviços, etc.)
     - Prioridade (Baixa, Média, Alta, Urgente)
     - Descrição detalhada
     - Anexo de arquivos (screenshots, documentos)

3. **Chat em Tempo Real**
   - Conversa direta com agente de suporte
   - Envio de mensagens e anexos
   - Histórico completo da conversa
   - Notificações de novas mensagens

4. **Avaliar Atendimento**
   - Avaliação de 1 a 5 estrelas
   - Feedback escrito
   - Fechamento do ticket após avaliação

### 🎧 Para Agentes de Suporte

1. **Dashboard do Agente**
   - Estatísticas em tempo real
   - Tickets não atribuídos
   - Meus tickets recentes
   - Tickets aguardando resposta

2. **Gerenciamento de Tickets**
   - Atribuir tickets a si mesmo
   - Desatribuir tickets
   - Atualizar status do ticket
   - Filtros avançados (status, prioridade, atribuição)
   - Busca por número, assunto ou cliente

3. **Chat com Cliente**
   - Responder mensagens
   - Enviar anexos
   - Notas internas (não visíveis ao cliente)
   - Mensagens do sistema

4. **Estatísticas Pessoais**
   - Total de tickets atendidos
   - Avaliação média
   - Tempo médio de resposta
   - Tempo médio de resolução
   - Tickets por categoria e status

### 📚 Base de Conhecimento

1. **Artigos de Ajuda**
   - Categorias organizadas
   - Busca por palavras-chave
   - Artigos mais visualizados
   - Avaliação de utilidade

2. **Categorias**
   - Primeiros Passos
   - Conta e Perfil
   - Serviços
   - Pagamentos
   - Problemas Técnicos
   - Políticas
   - Perguntas Frequentes

---

## 🗄️ Modelos Criados

### 1. SupportTicket
```python
- ticket_number: Número único do ticket (gerado automaticamente)
- customer: Cliente que abriu o ticket
- assigned_to: Agente responsável
- subject: Assunto
- description: Descrição detalhada
- category: Categoria do problema
- priority: Prioridade (baixa, média, alta, urgente)
- status: Status atual (aberto, em andamento, aguardando, resolvido, fechado)
- attachment: Arquivo anexo
- customer_rating: Avaliação do cliente (1-5)
- customer_feedback: Feedback do cliente
- created_at, updated_at, resolved_at, closed_at
```

### 2. SupportMessage
```python
- ticket: Ticket relacionado
- sender: Quem enviou a mensagem
- message_type: Tipo (mensagem, nota interna, sistema)
- content: Conteúdo da mensagem
- attachment: Arquivo anexo
- is_read: Se foi lida
- created_at: Data de envio
```

### 3. SupportAgent
```python
- user: Usuário do agente
- employee_id: ID do funcionário (gerado automaticamente)
- department: Departamento (técnico, financeiro, geral)
- is_active: Se está ativo
- is_available: Se está disponível
- max_concurrent_tickets: Máximo de tickets simultâneos
- total_tickets_handled: Total de tickets atendidos
- average_rating: Avaliação média
- average_response_time_minutes: Tempo médio de resposta
- average_resolution_time_hours: Tempo médio de resolução
```

### 4. SupportKnowledgeBase
```python
- title: Título do artigo
- slug: URL amigável
- category: Categoria
- content: Conteúdo completo
- summary: Resumo
- keywords: Palavras-chave para busca
- author: Autor do artigo
- is_published: Se está publicado
- view_count: Número de visualizações
- helpful_count: Quantos acharam útil
- not_helpful_count: Quantos não acharam útil
```

### 5. UserProfile (Atualizado)
```python
# Adicionado novo tipo de usuário:
USER_TYPE_CHOICES = [
    ('customer', 'Cliente'),
    ('professional', 'Profissional'),
    ('admin', 'Administrador'),
    ('support', 'Suporte'),  # NOVO!
]
```

---

## 🌐 URLs Criadas

### Cliente
- `/support/` - Dashboard de suporte
- `/support/create/` - Criar novo ticket
- `/support/ticket/<id>/` - Detalhes e chat do ticket
- `/support/ticket/<id>/rate/` - Avaliar atendimento

### Agente
- `/support/agent/` - Dashboard do agente
- `/support/agent/tickets/` - Lista de todos os tickets
- `/support/agent/ticket/<id>/assign/` - Atribuir ticket
- `/support/agent/ticket/<id>/status/` - Atualizar status
- `/support/agent/statistics/` - Estatísticas pessoais

### Base de Conhecimento
- `/support/kb/` - Lista de artigos
- `/support/kb/<slug>/` - Artigo específico
- `/support/kb/<slug>/rate/` - Avaliar artigo

### API
- `/api/support/unread-count/` - Contagem de mensagens não lidas

---

## 📁 Arquivos Criados

### Models
- `services/models.py` - Modelos adicionados ao final do arquivo

### Views
- `services/support_views.py` - Todas as views do sistema de suporte

### Templates
- `templates/services/support/customer_dashboard.html` - Dashboard do cliente
- `templates/services/support/create_ticket.html` - Criar ticket
- `templates/services/support/ticket_detail.html` - Detalhes e chat
- `templates/services/support/agent_dashboard.html` - Dashboard do agente

### URLs
- `services/urls.py` - URLs adicionadas

### Migrations
- `services/migrations/0033_*.py` - Migração criada automaticamente

---

## 🚀 Como Usar

### 1. Criar um Agente de Suporte

```python
# No Django Admin ou via shell
from django.contrib.auth.models import User
from services.models import SupportAgent

# Criar usuário
user = User.objects.create_user(
    username='agente1',
    email='agente1@jobfinder.com',
    password='senha123',
    first_name='João',
    last_name='Silva'
)

# Criar perfil de agente
agent = SupportAgent.objects.create(
    user=user,
    department='general',
    is_active=True,
    is_available=True
)

# O user_type será automaticamente definido como 'support'
```

### 2. Cliente Criar Ticket

1. Acesse: `/support/`
2. Clique em "Novo Ticket"
3. Preencha o formulário
4. Envie

### 3. Agente Atender Ticket

1. Acesse: `/support/agent/`
2. Veja tickets não atribuídos
3. Clique em "Ver" no ticket
4. Clique em "Atribuir a Mim"
5. Responda ao cliente via chat
6. Atualize o status conforme necessário

### 4. Cliente Avaliar Atendimento

1. Quando o ticket for resolvido
2. Acesse o ticket
3. Clique em "Avaliar Atendimento"
4. Dê nota de 1 a 5 estrelas
5. Deixe feedback (opcional)

---

## 🎨 Recursos Visuais

### Badges de Status
- **Aberto**: Badge azul
- **Em Andamento**: Badge info
- **Aguardando Cliente**: Badge warning
- **Aguardando Suporte**: Badge warning
- **Resolvido**: Badge success
- **Fechado**: Badge secondary

### Badges de Prioridade
- **Urgente**: Badge danger (vermelho)
- **Alta**: Badge warning (amarelo)
- **Média**: Badge secondary (cinza)
- **Baixa**: Badge secondary (cinza)

### Chat
- Mensagens do cliente: Fundo azul claro, alinhadas à direita
- Mensagens do suporte: Fundo branco, alinhadas à esquerda
- Mensagens do sistema: Fundo amarelo claro, centralizadas

---

## 📊 Estatísticas e Métricas

### Para Agentes
- Total de tickets atendidos
- Avaliação média (calculada automaticamente)
- Tempo médio de primeira resposta
- Tempo médio de resolução
- Taxa de resolução

### Para Administradores
- Tickets por status
- Tickets por categoria
- Tickets por prioridade
- Performance dos agentes
- Satisfação dos clientes

---

## 🔔 Notificações

O sistema cria notificações automáticas para:

1. **Agentes disponíveis** quando um novo ticket é criado
2. **Agente atribuído** quando um ticket é atribuído a ele
3. **Cliente** quando recebe uma resposta do suporte
4. **Cliente** quando o ticket é resolvido

---

## 🔐 Permissões

### Cliente
- Criar tickets
- Ver seus próprios tickets
- Enviar mensagens em seus tickets
- Avaliar atendimento

### Agente de Suporte
- Ver todos os tickets
- Atribuir tickets a si mesmo
- Responder tickets
- Atualizar status
- Criar notas internas
- Ver estatísticas pessoais

### Administrador
- Todas as permissões de agente
- Gerenciar agentes
- Ver estatísticas globais
- Gerenciar base de conhecimento

---

## 🎯 Próximos Passos (Opcional)

### Melhorias Futuras
1. **WebSocket para chat em tempo real** (atualmente usa refresh)
2. **Notificações push** no navegador
3. **Anexos múltiplos** por mensagem
4. **Templates de resposta** para agentes
5. **Macros** para ações comuns
6. **SLA (Service Level Agreement)** com alertas
7. **Relatórios avançados** com gráficos
8. **Integração com email** (criar ticket por email)
9. **Chat bot** para respostas automáticas
10. **Pesquisa de satisfação** automática

---

## 📝 Notas Importantes

1. **Migrations**: Já foram executadas com sucesso
2. **Tipo de usuário**: Automaticamente definido como 'support' ao criar SupportAgent
3. **Número do ticket**: Gerado automaticamente no formato `TK20241202HHMMSSXXXX`
4. **Anexos**: Salvos em `media/support_attachments/` e `media/support_message_attachments/`
5. **Permissões**: Verificadas em cada view com `is_support_agent()`

---

## 🐛 Troubleshooting

### Problema: Agente não consegue acessar dashboard
**Solução**: Verificar se o user_type está definido como 'support' no UserProfile

### Problema: Tickets não aparecem
**Solução**: Verificar filtros aplicados e permissões do usuário

### Problema: Anexos não carregam
**Solução**: Verificar configuração de MEDIA_URL e MEDIA_ROOT no settings.py

---

## 📞 Contato

Para dúvidas sobre o sistema de suporte, consulte a documentação ou crie um ticket! 😄

---

**Desenvolvido para o Projeto Integrador SENAC - JobFinder**  
**Data**: Dezembro 2024
