# 🚀 Guia Rápido - Sistema de Suporte

## ⚡ Início Rápido

### 1. Criar um Agente de Suporte

Execute o script:
```bash
python create_support_agent.py
```

Ou manualmente no Django shell:
```bash
python manage.py shell
```

```python
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

# Criar agente
agent = SupportAgent.objects.create(
    user=user,
    department='general'
)

print(f"Agente criado: {agent.employee_id}")
```

### 2. Acessar como Cliente

1. Faça login como cliente
2. Acesse: http://127.0.0.1:8000/support/
3. Clique em "Novo Ticket"
4. Preencha e envie

### 3. Acessar como Agente

1. Faça login com as credenciais do agente
2. Acesse: http://127.0.0.1:8000/support/agent/
3. Veja tickets não atribuídos
4. Clique em "Ver" e depois "Atribuir a Mim"
5. Responda ao cliente

---

## 📱 URLs Principais

### Cliente
- **Dashboard**: `/support/`
- **Criar Ticket**: `/support/create/`
- **Ver Ticket**: `/support/ticket/<id>/`

### Agente
- **Dashboard**: `/support/agent/`
- **Lista de Tickets**: `/support/agent/tickets/`
- **Estatísticas**: `/support/agent/statistics/`

### Base de Conhecimento
- **Artigos**: `/support/kb/`

---

## 🎯 Fluxo Típico

### Cliente
1. Cria ticket com problema
2. Aguarda resposta do suporte
3. Conversa via chat
4. Problema é resolvido
5. Avalia o atendimento

### Agente
1. Vê novo ticket no dashboard
2. Atribui ticket a si mesmo
3. Responde ao cliente via chat
4. Resolve o problema
5. Marca como resolvido

---

## 🔧 Comandos Úteis

### Criar Agente via Admin
```
http://127.0.0.1:8000/admin/services/supportagent/add/
```

### Ver Todos os Tickets
```
http://127.0.0.1:8000/admin/services/supportticket/
```

### Atualizar Estatísticas de um Agente
```python
from services.models import SupportAgent

agent = SupportAgent.objects.get(employee_id='SUP0001')
agent.update_statistics()
```

---

## 📊 Status dos Tickets

- **open**: Aberto (novo ticket)
- **in_progress**: Em Andamento (agente trabalhando)
- **waiting_customer**: Aguardando Cliente (agente respondeu)
- **waiting_support**: Aguardando Suporte (cliente respondeu)
- **resolved**: Resolvido (problema solucionado)
- **closed**: Fechado (cliente avaliou)

---

## 🎨 Tipos de Usuário

Para definir um usuário como agente de suporte:

1. **Automático**: Criar um `SupportAgent` (define automaticamente)
2. **Manual**: Editar `UserProfile` e definir `user_type='support'`

---

## 💡 Dicas

1. **Prioridades**: Use "Urgente" apenas para problemas críticos
2. **Categorias**: Escolha a categoria correta para melhor roteamento
3. **Anexos**: Sempre anexe screenshots quando possível
4. **Notas Internas**: Agentes podem criar notas que clientes não veem
5. **Base de Conhecimento**: Consulte antes de criar ticket

---

## 🐛 Problemas Comuns

### Agente não vê dashboard
**Solução**: Verificar se `user_type='support'` no UserProfile

### Ticket não aparece
**Solução**: Verificar filtros aplicados

### Não consegue enviar mensagem
**Solução**: Verificar se ticket está aberto

---

## 📞 Suporte

Para dúvidas, crie um ticket! 😄

---

**JobFinder - Sistema de Suporte**  
**Versão**: 1.0  
**Data**: Dezembro 2024
