# Documentação da API - Job Finder

## Visão Geral
Esta documentação descreve os endpoints da API RESTful do Job Finder, uma plataforma de serviços domésticos que conecta clientes a profissionais.

## Autenticação
A maioria dos endpoints requer autenticação via sessão Django. Os endpoints públicos estão claramente marcados.

## Formato de Resposta
Todos os endpoints retornam dados no formato JSON.

## Endpoints da API

### Autenticação

#### Registrar Usuário
- **URL**: `/register/`
- **Método**: `POST`
- **Autenticação**: Não requerida
- **Parâmetros**:
  - `username` (string, obrigatório)
  - `email` (string, obrigatório)
  - `password` (string, obrigatório)
  - `password_confirm` (string, obrigatório)
  - `user_type` (string, opcional) - "customer" ou "professional"
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "message": "Conta criada com sucesso para {username}"
  }
  ```

#### Login
- **URL**: `/login/`
- **Método**: `POST`
- **Autenticação**: Não requerida
- **Parâmetros**:
  - `username` (string, obrigatório)
  - `password` (string, obrigatório)
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "redirect_url": "/"
  }
  ```

#### Logout
- **URL**: `/logout/`
- **Método**: `GET` ou `POST`
- **Autenticação**: Requerida
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "message": "Você saiu da sua conta com sucesso."
  }
  ```

### Perfis de Usuário

#### Obter Perfil do Usuário
- **URL**: `/profile/`
- **Método**: `GET`
- **Autenticação**: Requerida
- **Resposta de Sucesso**:
  ```json
  {
    "user_profile": {
      "user_type": "customer|professional|admin",
      "phone": "string",
      "address": "string",
      "city": "string",
      "state": "string",
      "zip_code": "string"
    },
    "payment_methods": [...],
    "user_orders": [...]
  }
  ```

#### Atualizar Perfil do Usuário
- **URL**: `/profile/`
- **Método**: `POST`
- **Autenticação**: Requerida
- **Parâmetros**:
  - `phone` (string, opcional)
  - `address` (string, opcional)
  - `city` (string, opcional)
  - `state` (string, opcional)
  - `zip_code` (string, opcional)
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "message": "Perfil atualizado com sucesso"
  }
  ```

### Serviços

#### Buscar Serviços
- **URL**: `/search/`
- **Método**: `GET`
- **Autenticação**: Não requerida (mas recomendada)
- **Parâmetros de Query**:
  - `search` (string, opcional) - Termo de busca
  - `category` (string, opcional) - Categoria do serviço
  - `rating` (number, opcional) - Avaliação mínima
  - `price_min` (number, opcional) - Preço mínimo
  - `price_max` (number, opcional) - Preço máximo
  - `location` (string, opcional) - Localização
- **Resposta de Sucesso**:
  ```json
  {
    "custom_services": [...],
    "categories": [...]
  }
  ```

#### Obter Detalhes de um Serviço
- **URL**: `/api/service/{service_id}/`
- **Método**: `GET`
- **Autenticação**: Não requerida
- **Resposta de Sucesso**:
  ```json
  {
    "id": 1,
    "name": "Nome do Serviço",
    "description": "Descrição do serviço",
    "category": "Categoria",
    "price": "150.00",
    "rating": "4.5",
    "provider": {
      "id": 1,
      "name": "Nome do Profissional",
      "rating": "4.5"
    }
  }
  ```

### Pedidos

#### Solicitar Serviço
- **URL**: `/request-service-from-search/{custom_service_id}/`
- **Método**: `POST`
- **Autenticação**: Requerida
- **Parâmetros**:
  - `scheduled_datetime` (datetime, obrigatório)
  - `address` (string, obrigatório)
  - `number` (string, obrigatório)
  - `city` (string, obrigatório)
  - `state` (string, obrigatório)
  - `problem_description` (string, opcional)
  - `notes` (string, opcional)
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "message": "Solicitação de serviço enviada com sucesso!",
    "redirect_url": "/order-confirmation/{order_id}/"
  }
  ```

#### Confirmar Pedido
- **URL**: `/order-confirmation/{order_id}/`
- **Método**: `GET`
- **Autenticação**: Requerida
- **Resposta de Sucesso**:
  ```json
  {
    "order": {
      "id": 1,
      "status": "pending|confirmed|in_progress|completed|cancelled",
      "scheduled_date": "2025-10-20T10:00:00",
      "total_price": "150.00"
    }
  }
  ```

### Chat

#### Listar Conversas
- **URL**: `/chats/`
- **Método**: `GET`
- **Autenticação**: Requerida
- **Resposta de Sucesso**:
  ```json
  {
    "chats": [...]
  }
  ```

#### Abrir Conversa
- **URL**: `/chats/{chat_id}/`
- **Método**: `GET`
- **Autenticação**: Requerida
- **Resposta de Sucesso**:
  ```json
  {
    "chat": {
      "id": 1,
      "customer": {...},
      "professional": {...},
      "messages": [...]
    }
  }
  ```

#### Enviar Mensagem
- **URL**: `/chats/{chat_id}/`
- **Método**: `POST`
- **Autenticação**: Requerida
- **Parâmetros**:
  - `content` (string, obrigatório)
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "message": "Mensagem enviada com sucesso"
  }
  ```

### Painel Administrativo

#### Dashboard Administrativo
- **URL**: `/admin-dashboard-new/`
- **Método**: `GET`
- **Autenticação**: Requerida (apenas administradores)
- **Resposta de Sucesso**:
  ```json
  {
    "users_count": 100,
    "services_count": 50,
    "orders_count": 200,
    "revenue": "15000.00"
  }
  ```

### Avaliações

#### Submeter Avaliação
- **URL**: `/api/review/{order_id}/`
- **Método**: `POST`
- **Autenticação**: Requerida
- **Parâmetros**:
  - `rating` (number, obrigatório) - 1 a 5
  - `comment` (string, opcional)
- **Resposta de Sucesso**:
  ```json
  {
    "success": true,
    "message": "Review submitted successfully"
  }
  ```

## Códigos de Status HTTP

- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `400 Bad Request` - Requisição inválida
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Acesso negado
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro interno do servidor

## Tratamento de Erros

Todos os erros seguem este formato:
```json
{
  "error": "Mensagem de erro detalhada"
}
```

Ou para erros de validação:
```json
{
  "success": false,
  "message": "Mensagem de erro"
}
```

## Limitações Conhecidas

1. O sistema de pagamento é simulado e não processa pagamentos reais
2. O sistema de notificações por email requer configuração adicional para produção
3. Algumas funcionalidades de IA estão em modo de demonstração

## Considerações de Segurança

1. Todas as senhas são armazenadas com hash seguro
2. A autenticação é gerenciada pelo Django
3. Proteção CSRF habilitada para todos os formulários
4. Validação de entrada em todos os endpoints

## Versão da API

Atual: v1.0

## Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento.