# Contribuindo para o Job Finder

Primeiramente, obrigado por considerar contribuir para o Job Finder! 🎉

## Bem-vindo!

Estamos felizes em ter você interessado em contribuir para o Job Finder. Este documento irá guiá-lo através do processo de contribuição e explicar nossas práticas e padrões.

O Job Finder é uma plataforma de serviços domésticos que conecta clientes a profissionais qualificados. Nossa missão é criar uma experiência excepcional para todos os usuários, e sua contribuição é fundamental para isso.

## Código de Conduta

Ao contribuir para este projeto, você concorda em seguir nosso Código de Conduta, que promove um ambiente acolhedor e respeitoso para todos os participantes.

### Nossos Padrões

Exemplos de comportamento que contribuem para criar um ambiente positivo:

- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista e experiências
- Aceitar críticas construtivas com elegância
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

Exemplos de comportamento inaceitável:

- Uso de linguagem ou imagens sexualizadas
- Comentários depreciativos, ataques pessoais ou políticos
- Assédio público ou privado
- Publicação de informações privadas de terceiros sem permissão
- Outras condutas que seriam consideradas inadequadas em um ambiente profissional

## Como Contribuir

### Reportando Bugs

Antes de reportar um bug, por favor verifique se ele já não foi reportado na seção de issues.

Ao reportar um bug, inclua:

1. **Versão da aplicação** - Qual versão você está usando
2. **Ambiente** - Sistema operacional, versão do Python, etc.
3. **Passos para reproduzir** - Passos claros para reproduzir o problema
4. **Comportamento esperado** - O que você esperava que acontecesse
5. **Comportamento atual** - O que realmente aconteceu
6. **Screenshots** - Se relevante, adicione screenshots
7. **Logs** - Se disponível, inclua logs de erro relevantes

### Sugerindo Funcionalidades

Nós adoramos novas ideias! Para sugerir uma funcionalidade:

1. Verifique se a funcionalidade já não foi sugerida
2. Descreva claramente a funcionalidade
3. Explique o problema que ela resolve
4. Forneça exemplos de uso
5. Explique como isso beneficiaria os usuários
6. Liste eventuais alternativas consideradas

### Contribuindo com Código

#### 1. Fork o Repositório

Crie um fork do repositório e clone para sua máquina local.

#### 2. Crie uma Branch

```bash
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b bugfix/nome-do-bug
```

#### 3. Siga as Convenções de Código

- Siga o PEP 8 para Python
- Use nomes de variáveis e funções descritivos
- Adicione docstrings para funções e classes
- Escreva comentários quando necessário
- Mantenha funções pequenas e focadas
- Prefira composição sobre herança

#### 4. Escreva Testes

- Adicione testes para novas funcionalidades
- Certifique-se de que todos os testes passam
- Mantenha uma cobertura de testes adequada
- Use nomes de testes descritivos
- Teste casos de borda e erros

#### 5. Commits

Siga o padrão de commits:

```
tipo(escopo): descrição concisa

Corpo da mensagem (opcional)

Resolves: #123
```

Tipos:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, ponto e vírgula faltando, etc.
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Atualizações de build, tarefas administrativas

#### 6. Pull Request

1. Atualize sua branch com a main
2. Rode todos os testes
3. Crie o Pull Request
4. Descreva claramente as mudanças
5. Referencie issues relacionadas
6. Inclua screenshots se relevante para UI
7. Espere pela revisão e responda aos comentários

## Estrutura do Projeto

```
Pi_mobile/
├── docs/                 # Documentação
├── home_services/        # Configurações do Django
├── services/             # Aplicação principal
│   ├── migrations/       # Migrações do banco de dados
│   ├── templates/        # Templates HTML
│   ├── static/           # Arquivos estáticos
│   ├── models.py         # Modelos do banco de dados
│   ├── views.py          # Views/controllers
│   ├── urls.py           # Rotas
│   ├── tests.py          # Testes
│   ├── chat_views.py     # Views específicas para chat
│   ├── payment.py        # Processamento de pagamentos
│   ├── content_generator.py # Geração de conteúdo com IA
│   ├── personalization.py   # Motor de personalização
│   ├── ml_analytics.py   # Análise de dados com machine learning
│   ├── notifications.py  # Sistema de notificações
│   ├── health.py         # Monitoramento de saúde do sistema
│   ├── management/       # Comandos de gerenciamento personalizados
│   └── ...
├── templates/            # Templates globais
├── static/               # Arquivos estáticos globais
└── manage.py             # Script de gerenciamento
```

## Ambiente de Desenvolvimento

### Configuração Inicial

1. Clone o repositório
2. Crie um ambiente virtual
3. Instale as dependências
4. Configure o banco de dados
5. Rode as migrações
6. Configure variáveis de ambiente

### Rodando Testes

```bash
python manage.py test
```

#### Rodando Testes Específicos

```bash
# Testar apenas a aplicação services
python manage.py test services

# Testar modelos específicos
python manage.py test services.tests.ModelTests

# Testar views específicas
python manage.py test services.tests.ViewTests
```

### Rodando o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

### Comandos de Gerenciamento Úteis

```bash
# Popular dados de exemplo
python manage.py populate_data

# Processar análises de IA
python manage.py process_ai_analytics

# Gerar pedidos de exemplo
python manage.py generate_sample_orders --number 20

# Limpar mensagens de chat antigas
python manage.py cleanup_chat_messages --days 60
```

## Padrões de Código

### Python

- Siga o PEP 8
- Use type hints quando possível
- Mantenha funções pequenas e focadas
- Prefira composição sobre herança
- Use docstrings para todas as funções, classes e módulos
- Trate exceções apropriadamente
- Use constantes para valores mágicos

### Django

- Use Class-Based Views quando apropriado
- Siga as convenções de nomenclatura do Django
- Use o sistema de mensagens para feedback ao usuário
- Implemente autenticação e autorização corretamente
- Use migrations para alterações no banco de dados
- Valide dados de entrada
- Proteja contra CSRF e XSS

### HTML/CSS/JavaScript

- Siga as convenções do Bootstrap 5
- Use classes semânticas
- Mantenha o JavaScript não-obstrusivo
- Otimize para performance
- Use atributos ARIA para acessibilidade
- Valide formulários no cliente e servidor
- Trate erros de forma elegante

## Processo de Revisão

1. Todos os PRs precisam de revisão
2. Pelo menos um mantenedor precisa aprovar
3. Todos os testes devem passar
4. O código deve seguir os padrões estabelecidos
5. A documentação deve ser atualizada conforme necessário
6. O código deve ser testado em múltiplos navegadores/dispositivos
7. A performance não deve ser degradada
8. A segurança deve ser verificada

## Comunicação

- Use issues para discussões gerais
- Use PR comments para feedback específico de código
- Seja respeitoso e construtivo
- Ajude outros contribuidores
- Responda a comentários em PRs em até 48 horas
- Seja claro e objetivo nas discussões
- Use o português ou inglês de forma consistente

## Recursos Úteis

- [Documentação do Django](https://docs.djangoproject.com/)
- [PEP 8 - Guia de Estilo Python](https://pep8.org/)
- [Git Book](https://git-scm.com/book/en/v2)

## Agradecimentos

Contribuidores são reconhecidos no arquivo AUTHORS e através do GitHub.

Obrigado novamente por contribuir! 🚀