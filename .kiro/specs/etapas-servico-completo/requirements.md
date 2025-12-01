# Requirements Document

## Introduction

Este documento define os requisitos para implementar um fluxo completo de solicitação de serviços com múltiplas etapas: solicitação inicial, agendamento, pagamento e acompanhamento. O sistema deve guiar o usuário através de um processo estruturado que garanta todas as informações necessárias sejam coletadas de forma organizada e intuitiva.

## Glossary

- **Sistema**: Plataforma web Job Finder para conectar clientes e prestadores de serviços
- **Fluxo_Multietapas**: Processo sequencial de solicitação dividido em etapas distintas
- **Usuario_Cliente**: Usuário que solicita serviços através da plataforma
- **Prestador_Servico**: Profissional que oferece serviços através da plataforma
- **Etapa_Solicitacao**: Primeira etapa onde são definidos serviço e dados básicos
- **Etapa_Agendamento**: Segunda etapa para definir data, horário e endereço
- **Etapa_Pagamento**: Terceira etapa para escolher método de pagamento
- **Etapa_Confirmacao**: Etapa final com resumo e confirmação do pedido
- **Status_Solicitacao**: Estado atual da solicitação no sistema

## Requirements

### Requirement 1

**User Story:** Como um usuário, eu quero um fluxo de solicitação dividido em etapas claras, para que eu possa fornecer informações de forma organizada e não me sentir sobrecarregado.

#### Acceptance Criteria

1. THE Sistema SHALL apresentar fluxo de solicitação dividido em 4 etapas distintas: Solicitação, Agendamento, Pagamento, Confirmação
2. THE Sistema SHALL exibir indicador visual de progresso mostrando etapa atual e etapas restantes
3. THE Sistema SHALL permitir navegação entre etapas já preenchidas através do indicador de progresso
4. WHEN Usuario_Cliente completa uma etapa, THE Sistema SHALL validar dados obrigatórios antes de prosseguir
5. THE Sistema SHALL salvar progresso automaticamente em cada etapa para evitar perda de dados

### Requirement 2

**User Story:** Como um usuário, eu quero definir detalhes do serviço na primeira etapa, para que o prestador tenha todas as informações necessárias sobre o que preciso.

#### Acceptance Criteria

1. THE Sistema SHALL exibir informações do serviço selecionado na Etapa_Solicitacao
2. THE Sistema SHALL permitir adicionar observações específicas sobre o serviço
3. THE Sistema SHALL permitir upload de fotos relacionadas ao serviço
4. THE Sistema SHALL validar que todos os campos obrigatórios estejam preenchidos
5. WHEN dados estão válidos, THE Sistema SHALL habilitar botão "Próxima Etapa"

### Requirement 3

**User Story:** Como um usuário, eu quero agendar data e horário na segunda etapa, para que o prestador saiba quando e onde realizar o serviço.

#### Acceptance Criteria

1. THE Sistema SHALL exibir calendário para seleção de data preferida
2. THE Sistema SHALL oferecer opções de horário baseadas na disponibilidade
3. THE Sistema SHALL capturar endereço completo para realização do serviço
4. THE Sistema SHALL validar CEP e preencher dados automaticamente quando possível
5. THE Sistema SHALL permitir adicionar observações sobre acesso ao local

### Requirement 4

**User Story:** Como um usuário, eu quero escolher método de pagamento na terceira etapa, para que o prestador saiba como será remunerado pelo serviço.

#### Acceptance Criteria

1. THE Sistema SHALL oferecer múltiplas opções de pagamento: dinheiro, cartão, PIX, transferência
2. WHEN Usuario_Cliente seleciona cartão, THE Sistema SHALL capturar preferências de débito/crédito
3. WHEN Usuario_Cliente seleciona dinheiro, THE Sistema SHALL perguntar se precisa de troco
4. WHEN Usuario_Cliente seleciona PIX, THE Sistema SHALL capturar chave PIX se necessário
5. THE Sistema SHALL calcular e exibir valor total estimado do serviço

