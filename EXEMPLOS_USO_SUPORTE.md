# 📚 Exemplos de Uso - Sistema de Suporte

## 🎯 Cenários Práticos

### Cenário 1: Cliente com Problema de Login

**Cliente**: Maria Silva  
**Problema**: Não consegue fazer login

#### Passo a Passo

1. **Maria acessa o suporte**
   ```
   URL: /support/
   ```

2. **Cria um novo ticket**
   ```
   Assunto: Não consigo fazer login
   Categoria: Conta e Perfil
   Prioridade: Alta
   Descrição: Estou tentando fazer login mas aparece "senha incorreta"
   Anexo: screenshot_erro.png
   ```

3. **Sistema gera ticket**
   ```
   Ticket: #TK20241202143025XXXX
   Status: Aberto
   ```

4. **Agente João recebe notificação**
   ```
   "Novo ticket #TK20241202143025XXXX: Não consigo fazer login"
   ```

5. **João atribui o ticket a si mesmo**
   ```
   Status: Em Andamento
   Atribuído a: João Silva
   ```

6. **João responde**
   ```
   "Olá Maria! Vou te ajudar. Você tentou usar a opção 'Esqueci minha senha'?"
   Status: Aguardando Cliente
   ```

7. **Maria responde**
   ```
   "Sim, mas não recebi o email de recuperação."
   Status: Aguardando Suporte
   ```

8. **João resolve**
   ```
   "Encontrei o problema! Seu email estava com erro de digitação. 
   Corrigi e enviei novo link de recuperação. Verifique sua caixa de entrada."
   Status: Resolvido
   ```

9. **Maria avalia**
   ```
   Avaliação: 5 estrelas
   Feedback: "Atendimento rápido e eficiente! Obrigada!"
   Status: Fechado
   ```

---

### Cenário 2: Problema Técnico Urgente

**Cliente**: Pedro Santos  
**Problema**: Erro ao processar pagamento

#### Passo a Passo

1. **Pedro cria ticket urgente**
   ```
   Assunto: Erro ao processar pagamento
   Categoria: Pagamento
   Prioridade: Urgente
   Descrição: Tentei pagar um serviço mas deu erro 500
   ```

2. **Múltiplos agentes são notificados**
   ```
   Prioridade URGENTE detectada!
   Notificação enviada para todos os agentes disponíveis
   ```

3. **Ana (agente disponível) atribui imediatamente**
   ```
   Tempo de resposta: 2 minutos
   ```

4. **Ana investiga**
   ```
   "Pedro, estou verificando. Pode me informar o horário exato do erro?"
   ```

5. **Pedro responde**
   ```
   "Foi às 14:30, tentei 3 vezes"
   ```

6. **Ana cria nota interna**
   ```
   Tipo: Nota Interna (cliente não vê)
   "Verificar logs do gateway de pagamento às 14:30"
   ```

7. **Ana resolve**
   ```
   "Pedro, identifiquei o problema. Era uma instabilidade temporária 
   do gateway. Já está normalizado. Pode tentar novamente."
   Status: Resolvido
   ```

8. **Pedro confirma e avalia**
   ```
   "Funcionou! Obrigado pela agilidade!"
   Avaliação: 5 estrelas
   ```

---

### Cenário 3: Dúvida Simples (Base de Conhecimento)

**Cliente**: Lucas Oliveira  
**Dúvida**: Como adicionar foto de perfil?

#### Passo a Passo

1. **Lucas acessa o suporte**
   ```
   URL: /support/
   ```

2. **Vê link para Base de Conhecimento**
   ```
   "Antes de criar um ticket, consulte nossa Base de Conhecimento"
   ```

3. **Lucas busca**
   ```
   Busca: "foto perfil"
   Resultado: "Como adicionar foto de perfil"
   ```

4. **Lucas lê o artigo**
   ```
   Artigo explica passo a passo com screenshots
   ```

5. **Lucas avalia o artigo**
   ```
   "Este artigo foi útil?" → SIM
   ```

6. **Ticket não foi necessário!**
   ```
   Economia de tempo para cliente e agente
   ```

---

### Cenário 4: Múltiplos Tickets do Mesmo Cliente

**Cliente**: Carla Mendes  
**Situação**: Vários problemas diferentes

#### Tickets Criados

**Ticket 1**
```
#TK001 - Dúvida sobre cancelamento
Status: Resolvido
Agente: João
Avaliação: 4 estrelas
```

**Ticket 2**
```
#TK002 - Problema com notificações
Status: Em Andamento
Agente: Ana
```

