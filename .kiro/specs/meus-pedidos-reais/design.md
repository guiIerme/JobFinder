# Design Document

## Overview

Este documento descreve o design técnico para implementar a funcionalidade de exibição de pedidos reais na tela "Meus Pedidos". A implementação envolve a verificação e possível ajuste da view Django existente `meus_pedidos`, garantindo que ela consulte corretamente o banco de dados através do modelo `ServiceRequestModal`, e a remoção de quaisquer dados estáticos do template HTML.

A análise do código existente revela que:
- A view `meus_pedidos` já está implementada em `services/views.py` (linha 6425)
- A rota URL `/meus-pedidos/` já está configurada em `services/urls.py`
- O template `templates/services/meus_pedidos.html` já existe e está estruturado corretamente
- A view atual já consulta o modelo `ServiceRequestModal` e implementa filtros por status

Portanto, o foco principal será **validar** que a implementação existente está funcionando corretamente e **remover quaisquer dados mockados ou estáticos** que possam estar sendo usados no template ou na view.

## Architecture

### Componentes Envolvidos

```
┌─────────────────┐
│   Cliente       │
│   (Browser)     │
└────────┬────────┘
         │ HTTP GET /meus-pedidos/
         ▼
┌─────────────────────────────────┐
│   Django URL Router             │
│   (services/urls.py)            │
└────────┬────────────────────────┘
         │ routes to
         ▼
┌─────────────────────────────────┐
│   View: meus_pedidos            │
│   (services/views.py)           │
│   - Autentica usuário           │
│   - Consulta ServiceRequestModal│
│   - Aplica filtros              │
│   - Calcula estatísticas        │
└────────┬────────────────────────┘
         │ queries
         ▼
┌─────────────────────────────────┐
│   Model: ServiceRequestModal    │
│   (services/models.py)          │
│   - Dados de solicitações       │
└────────┬────────────────────────┘
         │ returns QuerySet
         ▼
┌─────────────────────────────────┐
│   Template: meus_pedidos.html   │
│   (templates/services/)         │
│   - Renderiza solicitações      │
│   - Exibe estatísticas          │
│   - Botões de filtro            │
└─────────────────────────────────┘
```

### Fluxo de Dados

1. **Requisição**: Cliente acessa `/meus-pedidos/` (opcionalmente com `?status=pending`)
2. **Autenticação**: Decorator `@login_required` valida autenticação
3. **Consulta ao Banco**: View consulta `ServiceRequestModal.objects.filter(user=request.user)`
4. **Filtros**: Aplica filtro de status se fornecido via query parameter
5. **Estatísticas**: Calcula contadores (total, pendentes, agendadas, concluídas)
6. **Contexto**: Prepara dicionário de contexto com dados
7. **Renderização**: Template renderiza HTML com dados do contexto
8. **Resposta**: HTML é retornado ao cliente

## Components and Interfaces

### 1. View: `meus_pedidos`

**Localização**: `services/views.py` (linha ~6425)

**Responsabilidades**:
- Autenticar o usuário (via decorator `@login_required`)
- Consultar solicitações do usuário no banco de dados
- Aplicar filtros de status quando fornecidos
- Calcular estatísticas (total, pendentes, agendadas, concluídas)
- Preparar contexto para o template
- Renderizar o template com os dados

**Implementação Atual**:
```python
@login_required
def meus_pedidos(request):
    """Página Meus Pedidos - exibe todas as solicitações do cliente"""
    from .models import ServiceRequestModal
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"meus_pedidos acessado por user={request.user.id}")
    
    # Filtrar solicitações do usuário logado (cliente)
    solicitacoes = ServiceRequestModal.objects.filter(
        user=request.user
    ).select_related('provider', 'service').order_by('-created_at')
    
    # Filtros opcionais por status
    status_filter = request.GET.get('status')
    if status_filter:
        solicitacoes = solicitacoes.filter(status=status_filter)
        logger.info(f"Filtro aplicado: status={status_filter}")
    
    # Contadores
    total = solicitacoes.count()
    pendentes = ServiceRequestModal.objects.filter(user=request.user, status='pending').count()
    agendadas = ServiceRequestModal.objects.filter(user=request.user, status='scheduled').count()
    concluidas = ServiceRequestModal.objects.filter(user=request.user, status='completed').count()
    
    logger.info(f"Solicitações encontradas: total={total}, pendentes={pendentes}")
    
    context = {
        'solicitacoes': solicitacoes,
        'total': total,
        'pendentes': pendentes,
        'agendadas': agendadas,
        'concluidas': concluidas,
        'status_filter': status_filter,
    }
    
    return render(request, 'services/meus_pedidos.html', context)
```

