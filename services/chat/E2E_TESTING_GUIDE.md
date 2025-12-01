# Chat IA Assistente (Sophie) - End-to-End Testing Guide

Este documento fornece um guia completo para testes end-to-end do sistema de Chat IA Assistente em ambiente de staging.

## Índice

1. [Preparação do Ambiente](#preparação-do-ambiente)
2. [Testes de Fluxo do Cliente](#testes-de-fluxo-do-cliente)
3. [Testes de Fluxo do Prestador](#testes-de-fluxo-do-prestador)
4. [Testes de Responsividade Mobile](#testes-de-responsividade-mobile)
5. [Testes de Persistência de Navegação](#testes-de-persistência-de-navegação)
6. [Testes de Performance](#testes-de-performance)
7. [Checklist de Validação](#checklist-de-validação)

---

## Preparação do Ambiente

### Pré-requisitos

- [ ] Ambiente de staging configurado e acessível
- [ ] Redis rodando e acessível
- [ ] OpenAI API key configurada
- [ ] Banco de dados populado com dados de teste
- [ ] Usuários de teste criados (cliente e prestador)
- [ ] Navegadores para teste: Chrome, Firefox, Safari, Edge
- [ ] Dispositivos móveis ou emuladores disponíveis

### Credenciais de Teste

Crie os seguintes usuários de teste:

**Cliente de Teste**:
- Username: `test_client`
- Email: `client@test.com`
- Password: `TestClient123!`
- User Type: Customer

**Prestador de Teste**:
- Username: `test_provider`
- Email: `provider@test.com`
- Password: `TestProvider123!`
- User Type: Professional

### Verificação Inicial

Antes de iniciar os testes, verifique:

```bash
# 1. Redis está rodando
redis-cli ping
# Deve retornar: PONG

# 2. Daphne está rodando
curl http://staging-url:8000/
# Deve retornar resposta HTTP

# 3. WebSocket está acessível
wscat -c ws://staging-url:8000/ws/chat/
# Deve conectar sem erros
```

---

## Testes de Fluxo do Cliente

### Teste 1: Abertura do Chat

**Objetivo**: Verificar que o widget de chat aparece e abre corretamente

**Passos**:
1. Acesse a página inicial como usuário não autenticado
2. Localize o botão flutuante do chat (canto inferior direito)
3. Verifique que o botão está posicionado acima do botão de acessibilidade
4. Clique no botão do chat

**Resultado Esperado**:
- ✅ Botão do chat visível e bem posicionado
- ✅ Janela do chat abre suavemente
- ✅ Mensagem de boas-vindas da Sophie aparece
- ✅ Campo de input está focado e pronto para digitação

**Requirements**: 1.1, 1.7

---

### Teste 2: Envio de Mensagem Simples

**Objetivo**: Verificar envio e recebimento de mensagens

**Passos**:
1. Com o chat aberto, digite: "Olá, preciso de ajuda"
2. Pressione Enter ou clique no botão de enviar
3. Aguarde a resposta

**Resultado Esperado**:
- ✅ Mensagem do usuário aparece imediatamente
- ✅ Indicador de digitação aparece
- ✅ Resposta da Sophie aparece em menos de 3 segundos
- ✅ Resposta é relevante e em português
- ✅ Timestamp correto nas mensagens

**Requirements**: 1.3, 2.1

---

### Teste 3: Pergunta sobre Serviços

**Objetivo**: Verificar que a IA responde perguntas sobre serviços

**Passos**:
1. Digite: "Quais serviços vocês oferecem?"
2. Aguarde resposta
3. Digite: "Quanto custa um encanador?"
4. Aguarde resposta

**Resultado Esperado**:
- ✅ Sophie lista serviços disponíveis
- ✅ Sophie fornece informações de preço
- ✅ Respostas incluem links para páginas relevantes
- ✅ Contexto é mantido entre mensagens

**Requirements**: 2.2, 2.4, 2.5

---

### Teste 4: Ajuda com Navegação

**Objetivo**: Verificar que a IA ajuda com navegação no site

**Passos**:
1. Digite: "Como faço para solicitar um serviço?"
2. Aguarde resposta
3. Clique em um link fornecido pela Sophie
4. Verifique se o chat permanece acessível

**Resultado Esperado**:
- ✅ Sophie fornece instruções passo a passo
- ✅ Links diretos para páginas relevantes
- ✅ Chat permanece aberto durante navegação
- ✅ Histórico de conversa é mantido

**Requirements**: 3.1, 3.3, 3.5

---

### Teste 5: Minimizar e Maximizar Chat

**Objetivo**: Verificar funcionalidade de minimizar/maximizar

**Passos**:
1. Com o chat aberto e algumas mensagens trocadas
2. Clique no botão de minimizar
3. Navegue para outra página
4. Clique no botão do chat novamente

**Resultado Esperado**:
- ✅ Chat minimiza suavemente
- ✅ Botão do chat mostra badge de mensagens não lidas (se houver)
- ✅ Chat reabre com histórico intacto
- ✅ Sessão é mantida entre páginas

**Requirements**: 1.5, 5.1, 5.3

---

### Teste 6: Fechar e Reabrir Chat

**Objetivo**: Verificar persistência de sessão

**Passos**:
1. Com o chat aberto e histórico de mensagens
2. Clique no botão de fechar (X)
3. Aguarde 5 segundos
4. Clique no botão do chat novamente

**Resultado Esperado**:
- ✅ Chat fecha completamente
- ✅ Ao reabrir, histórico é recuperado
- ✅ Sessão é mantida (mesmo session_id)
- ✅ Contexto de navegação é atualizado

**Requirements**: 1.4, 5.3

---

### Teste 7: Avaliação de Satisfação

**Objetivo**: Verificar sistema de avaliação

**Passos**:
1. Após algumas mensagens, feche o chat
2. Verifique se aparece prompt de avaliação
3. Selecione 5 estrelas
4. Clique em "Enviar Avaliação"

**Resultado Esperado**:
- ✅ Prompt de avaliação aparece ao fechar
- ✅ Estrelas são selecionáveis
- ✅ Avaliação é enviada com sucesso
- ✅ Mensagem de confirmação aparece

**Requirements**: 6.4

---

### Teste 8: Detecção de Frustração

**Objetivo**: Verificar escalação para suporte humano

**Passos**:
1. Digite mensagens indicando frustração:
   - "Isso não está funcionando"
   - "Não estou conseguindo resolver"
   - "Preciso falar com alguém"
2. Aguarde resposta

**Resultado Esperado**:
- ✅ Sophie detecta frustração
- ✅ Oferece contato com suporte humano
- ✅ Fornece informações de contato
- ✅ Sessão é marcada como escalada

**Requirements**: 6.3, 6.5

---

## Testes de Fluxo do Prestador

### Teste 9: Chat como Prestador

**Objetivo**: Verificar experiência específica para prestadores

**Passos**:
1. Faça login como prestador de teste
2. Abra o chat
3. Digite: "Como aceito uma solicitação?"
4. Digite: "Onde vejo meus pagamentos?"

**Resultado Esperado**:
- ✅ Sophie identifica usuário como prestador
- ✅ Respostas são específicas para prestadores
- ✅ Links direcionam para painel do prestador
- ✅ Informações sobre gerenciamento de solicitações

**Requirements**: 4.1, 4.2, 4.3

---

### Teste 10: Contexto do Prestador

**Objetivo**: Verificar personalização para prestadores

**Passos**:
1. Como prestador, navegue para "Painel do Prestador"
2. Abra o chat
3. Digite: "Preciso de ajuda"

**Resultado Esperado**:
- ✅ Sophie reconhece contexto do painel
- ✅ Oferece ajuda específica para a página atual
- ✅ Sugere ações relevantes para prestadores

**Requirements**: 4.1, 5.5

---

## Testes de Responsividade Mobile

### Teste 11: Chat em Mobile (Portrait)

**Objetivo**: Verificar funcionamento em dispositivos móveis

**Dispositivos**: iPhone 12, Samsung Galaxy S21, ou emuladores

**Passos**:
1. Acesse o site em dispositivo móvel (modo retrato)
2. Localize e clique no botão do chat
3. Envie algumas mensagens
4. Teste scroll do histórico
5. Minimize e maximize o chat

**Resultado Esperado**:
- ✅ Botão do chat visível e acessível
- ✅ Chat abre em tela cheia no mobile
- ✅ Teclado não sobrepõe o input
- ✅ Scroll funciona suavemente
- ✅ Botões são facilmente clicáveis (min 44x44px)

**Requirements**: 1.6

---

### Teste 12: Chat em Mobile (Landscape)

**Objetivo**: Verificar funcionamento em modo paisagem

**Passos**:
1. Rotacione o dispositivo para modo paisagem
2. Abra o chat
3. Envie mensagens
4. Verifique layout

**Resultado Esperado**:
- ✅ Layout se adapta ao modo paisagem
- ✅ Chat permanece usável
- ✅ Não há elementos cortados ou sobrepostos

**Requirements**: 1.6

---

### Teste 13: Chat em Tablet

**Objetivo**: Verificar funcionamento em tablets

**Dispositivos**: iPad, Samsung Tab, ou emuladores

**Passos**:
1. Acesse o site em tablet
2. Teste o chat em ambas orientações
3. Verifique tamanho e posicionamento

**Resultado Esperado**:
- ✅ Chat tem tamanho apropriado para tablet
- ✅ Não ocupa tela inteira desnecessariamente
- ✅ Posicionamento é adequado

**Requirements**: 1.6

---

## Testes de Persistência de Navegação

### Teste 14: Navegação com Chat Aberto

**Objetivo**: Verificar que o chat persiste durante navegação

**Passos**:
1. Abra o chat na página inicial
2. Envie uma mensagem
3. Navegue para "Buscar Profissionais"
4. Verifique o chat
5. Navegue para "Sobre"
6. Verifique o chat novamente

**Resultado Esperado**:
- ✅ Chat permanece aberto durante navegação
- ✅ Histórico é mantido
- ✅ Contexto de navegação é atualizado
- ✅ Não há perda de conexão

**Requirements**: 1.4, 3.5

---

### Teste 15: Reconexão após Perda de Rede

**Objetivo**: Verificar recuperação após perda de conexão

**Passos**:
1. Abra o chat e envie mensagens
2. Desabilite a conexão de rede por 10 segundos
3. Reabilite a conexão
4. Tente enviar uma nova mensagem

**Resultado Esperado**:
- ✅ Chat detecta perda de conexão
- ✅ Mostra indicador de "Reconectando..."
- ✅ Reconecta automaticamente
- ✅ Sessão é recuperada
- ✅ Mensagens pendentes são enviadas

**Requirements**: 1.4, 6.1

---

### Teste 16: Múltiplas Abas

**Objetivo**: Verificar comportamento com múltiplas abas

**Passos**:
1. Abra o site em uma aba
2. Abra o chat e envie mensagens
3. Abra o site em outra aba
4. Abra o chat na segunda aba

**Resultado Esperado**:
- ✅ Cada aba mantém sua própria conexão
- ✅ Histórico é compartilhado (mesma sessão)
- ✅ Não há conflitos entre abas

**Requirements**: 5.3

---

## Testes de Performance

### Teste 17: Tempo de Resposta

**Objetivo**: Verificar que respostas são rápidas

**Passos**:
1. Envie 10 mensagens diferentes
2. Meça o tempo de resposta de cada uma
3. Calcule a média

**Resultado Esperado**:
- ✅ 95% das respostas em menos de 2 segundos
- ✅ Nenhuma resposta demora mais de 5 segundos
- ✅ Tempo médio < 1.5 segundos

**Requirements**: 8.4

---

### Teste 18: Múltiplos Usuários Simultâneos

**Objetivo**: Verificar performance com carga

**Passos**:
1. Abra 10 navegadores/abas diferentes
2. Faça login com usuários diferentes em cada
3. Abra o chat em todos simultaneamente
4. Envie mensagens em todos ao mesmo tempo

**Resultado Esperado**:
- ✅ Todos os chats funcionam normalmente
- ✅ Não há degradação perceptível de performance
- ✅ Respostas continuam rápidas

**Requirements**: 8.1

---

### Teste 19: Rate Limiting

**Objetivo**: Verificar que rate limiting funciona

**Passos**:
1. Abra o chat
2. Envie 15 mensagens rapidamente (uma após a outra)
3. Observe o comportamento

**Resultado Esperado**:
- ✅ Primeiras 10 mensagens são processadas
- ✅ Mensagens 11-15 são bloqueadas
- ✅ Mensagem de erro clara é exibida
- ✅ Indica tempo de espera

**Requirements**: 8.3

---

## Checklist de Validação

### Funcionalidade Básica
- [ ] Chat abre e fecha corretamente
- [ ] Mensagens são enviadas e recebidas
- [ ] Histórico é mantido
- [ ] Sessão persiste entre páginas
- [ ] Avaliação de satisfação funciona

### Inteligência Artificial
- [ ] Respostas são relevantes e em português
- [ ] IA responde perguntas sobre serviços
- [ ] IA ajuda com navegação
- [ ] IA diferencia cliente de prestador
- [ ] Detecção de frustração funciona

### Interface e UX
- [ ] Design é atraente e profissional
- [ ] Animações são suaves
- [ ] Botões são facilmente clicáveis
- [ ] Feedback visual é claro
- [ ] Acessibilidade está adequada

### Mobile e Responsividade
- [ ] Funciona em smartphones (iOS e Android)
- [ ] Funciona em tablets
- [ ] Layout se adapta a diferentes tamanhos
- [ ] Touch targets são adequados
- [ ] Teclado não causa problemas

### Performance
- [ ] Respostas são rápidas (< 2s)
- [ ] Não há travamentos ou lentidão
- [ ] Múltiplos usuários não causam problemas
- [ ] Rate limiting funciona corretamente

### Segurança
- [ ] Mensagens são sanitizadas
- [ ] Rate limiting previne abuso
- [ ] Sessões são seguras
- [ ] Dados sensíveis não são expostos

### Integração
- [ ] Chat funciona em todas as páginas
- [ ] Não interfere com outros elementos
- [ ] Posicionamento é consistente
- [ ] Não causa erros de console

---

## Relatório de Bugs

Use o seguinte template para reportar bugs encontrados:

```markdown
### Bug #[número]

**Título**: [Descrição curta do bug]

**Severidade**: [Crítica / Alta / Média / Baixa]

**Ambiente**:
- URL: [URL onde ocorreu]
- Navegador: [Chrome 120 / Firefox 121 / etc]
- Dispositivo: [Desktop / iPhone 12 / etc]
- Usuário: [Cliente / Prestador / Anônimo]

**Passos para Reproduzir**:
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

**Resultado Esperado**:
[O que deveria acontecer]

**Resultado Atual**:
[O que realmente aconteceu]

**Screenshots/Vídeos**:
[Anexar se possível]

**Logs**:
```
[Colar logs relevantes]
```

**Requirement Afetado**: [1.1, 2.3, etc]
```

---

## Aprovação Final

Após completar todos os testes, preencha:

**Testado por**: ___________________________

**Data**: ___________________________

**Ambiente**: ___________________________

**Status Geral**: [ ] Aprovado [ ] Aprovado com ressalvas [ ] Reprovado

**Observações**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

**Assinatura**: ___________________________

---

**Última atualização**: 2025-11-26
**Versão**: 1.0.0