**Ticket 3**
```
#TK003 - Sugestão de melhoria
Status: Aberto
Agente: Não atribuído
```

#### Dashboard da Carla
```
Total de Tickets: 3
Abertos: 1
Em Andamento: 1
Resolvidos: 1
```

---

### Cenário 5: Agente com Múltiplos Tickets

**Agente**: João Silva  
**Situação**: Gerenciando vários tickets

#### Dashboard do João
```
Meus Tickets Abertos: 5
Aguardando Resposta: 2
Total Atribuídos: 12
Não Atribuídos: 3
```

#### Tickets do João

**Prioridade Urgente**
```
#TK101 - Erro crítico no sistema
Status: Em Andamento
Última atualização: 5 min atrás
```

**Prioridade Alta**
```
#TK102 - Problema com pagamento
Status: Aguardando Cliente
Última atualização: 1 hora atrás
```

**Prioridade Média**
```
#TK103 - Dúvida sobre serviço
#TK104 - Alteração de dados
#TK105 - Sugestão de melhoria
```

#### Estatísticas do João
```
Total de Tickets: 45
Avaliação Média: 4.8 ⭐
Tempo Médio de Resposta: 15 minutos
Tempo Médio de Resolução: 2.5 horas
Taxa de Satisfação: 95%
```

---

## 🔄 Fluxos de Status

### Fluxo Normal
```
Aberto → Em Andamento → Aguardando Cliente → Resolvido → Fechado
```

### Fluxo com Ida e Volta
```
Aberto → Em Andamento → Aguardando Cliente → 
Aguardando Suporte → Aguardando Cliente → Resolvido → Fechado
```

### Fluxo Rápido
```
Aberto → Em Andamento → Resolvido → Fechado
```

---

## 📊 Exemplos de Estatísticas

### Estatísticas do Sistema
```
Total de Tickets: 1.234
Tickets Abertos: 45
Tickets Resolvidos Hoje: 23
Tempo Médio de Resolução: 3.2 horas
Satisfação Média: 4.6 ⭐
```

### Estatísticas por Categoria
```
Técnico: 35%
Conta: 25%
Pagamento: 20%
Serviços: 15%
Outros: 5%
```

### Estatísticas por Prioridade
```
Urgente: 5%
Alta: 15%
Média: 60%
Baixa: 20%
```

---

## 💬 Exemplos de Mensagens

### Mensagem de Boas-Vindas (Sistema)
```
"Olá! Seu ticket foi criado com sucesso. 
Um agente irá responder em breve."
```

### Primeira Resposta do Agente
```
"Olá [Nome]! Sou [Agente] e vou te ajudar com [Problema]. 
Pode me fornecer mais detalhes sobre [Informação]?"
```

### Solicitação de Informações
```
"Para resolver melhor, preciso de algumas informações:
1. Quando o problema começou?
2. Você já tentou [Solução]?
3. Pode enviar um screenshot?"
```

### Resolução
```
"Ótimo! O problema foi resolvido. 
Se precisar de mais alguma coisa, é só responder aqui!"
```

### Agradecimento
```
"Obrigado pelo contato! Ficamos felizes em ajudar. 
Não esqueça de avaliar nosso atendimento! 😊"
```

---

## 🎯 Boas Práticas

### Para Clientes
1. ✅ Seja específico no assunto
2. ✅ Descreva o problema em detalhes
3. ✅ Anexe screenshots quando possível
4. ✅ Responda rapidamente às perguntas do agente
5. ✅ Avalie o atendimento ao final

### Para Agentes
1. ✅ Responda rapidamente (meta: 15 min)
2. ✅ Seja educado e profissional
3. ✅ Faça perguntas claras
4. ✅ Use notas internas para documentar
5. ✅ Atualize o status corretamente
6. ✅ Confirme a resolução com o cliente

---

## 🚫 O que NÃO fazer

### Clientes
- ❌ Criar múltiplos tickets para o mesmo problema
- ❌ Usar linguagem ofensiva
- ❌ Enviar informações sensíveis (senhas, cartões)
- ❌ Avaliar negativamente sem explicar o motivo

### Agentes
- ❌ Deixar tickets sem resposta por muito tempo
- ❌ Fechar tickets sem confirmar resolução
- ❌ Usar linguagem técnica demais
- ❌ Esquecer de atualizar o status

---

## 📞 Contato

Para dúvidas sobre o sistema de suporte, crie um ticket! 😄

---

**JobFinder - Sistema de Suporte**  
**Exemplos de Uso**  
**Versão**: 1.0
