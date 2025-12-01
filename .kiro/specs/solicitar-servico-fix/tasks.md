# Implementation Plan

- [x] 1. Diagnosticar modelo ServiceRequest e identificar problemas


  - Localizar arquivo do modelo ServiceRequest (models.py)
  - Verificar se campo `provider` existe no modelo
  - Verificar se campo `user` existe e está correto
  - Listar todos os campos atuais do modelo
  - Identificar campos faltantes comparando com design
  - _Requirements: 1.1, 1.2, 1.3_



- [ ] 2. Corrigir modelo ServiceRequest adicionando campos necessários
  - Adicionar campo `provider` (ForeignKey para User) se não existir
  - Adicionar `related_name='received_requests'` no campo provider
  - Adicionar `related_name='service_requests'` no campo user
  - Adicionar campos de agendamento se faltarem (preferred_date, preferred_time, address)
  - Adicionar campos de pagamento se faltarem (payment_method, payment_notes)
  - Adicionar campos de notificação (client_notified, provider_notified)



  - Adicionar Meta class com ordering e indexes
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Criar e executar migration para atualizar banco de dados


  - Executar `python manage.py makemigrations` para criar migration
  - Revisar arquivo de migration gerado
  - Executar `python manage.py migrate` para aplicar mudanças
  - Verificar no banco se campos foram adicionados corretamente
  - _Requirements: 1.1, 1.5_



- [ ] 4. Corrigir view solicitar_confirm para salvar dados corretamente
  - Localizar view `solicitar_confirm` em views.py
  - Implementar recuperação de dados da sessão
  - Identificar prestador através do serviço (service.user ou service.provider)
  - Criar objeto ServiceRequest com todos os campos obrigatórios
  - Associar corretamente user (cliente) e provider (prestador)
  - Adicionar captura de IP e logging detalhado
  - Implementar tratamento de erros com try/except

  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2_

- [ ] 5. Implementar sistema de notificações por email
  - Criar função `send_client_notification(service_request)`
  - Criar função `send_provider_notification(service_request)`
  - Implementar templates de email para cliente e prestador
  - Chamar funções de notificação após criar ServiceRequest
  - Atualizar flags client_notified e provider_notified


  - Adicionar tratamento de erro para falhas no envio
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Implementar view meus_pedidos para exibir solicitações do cliente
  - Criar ou corrigir view `meus_pedidos` em views.py
  - Implementar query: ServiceRequest.objects.filter(user=request.user)
  - Adicionar select_related para otimizar queries
  - Ordenar por data de criação (mais recentes primeiro)


  - Implementar filtros opcionais por status
  - Calcular contadores (total, pendentes, confirmadas)
  - Passar dados para template via context
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 7. Criar template meus_pedidos.html para exibir lista de solicitações
  - Criar arquivo `templates/services/meus_pedidos.html`
  - Implementar loop para exibir todas as solicitações
  - Exibir informações essenciais: serviço, prestador, data, status
  - Adicionar badges coloridos para status

  - Implementar link para ver detalhes de cada solicitação
  - Adicionar mensagem quando não houver solicitações
  - Garantir responsividade mobile
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 8. Implementar view painel_prestador para exibir solicitações recebidas
  - Criar ou corrigir view `painel_prestador` em views.py


  - Verificar se usuário é prestador
  - Implementar query: ServiceRequest.objects.filter(provider=request.user)
  - Adicionar select_related para otimizar queries
  - Implementar filtros por status (pendentes, confirmadas, etc)
  - Calcular contadores por status
  - Passar dados para template via context
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 9. Criar template painel_prestador.html para exibir solicitações
  - Criar arquivo `templates/services/painel_prestador.html`
  - Implementar abas para filtrar por status (Pendentes, Confirmadas)

  - Exibir dados completos do cliente (nome, telefone, endereço)
  - Exibir detalhes do agendamento (data, horário)
  - Adicionar botões Confirmar/Rejeitar para solicitações pendentes
  - Implementar layout responsivo


  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 10. Implementar views de ação do prestador (confirmar/rejeitar)
  - Criar view `confirmar_solicitacao(request, request_id)`
  - Criar view `rejeitar_solicitacao(request, request_id)`
  - Verificar permissões (apenas o prestador pode confirmar/rejeitar)
  - Atualizar status da solicitação

  - Enviar notificação ao cliente sobre a decisão
  - Redirecionar de volta ao painel com mensagem de sucesso
  - _Requirements: 3.5_

- [ ] 11. Adicionar URLs para todas as views criadas
  - Adicionar URL para `meus_pedidos`
  - Adicionar URL para `painel_prestador`
  - Adicionar URL para `confirmar_solicitacao`




  - Adicionar URL para `rejeitar_solicitacao`
  - Adicionar URL para `detalhes_solicitacao` (se necessário)
  - Verificar se URL `solicitar_confirm` existe
  - _Requirements: 2.1, 3.1_

- [ ] 12. Adicionar logging detalhado em todas as operações críticas
  - Configurar logger no início do arquivo views.py
  - Adicionar log ao criar ServiceRequest
  - Adicionar log ao enviar notificações
  - Adicionar log de erro com stack trace em exceções
  - Adicionar log ao confirmar/rejeitar solicitações
  - Incluir informações relevantes (user_id, request_id, etc)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 13. Testar fluxo completo de solicitação e exibição
  - Fazer solicitação de serviço como cliente
  - Verificar no banco se ServiceRequest foi criado
  - Verificar se campos user e provider estão corretos
  - Acessar "Meus Pedidos" e verificar se solicitação aparece
  - Fazer login como prestador e verificar painel
  - Verificar se solicitação aparece no painel do prestador
  - Testar confirmação e rejeição de solicitações
  - Verificar recebimento de emails
  - _Requirements: 1.1, 2.1, 3.1, 4.1_