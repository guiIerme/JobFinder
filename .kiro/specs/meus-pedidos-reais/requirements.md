# Requirements Document

## Introduction

Este documento define os requisitos para implementar a funcionalidade de exibição de pedidos reais na tela "Meus Pedidos", substituindo os dados estáticos atualmente exibidos por dados dinâmicos provenientes do banco de dados. A funcionalidade permitirá que clientes visualizem suas solicitações de serviço reais com informações precisas e atualizadas.

## Glossary

- **Sistema**: A aplicação web Job Finder
- **Cliente**: Usuário que solicita serviços através da plataforma
- **Solicitação**: Registro de ServiceRequestModal no banco de dados representando um pedido de serviço
- **Tela de Pedidos**: Interface localizada em `/meus-pedidos` que exibe as solicitações do cliente
- **View**: Função Python no Django que processa requisições HTTP e retorna respostas
- **Template**: Arquivo HTML que renderiza a interface do usuário
- **Estatísticas**: Contadores que mostram total, pendentes, agendadas e concluídas

## Requirements

### Requirement 1

**User Story:** Como um cliente, eu quero visualizar minhas solicitações de serviço reais na tela "Meus Pedidos", para que eu possa acompanhar o status dos serviços que solicitei.

#### Acceptance Criteria

1. WHEN o Cliente acessa a URL `/meus-pedidos`, THE Sistema SHALL recuperar todas as solicitações do modelo ServiceRequestModal associadas ao usuário autenticado
2. WHEN o Sistema recupera as solicitações, THE Sistema SHALL ordenar as solicitações por data de criação em ordem decrescente
3. THE Sistema SHALL exibir cada solicitação com as seguintes informações: nome do serviço, status, prestador, data preferencial, endereço e método de pagamento
4. IF o Cliente não possui solicitações no banco de dados, THEN THE Sistema SHALL exibir uma mensagem informativa indicando que não há solicitações
5. THE Sistema SHALL garantir que apenas solicitações do usuário autenticado sejam exibidas

### Requirement 2

**User Story:** Como um cliente, eu quero ver estatísticas atualizadas dos meus pedidos, para que eu possa ter uma visão geral rápida do status das minhas solicitações.

#### Acceptance Criteria

1. THE Sistema SHALL calcular e exibir o número total de solicitações do cliente
2. THE Sistema SHALL calcular e exibir o número de solicitações com status "pending" (pendentes)
3. THE Sistema SHALL calcular e exibir o número de solicitações com status "scheduled" (agendadas)
4. THE Sistema SHALL calcular e exibir o número de solicitações com status "completed" (concluídas)
5. WHEN as estatísticas são calculadas, THE Sistema SHALL considerar apenas as solicitações do usuário autenticado

### Requirement 3

**User Story:** Como um cliente, eu quero filtrar minhas solicitações por status, para que eu possa visualizar apenas os pedidos em um estado específico.

#### Acceptance Criteria

1. WHEN o Cliente clica em um botão de filtro de status, THE Sistema SHALL exibir apenas as solicitações que correspondem ao status selecionado
2. THE Sistema SHALL suportar filtros para os seguintes status: todos, pending, scheduled, completed e cancelled
3. WHEN um filtro é aplicado, THE Sistema SHALL manter o filtro ativo visualmente através de estilo diferenciado no botão
4. THE Sistema SHALL preservar o filtro selecionado através de parâmetros de URL
5. WHEN o filtro "Todos" é selecionado, THE Sistema SHALL exibir todas as solicitações sem restrição de status

### Requirement 4

**User Story:** Como um cliente, eu quero que a view de "Meus Pedidos" seja criada ou atualizada corretamente, para que os dados sejam carregados do banco de dados e não de dados estáticos.

#### Acceptance Criteria

1. THE Sistema SHALL implementar ou atualizar a view `meus_pedidos` no arquivo `services/views.py`
2. THE Sistema SHALL configurar a rota URL para `/meus-pedidos` apontando para a view correta
3. WHEN a view é executada, THE Sistema SHALL consultar o banco de dados usando o modelo ServiceRequestModal
4. THE Sistema SHALL passar os dados das solicitações e estatísticas para o template através do contexto
5. THE Sistema SHALL aplicar o decorador `@login_required` para garantir que apenas usuários autenticados acessem a página

### Requirement 5

**User Story:** Como um cliente, eu quero que o template exiba corretamente as informações das minhas solicitações reais, para que eu possa ver dados precisos e atualizados.

#### Acceptance Criteria

1. THE Sistema SHALL remover quaisquer dados estáticos ou mockados do template `meus_pedidos.html`
2. THE Sistema SHALL utilizar os dados do contexto fornecido pela view para renderizar as solicitações
3. WHEN uma solicitação não possui prestador atribuído, THE Sistema SHALL exibir "Não atribuído"
4. THE Sistema SHALL formatar datas usando o filtro de template apropriado no formato "dd/mm/YYYY"
5. THE Sistema SHALL exibir badges de status com cores apropriadas baseadas no status da solicitação
