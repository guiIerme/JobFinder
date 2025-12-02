# 🎧 Sistema de Suporte - JobFinder

> Sistema completo de suporte ao cliente com chat integrado

[![Status](https://img.shields.io/badge/status-completo-success)]()
[![Django](https://img.shields.io/badge/django-5.2-green)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()

---

## 📖 Sobre

Sistema de suporte desenvolvido para o JobFinder que permite comunicação direta entre clientes e equipe de suporte através de tickets com chat integrado.

---

## ✨ Funcionalidades

### 👤 Para Clientes
- ✅ Criar tickets de suporte
- ✅ Chat em tempo real com agentes
- ✅ Acompanhar status dos tickets
- ✅ Avaliar atendimento
- ✅ Consultar base de conhecimento

### 🎧 Para Agentes
- ✅ Dashboard com estatísticas
- ✅ Gerenciar múltiplos tickets
- ✅ Chat com clientes
- ✅ Notas internas
- ✅ Métricas de desempenho

### 📚 Base de Conhecimento
- ✅ Artigos organizados por categoria
- ✅ Busca por palavras-chave
- ✅ Avaliação de utilidade

---

## 🚀 Início Rápido

### 1. Criar Agente de Suporte

```bash
python create_support_agent.py
```

### 2. Acessar o Sistema

**Cliente**: http://127.0.0.1:8000/support/  
**Agente**: http://127.0.0.1:8000/support/agent/

### 3. Credenciais Padrão

```
Username: agente1
Senha: senha123
```

---

## 📁 Estrutura

```
projeto_integrador/
├── services/
│   ├── models.py              # Modelos do sistema
│   ├── support_views.py       # Views de suporte
│   ├── admin.py               # Configuração admin
│   └── urls.py                # URLs
├── templates/
│   └── services/
│       └── support/           # Templates de suporte
├── create_support_agent.py    # Script de criação
└── docs/                      # Documentação
    ├── SISTEMA_SUPORTE_IMPLEMENTADO.md
    ├── GUIA_RAPIDO_SUPORTE.md
    ├── RESUMO_SISTEMA_SUPORTE.md
    ├── EXEMPLOS_USO_SUPORTE.md
    └── APRESENTACAO_SISTEMA_SUPORTE.md
```

---

## 🗄️ Modelos

### SupportTicket
Gerencia tickets de suporte com status, prioridade e categoria.

### SupportMessage
Mensagens do chat entre cliente e agente.

### SupportAgent
Perfil dos agentes com estatísticas de desempenho.

### SupportKnowledgeBase
Artigos da base de conhecimento.

---

## 🌐 URLs

### Cliente
```
/support/                      # Dashboard
/support/create/               # Criar ticket
/support/ticket/<id>/          # Ver ticket
/support/ticket/<id>/rate/     # Avaliar
```

### Agente
```
/support/agent/                # Dashboard
/support/agent/tickets/        # Lista de tickets
/support/agent/statistics/     # Estatísticas
```

### Base de Conhecimento
```
/support/kb/                   # Lista de artigos
/support/kb/<slug>/            # Artigo específico
```

---

## 📊 Estatísticas

O sistema rastreia automaticamente:

- Total de tickets atendidos
- Avaliação média (1-5 ⭐)
- Tempo médio de resposta
- Tempo médio de resolução
- Taxa de satisfação

---

## 🔔 Notificações

Notificações automáticas para:

- ✅ Novo ticket criado
- ✅ Ticket atribuído
- ✅ Nova resposta recebida
- ✅ Ticket resolvido

---

## 🎨 Interface

### Chat
- Mensagens do cliente: Azul claro, à direita
- Mensagens do suporte: Branco, à esquerda
- Mensagens do sistema: Amarelo, centralizado

### Badges
- **Status**: Cores por status
- **Prioridade**: Vermelho (urgente), Amarelo (alta)
- **Categoria**: Azul info

---

## 📚 Documentação

### Guias Disponíveis

1. **LEIA_ME_PRIMEIRO.md** - Comece aqui!
2. **GUIA_RAPIDO_SUPORTE.md** - Uso rápido
3. **SISTEMA_SUPORTE_IMPLEMENTADO.md** - Detalhes técnicos
4. **EXEMPLOS_USO_SUPORTE.md** - Casos práticos
5. **APRESENTACAO_SISTEMA_SUPORTE.md** - Para apresentar
6. **CHECKLIST_SUPORTE.md** - Lista de verificação

---

## 🧪 Testes

### Testar como Cliente

1. Login como cliente
2. Acesse `/support/`
3. Crie um ticket
4. Aguarde resposta

### Testar como Agente

1. Login como agente
2. Acesse `/support/agent/`
3. Atribua ticket
4. Responda ao cliente

---

## 🔧 Configuração

### Criar Agente via Shell

```python
from django.contrib.auth.models import User
from services.models import SupportAgent

user = User.objects.create_user(
    username='agente1',
    password='senha123'
)

agent = SupportAgent.objects.create(user=user)
```

### Criar Agente via Admin

```
http://127.0.0.1:8000/admin/services/supportagent/add/
```

---

## 📈 Métricas

### Para Agentes
- Total de tickets
- Avaliação média
- Tempo de resposta
- Tempo de resolução

### Para Administradores
- Performance da equipe
- Tickets por categoria
- Satisfação geral
- Tendências

---

## 🛠️ Tecnologias

- **Backend**: Django 5.2
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite (pode migrar para PostgreSQL)
- **Notificações**: Sistema Django

---

## 🚀 Deploy

### Desenvolvimento

```bash
python manage.py runserver
```

### Produção

```bash
# Coletar arquivos estáticos
python manage.py collectstatic

# Executar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar com Gunicorn
gunicorn home_services.wsgi:application
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adicionar nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto faz parte do Projeto Integrador SENAC.

---

## 👥 Equipe

- Guilherme Beserra de Souza
- Felipe Costa da Silva
- Anna Júlia Pereira de Almeida
- Isabelle Victória Gonçalves Damasceno
- Mariana Júlia da Silva Lima
- Isaque Atila de Oliveira Santos

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte a documentação
2. Crie um ticket de suporte (use o próprio sistema! 😄)
3. Entre em contato com a equipe

---

## 🎯 Roadmap

### Próximas Melhorias

- [ ] WebSocket para chat em tempo real
- [ ] Notificações push
- [ ] Templates de resposta
- [ ] SLA com alertas
- [ ] Relatórios com gráficos
- [ ] Integração com email
- [ ] Chat bot com IA

---

## ⭐ Agradecimentos

Obrigado por usar o Sistema de Suporte JobFinder!

Se este sistema foi útil, considere dar uma ⭐ no repositório!

---

**Desenvolvido com ❤️ pela Equipe JobFinder**  
**SENAC DF - Projeto Integrador**  
**Dezembro 2024**