**Análise**:
- ✅ Já implementada corretamente
- ✅ Usa `@login_required` para autenticação
- ✅ Consulta o banco de dados via `ServiceRequestModal`
- ✅ Implementa filtros por status
- ✅ Calcula estatísticas corretamente
- ⚠️ Possível otimização: os contadores fazem queries separadas (pode ser otimizado com agregação)

**Melhorias Sugeridas**:
```python
from django.db.models import Count, Q

# Otimizar contadores com uma única query
stats = ServiceRequestModal.objects.filter(user=request.user).aggregate(
    total=Count('id'),
    pendentes=Count('id', filter=Q(status='pending')),
    agendadas=Count('id', filter=Q(status='scheduled')),
    concluidas=Count('id', filter=Q(status='completed'))
)
```

### 2. Model: `ServiceRequestModal`

**Localização**: `services/models.py`

**Campos Relevantes**:
- `user`: ForeignKey para User (cliente que fez a solicitação)
- `provider`: ForeignKey para User (prestador atribuído)
- `service`: ForeignKey para CustomService
- `service_name`: CharField (nome do serviço)
- `service_description`: TextField
- `status`: CharField com choices (pending, contacted, scheduled, completed, cancelled)
- `preferred_date`: DateField
- `preferred_time`: TimeField
- `preferred_period`: CharField (manha, tarde, flexivel)
- `address_*`: Campos de endereço
- `payment_method`: CharField
- `created_at`: DateTimeField
- `updated_at`: DateTimeField

**Métodos Relevantes**:
- `get_status_display()`: Retorna o label legível do status
- `get_payment_method_display()`: Retorna o label legível do método de pagamento
- `get_preferred_period_display()`: Retorna o label legível do período preferencial

### 3. Template: `meus_pedidos.html`

**Localização**: `templates/services/meus_pedidos.html`

**Estrutura Atual**:
- Seção de estatísticas (cards com total, pendentes, agendadas, concluídas)
- Botões de filtro por status
- Lista de solicitações com informações detalhadas
- Mensagem quando não há solicitações

**Análise**:
- ✅ Template já está estruturado para receber dados dinâmicos
- ✅ Usa variáveis de contexto corretamente (`{{ solicitacoes }}`, `{{ total }}`, etc.)
- ✅ Implementa loops `{% for solicitacao in solicitacoes %}`
- ✅ Usa filtros de template para formatação de datas
- ⚠️ Precisa verificar se não há dados mockados/estáticos

**Verificações Necessárias**:
1. Confirmar que não há dados hardcoded no template
2. Verificar se todas as variáveis vêm do contexto
3. Garantir que os filtros de template estão corretos

### 4. URL Configuration

**Localização**: `services/urls.py`

**Rota Atual**:
```python
path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
```

**Análise**:
- ✅ Rota já configurada corretamente
- ✅ Nome da URL é `meus_pedidos`
- ✅ Aponta para a view correta

## Data Models

### ServiceRequestModal

O modelo `ServiceRequestModal` é a entidade central para armazenar solicitações de serviço. Abaixo está a estrutura relevante:

```python
class ServiceRequestModal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('contacted', 'Contatado'),
        ('scheduled', 'Agendado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Relacionamentos
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modal_service_requests')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_service_requests', null=True, blank=True)
    service = models.ForeignKey('CustomService', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dados do serviço
    service_name = models.CharField(max_length=200)
    service_description = models.TextField()
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dados de contato
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    
    # Dados de endereço
    address_street = models.CharField(max_length=200, blank=True)
    address_number = models.CharField(max_length=10, blank=True)
    address_neighborhood = models.CharField(max_length=100, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    
    # Dados de agendamento
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    preferred_period = models.CharField(max_length=20, blank=True, choices=[...])
    
    # Dados de pagamento
    payment_method = models.CharField(max_length=20, blank=True, choices=[...])
    
    # Status e datas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Query Patterns

**Consulta Principal**:
```python
ServiceRequestModal.objects.filter(user=request.user).select_related('provider', 'service').order_by('-created_at')
```

**Otimização com select_related**:
- `select_related('provider', 'service')` reduz queries N+1 ao buscar dados relacionados

**Filtros**:
```python
# Por status
.filter(status='pending')

# Por usuário
.filter(user=request.user)

# Combinado
.filter(user=request.user, status='pending')
```

**Agregações para Estatísticas**:
```python
from django.db.models import Count, Q

