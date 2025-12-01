# Requirements Document

## Introduction

Este documento define os requisitos para corrigir o fluxo completo de solicitação de serviços no sistema Job Finder. O problema crítico identificado é que quando um cliente solicita um serviço, o agendamento não aparece em "Meus Pedidos" para o cliente e também não aparece no painel do prestador de serviços. Esta correção deve garantir que todas as solicitações sejam salvas corretamente no banco de dados e exibidas nas interfaces apropriadas.

## Glossary

- **Sistema**: Plataforma web Job Finder para conectar clientes e prestadores de serviços
- **Cliente**: Usuário que solicita serviços através da plataforma
- **Prestador_Servico**: Profissional que oferece serviços através da plataforma
- **Solicitacao_Servico**: Registro de pedido de serviço criado pelo cliente no banco de dados
- **Painel_Cliente**: Interface onde o cliente visualiza seus pedidos em "Meus Pedidos"
- **Painel_Prestador**: Interface onde o prestador visualiza solicitações recebidas
- **ServiceRequest**: Modelo Django que armazena dados de solicitações de serviço

## Requirements

### Requirement 1

**User Story:** Como um cliente, eu quero que minhas solicitações de serviço sejam salvas corretamente no banco de dados, para que eu possa acompanhá-las posteriormente.

#### Acceptance Criteria

1. WHEN Cliente submete formulário de solicitação, THE Sistema SHALL criar registro ServiceRequest no banco de dados
2. THE Sistema SHALL associar ServiceRequest ao usuário autenticado (Cliente)
3. THE Sistema SHALL associar ServiceRequest ao prestador de serviço correto
4. THE Sistema SHALL armazenar todos os dados do formulário: nome, telefone, email, descrição, data, horário, endereço, método de pagamento
5. THE Sistema SHALL definir status inicial como "pending" para novas solicitações

### Requirement 2

**User Story:** Como um cliente, eu quero visualizar todas as minhas solicitações de serviço em "Meus Pedidos", para que eu possa acompanhar o status de cada uma.

#### Acceptance Criteria

1. WHEN Cliente acessa página "Meus Pedidos", THE Sistema SHALL exibir todas as solicitações criadas por ele
2. THE Sistema SHALL ordenar solicitações por data de criação (mais recentes primeiro)
3. THE Sistema SHALL exibir informações essenciais: nome do serviço, prestador, data, horário, status
4. WHEN Cliente clica em uma solicitação, THE Sistema SHALL exibir detalhes completos
5. THE Sistema SHALL permitir que Cliente cancele solicitações com status "pending"

### Requirement 3

**User Story:** Como um prestador de serviços, eu quero visualizar todas as solicitações recebidas no meu painel, para que eu possa gerenciar meus agendamentos.

#### Acceptance Criteria

1. WHEN Prestador_Servico acessa seu painel, THE Sistema SHALL exibir todas as solicitações direcionadas a ele
2. THE Sistema SHALL filtrar solicitações por status: pendentes, confirmadas, em andamento, concluídas
3. THE Sistema SHALL exibir dados do cliente: nome, telefone, endereço, data e horário solicitados
4. THE Sistema SHALL permitir que Prestador_Servico confirme ou rejeite solicitações pendentes
5. THE Sistema SHALL atualizar status da solicitação quando Prestador_Servico tomar ação

### Requirement 4

**User Story:** Como um cliente, eu quero receber notificações quando minha solicitação for processada, para que eu saiba que o prestador foi informado.

#### Acceptance Criteria

1. WHEN Solicitacao_Servico é criada com sucesso, THE Sistema SHALL enviar email de confirmação ao Cliente
2. THE Sistema SHALL enviar notificação ao Prestador_Servico informando nova solicitação
3. WHEN Prestador_Servico confirma solicitação, THE Sistema SHALL notificar Cliente
4. WHEN Prestador_Servico rejeita solicitação, THE Sistema SHALL notificar Cliente com motivo
5. THE Sistema SHALL registrar todas as notificações enviadas no banco de dados

### Requirement 5

**User Story:** Como desenvolvedor, eu quero que o sistema tenha logs detalhados de todas as solicitações, para que eu possa diagnosticar problemas rapidamente.

#### Acceptance Criteria

1. WHEN Cliente submete solicitação, THE Sistema SHALL registrar log com dados completos
2. WHEN ocorre erro no processamento, THE Sistema SHALL registrar log com stack trace
3. THE Sistema SHALL registrar IP e user agent do Cliente em cada solicitação
4. THE Sistema SHALL registrar timestamp de cada etapa do processo
5. THE Sistema SHALL permitir consulta de logs por usuário, prestador ou período