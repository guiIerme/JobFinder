# Design Document

## Overview

Este documento descreve o design para corrigir e melhorar o sistema de filtros da página de busca de profissionais. O sistema atual possui funcionalidade básica no backend, mas o frontend não está aplicando os filtros automaticamente. O design foca em criar uma experiência fluida com aplicação automática de filtros e melhorias visuais.

## Architecture

### Frontend Architecture
- **Auto-Filter System**: JavaScript que detecta mudanças nos filtros e aplica automaticamente
- **Debounce System**: Implementação de debounce para campos de texto para evitar requisições excessivas
- **Visual Feedback**: Sistema de loading e feedback visual para o usuário
- **State Management**: Gerenciamento do estado dos filtros no frontend

### Backend Architecture
- **Existing View**: A view `search_new` já processa corretamente os parâmetros de filtro
- **Query Parameters**: Sistema atual usa GET parameters que funcionam corretamente
- **Filter Logic**: Lógica de filtro já implementada e funcional

## Components and Interfaces

### 1. Auto-Filter Manager (JavaScript)
```javascript
class AutoFilterManager {
    constructor() {
        this.debounceTimeout = null;
        this.isLoading = false;
    }
    
    // Aplica filtros automaticamente
    applyFilters(immediate = false)
    
    // Debounce para campos de texto
    debounceFilter(callback, delay = 500)
    
    // Mostra/esconde loading
    toggleLoading(show)
    
    // Atualiza URL e recarrega página
    updateResults(params)
}
```

### 2. Visual Enhancement System (CSS)
- **Modern Card Design**: Cards com sombras suaves e bordas arredondadas
- **Color Consistency**: Uso consistente do tema roxo (#6f42c1)
- **Smooth Transitions**: Transições suaves para mudanças de estado
- **Interactive States**: Estados hover e active bem definidos

### 3. Filter Components

#### Search Filter
- Input com debounce de 500ms
- Ícone de busca integrado
- Aplicação automática ao digitar

#### Category Filter
- Radio buttons com aplicação imediata
- Ícones coloridos para cada categoria
- Visual feedback para seleção

#### Rating Filter
- Radio buttons com estrelas visuais
- Aplicação imediata ao selecionar
- Cores diferenciadas para ratings

#### Price Filter
- Radio buttons para faixas predefinidas
- Aplicação imediata ao selecionar
- Formatação monetária clara

#### Location Filter
- Input com debounce de 500ms
- Ícone de localização
- Toggle para "próximos a mim"

## Data Models

### Filter State Object
```javascript
{
    search: string,
    category: string,
    rating: string,
    price: string,
    location: string,
    nearby: boolean
}
```

### URL Parameters
- `search`: Termo de busca
- `category`: Categoria selecionada
- `rating`: Rating mínimo
- `price_min`: Preço mínimo
- `price_max`: Preço máximo
- `location`: Localização

## Error Handling

### Frontend Error Handling
1. **Network Errors**: Mostrar mensagem de erro se requisição falhar
2. **Invalid Input**: Validação de entrada antes de aplicar filtros
3. **Loading States**: Indicadores visuais durante carregamento
4. **Fallback**: Manter estado anterior se erro ocorrer

### Backend Error Handling
- O backend já possui tratamento adequado com try/catch para conversões
- Filtros inválidos são ignorados silenciosamente

## Testing Strategy

### Unit Tests
- Testar funções de debounce
- Testar construção de parâmetros de URL
- Testar validação de entrada

### Integration Tests
- Testar aplicação automática de filtros
- Testar combinação de múltiplos filtros
- Testar paginação com filtros

### User Experience Tests
- Testar responsividade em dispositivos móveis
- Testar acessibilidade com screen readers
- Testar performance com muitos resultados

## Implementation Details

### Phase 1: Fix Current Functionality
1. Corrigir JavaScript para aplicar filtros automaticamente
2. Implementar debounce para campos de texto
3. Adicionar feedback visual de loading

### Phase 2: Visual Improvements
1. Melhorar CSS dos filtros
2. Adicionar transições suaves
3. Implementar estados interativos

### Phase 3: Enhanced Features
1. Adicionar animações sutis
2. Implementar feedback de resultados
3. Otimizar performance

## Visual Design Specifications

### Color Palette
- Primary: #6f42c1 (roxo principal)
- Primary Light: #8a6ece
- Primary Dark: #5a32a3
- Secondary: #4e73df
- Success: #1cc88a
- Background: #f8f9fc

### Typography
- Headers: Font-weight 700
- Labels: Font-weight 600
- Body: Font-weight 400

### Spacing
- Card padding: 2rem
- Section spacing: 1.5rem
- Element spacing: 0.75rem

### Interactive Elements
- Border radius: 10px
- Box shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15)
- Transition: all 0.3s ease-in-out