ServiceRequestModal.objects.filter(user=request.user).aggregate(
    total=Count('id'),
    pendentes=Count('id', filter=Q(status='pending')),
    agendadas=Count('id', filter=Q(status='scheduled')),
    concluidas=Count('id', filter=Q(status='completed'))
)
```

## Error Handling

### Cenários de Erro

1. **Usuário não autenticado**
   - **Tratamento**: Decorator `@login_required` redireciona para página de login
   - **Resposta**: HTTP 302 Redirect para `/login/?next=/meus-pedidos/`

2. **Nenhuma solicitação encontrada**
   - **Tratamento**: Template exibe mensagem amigável
   - **Resposta**: HTML com mensagem "Nenhuma solicitação encontrada"

3. **Erro ao consultar banco de dados**
   - **Tratamento**: Django levanta exceção, middleware de erro captura
   - **Resposta**: Página de erro 500 (se DEBUG=False) ou traceback (se DEBUG=True)
   - **Melhoria**: Adicionar try-except na view para tratamento gracioso

4. **Filtro de status inválido**
   - **Tratamento Atual**: Query retorna vazio se status não existe
   - **Melhoria**: Validar status contra STATUS_CHOICES

5. **Provider não atribuído (null)**
   - **Tratamento**: Template verifica `{% if solicitacao.provider %}`
   - **Resposta**: Exibe "Não atribuído"

### Implementação de Error Handling

```python
@login_required
def meus_pedidos(request):
    try:
        # Validar filtro de status
        status_filter = request.GET.get('status')
        valid_statuses = ['pending', 'contacted', 'scheduled', 'completed', 'cancelled']
        
        if status_filter and status_filter not in valid_statuses:
            messages.warning(request, f'Status inválido: {status_filter}')
            status_filter = None
        
        # Consultar solicitações
        solicitacoes = ServiceRequestModal.objects.filter(
            user=request.user
        ).select_related('provider', 'service').order_by('-created_at')
        
        if status_filter:
            solicitacoes = solicitacoes.filter(status=status_filter)
        
        # Calcular estatísticas
        stats = ServiceRequestModal.objects.filter(user=request.user).aggregate(
            total=Count('id'),
            pendentes=Count('id', filter=Q(status='pending')),
            agendadas=Count('id', filter=Q(status='scheduled')),
            concluidas=Count('id', filter=Q(status='completed'))
        )
        
        context = {
            'solicitacoes': solicitacoes,
            'total': stats['total'],
            'pendentes': stats['pendentes'],
            'agendadas': stats['agendadas'],
            'concluidas': stats['concluidas'],
            'status_filter': status_filter,
        }
        
        return render(request, 'services/meus_pedidos.html', context)
        
    except Exception as e:
        logger.error(f'Erro em meus_pedidos: {str(e)}', exc_info=True)
        messages.error(request, 'Ocorreu um erro ao carregar suas solicitações. Por favor, tente novamente.')
        return render(request, 'services/meus_pedidos.html', {
            'solicitacoes': [],
            'total': 0,
            'pendentes': 0,
            'agendadas': 0,
            'concluidas': 0,
        })
```

## Testing Strategy

### Testes Unitários

**Teste 1: View retorna solicitações do usuário correto**
```python
def test_meus_pedidos_returns_user_requests_only(self):
    # Criar dois usuários
    user1 = User.objects.create_user('user1', 'user1@test.com', 'pass')
    user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
    
    # Criar solicitações para cada usuário
    ServiceRequestModal.objects.create(user=user1, service_name='Serviço 1', ...)
    ServiceRequestModal.objects.create(user=user2, service_name='Serviço 2', ...)
    
    # Login como user1
    self.client.login(username='user1', password='pass')
    
    # Acessar página
    response = self.client.get(reverse('meus_pedidos'))
    
    # Verificar que apenas solicitações de user1 são retornadas
    self.assertEqual(len(response.context['solicitacoes']), 1)
    self.assertEqual(response.context['solicitacoes'][0].service_name, 'Serviço 1')
```

**Teste 2: Filtro por status funciona corretamente**
```python
def test_meus_pedidos_status_filter(self):
    user = User.objects.create_user('user', 'user@test.com', 'pass')
    
    # Criar solicitações com diferentes status
    ServiceRequestModal.objects.create(user=user, status='pending', ...)
    ServiceRequestModal.objects.create(user=user, status='completed', ...)
    
    self.client.login(username='user', password='pass')
    
    # Filtrar por pending
    response = self.client.get(reverse('meus_pedidos') + '?status=pending')
    self.assertEqual(len(response.context['solicitacoes']), 1)
    self.assertEqual(response.context['solicitacoes'][0].status, 'pending')