### Requirement 5

**User Story:** Como um usuário, eu quero revisar todos os dados na etapa final, para que eu possa confirmar que tudo está correto antes de enviar a solicitação.

#### Acceptance Criteria

1. THE Sistema SHALL exibir resumo completo de todas as informações fornecidas
2. THE Sistema SHALL permitir editar qualquer etapa clicando em "Editar"
3. THE Sistema SHALL exibir termos de uso e política de privacidade para aceite
4. WHEN Usuario_Cliente confirma solicitação, THE Sistema SHALL criar registro no banco de dados
5. THE Sistema SHALL enviar notificações por email para cliente e prestador

### Requirement 6

**User Story:** Como um prestador de serviços, eu quero receber solicitações organizadas com todas as informações, para que eu possa avaliar e responder adequadamente.

#### Acceptance Criteria

1. THE Sistema SHALL criar notificação para Prestador_Servico quando solicitação for enviada
2. THE Sistema SHALL exibir todas as informações da solicitação de forma organizada
3. THE Sistema SHALL permitir que prestador aceite, recuse ou negocie a solicitação
4. WHEN prestador responde, THE Sistema SHALL notificar Usuario_Cliente
5. THE Sistema SHALL atualizar Status_Solicitacao conforme interações

### Requirement 7

**User Story:** Como um usuário, eu quero acompanhar o status da minha solicitação, para que eu saiba o andamento do processo.

#### Acceptance Criteria

1. THE Sistema SHALL exibir status atual da solicitação em tempo real
2. THE Sistema SHALL mostrar histórico de todas as interações e mudanças de status
3. THE Sistema SHALL enviar notificações automáticas sobre mudanças de status
4. THE Sistema SHALL permitir comunicação direta entre cliente e prestador
5. THE Sistema SHALL oferecer opção de cancelamento quando apropriado

### Requirement 8

**User Story:** Como um usuário, eu quero iniciar o processo de solicitação de serviço de forma intuitiva, para que eu possa facilmente encontrar e solicitar o serviço que preciso.

#### Acceptance Criteria

1. THE Sistema SHALL exibir botão "Solicitar Serviço" claramente visível na página do prestador
2. WHEN Usuario_Cliente clica em "Solicitar Serviço", THE Sistema SHALL iniciar Fluxo_Multietapas
3. THE Sistema SHALL exibir informações básicas do prestador e serviço selecionado
4. THE Sistema SHALL verificar se usuário está autenticado antes de iniciar solicitação
5. WHEN usuário não está autenticado, THE Sistema SHALL redirecionar para login/cadastro

### Requirement 9

**User Story:** Como um usuário, eu quero navegar facilmente entre as etapas do processo, para que eu possa revisar e corrigir informações quando necessário.

#### Acceptance Criteria

1. THE Sistema SHALL exibir botões "Voltar" e "Próximo" em todas as etapas
2. THE Sistema SHALL permitir acesso direto a etapas já preenchidas através do indicador de progresso
3. THE Sistema SHALL manter dados preenchidos ao navegar entre etapas
4. THE Sistema SHALL destacar visualmente campos com erros de validação
5. THE Sistema SHALL exibir mensagens de erro claras quando validação falhar

### Requirement 10

**User Story:** Como um usuário, eu quero que o sistema seja responsivo e funcione bem em dispositivos móveis, para que eu possa solicitar serviços de qualquer lugar.

#### Acceptance Criteria

1. THE Sistema SHALL adaptar interface para telas de smartphones e tablets
2. THE Sistema SHALL manter funcionalidade completa em dispositivos móveis
3. THE Sistema SHALL otimizar carregamento para conexões mais lentas
4. THE Sistema SHALL permitir upload de fotos através da câmera do dispositivo
5. THE Sistema SHALL manter dados salvos mesmo com perda de conexão temporária