```

**Teste 3: Estatísticas são calculadas corretamente**
```python
def test_meus_pedidos_statistics(self):
    user = User.objects.create_user('user', 'user@test.com', 'pass')
    
    # Criar solicitações
    ServiceRequestModal.objects.create(user=user, status='pending', ...)
    ServiceRequestModal.objects.create(user=user, status='pending', ...)
    ServiceRequestModal.objects.create(user=user, status='completed', ...)
    
    self.client.login(username='user', password='pass')
    response = self.client.get(reverse('meus_pedidos'))
    
    self.assertEqual(response.context['total'], 3)
    self.assertEqual(response.context['pendentes'], 2)
    self.assertEqual(response.context['concluidas'], 1)
```

**Teste 4: Usuário não autenticado é redirecionado**
```python
def test_meus_pedidos_requires_login(self):
    response = self.client.get(reverse('meus_pedidos'))
    self.assertEqual(response.status_code, 302)
    self.assertIn('/login/', response.url)
```

### Testes de Integração

**Teste 1: Fluxo completo de visualização de pedidos**
1. Criar usuário e fazer login
2. Criar solicitações no banco
3. Acessar `/meus-pedidos/`
4. Verificar que HTML contém dados corretos
5. Clicar em filtro de status
6. Verificar que apenas solicitações filtradas aparecem

**Teste 2: Template renderiza corretamente sem dados**
1. Criar usuário sem solicitações
2. Acessar `/meus-pedidos/`
3. Verificar que mensagem "Nenhuma solicitação encontrada" aparece
4. Verificar que estatísticas mostram zeros

### Testes Manuais

1. **Verificar dados reais no banco**
   - Criar solicitações via interface
   - Acessar "Meus Pedidos"
   - Confirmar que solicitações aparecem

2. **Testar filtros**
   - Clicar em cada botão de filtro
   - Verificar que URL muda
   - Verificar que lista é filtrada corretamente

3. **Testar com diferentes estados**
   - Criar solicitações com todos os status possíveis
   - Verificar que badges de status têm cores corretas
   - Verificar que contadores estão corretos

4. **Testar edge cases**
   - Solicitação sem prestador atribuído
   - Solicitação sem data/hora preferencial
   - Solicitação com endereço incompleto

## Implementation Notes

### Verificações Necessárias

1. **Remover dados estáticos do template**
   - Verificar se há loops `{% for %}` com dados hardcoded
   - Verificar se há valores mockados em variáveis
   - Garantir que todas as variáveis vêm do contexto da view

2. **Validar view existente**
   - Confirmar que a view consulta o banco corretamente
   - Verificar se há dados mockados na view
   - Testar com dados reais no banco

3. **Otimizações opcionais**
   - Implementar agregação para estatísticas (reduz queries)
   - Adicionar paginação se houver muitas solicitações
   - Implementar cache para estatísticas

### Possíveis Problemas

1. **Dados mockados na view**
   - **Sintoma**: Sempre mostra os mesmos dados independente do usuário
   - **Solução**: Remover dados mockados e usar query real

2. **Template não recebe contexto**
   - **Sintoma**: Template vazio ou com erros
   - **Solução**: Verificar que view passa contexto corretamente

3. **Filtros não funcionam**
   - **Sintoma**: Clicar em filtro não muda a lista
   - **Solução**: Verificar que view lê `request.GET.get('status')`

4. **Estatísticas incorretas**
   - **Sintoma**: Contadores não batem com lista
   - **Solução**: Verificar queries de contagem

### Melhorias Futuras

1. **Paginação**
   - Adicionar `Paginator` do Django para listas grandes
   - Limitar a 10-20 solicitações por página

2. **Busca**
   - Adicionar campo de busca por nome de serviço ou prestador
   - Implementar busca full-text

3. **Ordenação**
   - Permitir ordenar por data, status, prestador
   - Adicionar botões de ordenação

4. **Exportação**
   - Permitir exportar lista em CSV ou PDF
   - Útil para histórico do cliente

5. **Notificações**
   - Mostrar badge com número de solicitações pendentes
   - Integrar com sistema de notificações

## Summary

A implementação da funcionalidade de exibição de pedidos reais na tela "Meus Pedidos" está **praticamente completa**. A análise do código existente mostra que:

- ✅ View `meus_pedidos` já implementada e funcional
- ✅ Rota URL já configurada
- ✅ Template já estruturado para dados dinâmicos
- ✅ Modelo `ServiceRequestModal` adequado

**Tarefas principais**:
1. Verificar e remover quaisquer dados estáticos/mockados do template
2. Validar que a view está consultando o banco corretamente
3. Testar com dados reais no banco de dados
4. Implementar melhorias opcionais (otimização de queries, error handling)

**Riscos baixos**: A maior parte do código já existe e parece estar correta. O trabalho será principalmente de validação e limpeza.
