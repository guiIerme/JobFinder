# Guia do Sistema de Auto-Refresh

## 📋 Visão Geral

O sistema de Auto-Refresh permite que as páginas do site sejam recarregadas automaticamente após um período configurável de tempo. Isso é útil para manter o conteúdo atualizado sem intervenção manual do usuário.

## ✨ Funcionalidades

- ✅ **Auto-refresh configurável** - Defina o intervalo de atualização
- ✅ **Aviso antes de recarregar** - Notifica o usuário 10 segundos antes
- ✅ **Pausa durante atividade** - Reseta o timer quando o usuário está ativo
- ✅ **Páginas excluídas** - Admin, chat e suporte não têm auto-refresh
- ✅ **Interface de controle** - Botão flutuante para configurações
- ✅ **Atalho de teclado** - Ctrl+Shift+R para abrir configurações
- ✅ **Persistência** - Configurações salvas no localStorage
- ✅ **Modo escuro** - Suporte completo ao tema escuro

## 🚀 Como Usar

### Interface Visual

1. **Botão Flutuante**: No canto inferior direito da página, você verá um botão roxo com ícone de sincronização
2. **Clique no botão** para abrir o painel de configurações
3. **Configure as opções**:
   - Ativar/Desativar auto-refresh
   - Escolher intervalo (1 min a 1 hora)
   - Mostrar aviso antes de atualizar
   - Pausar durante atividade do usuário
4. **Clique em "Aplicar Configurações"** para salvar

### Atalho de Teclado

Pressione **Ctrl+Shift+R** para abrir rapidamente o painel de configurações.

### Via Console JavaScript

Você também pode controlar o auto-refresh via console do navegador:

```javascript
// Ativar auto-refresh
AutoRefresh.enable();

// Desativar auto-refresh
AutoRefresh.disable();

// Definir intervalo (em milissegundos)
AutoRefresh.setInterval(300000); // 5 minutos

// Ver configurações atuais
AutoRefresh.getConfig();

// Atualizar múltiplas configurações
AutoRefresh.updateConfig({
    enabled: true,
    interval: 600000, // 10 minutos
    showWarning: true,
    pauseOnActivity: true
});
```

## ⚙️ Configurações Disponíveis

### Intervalos Pré-definidos

- **1 minuto** - 60.000ms
- **2 minutos** - 120.000ms
- **5 minutos** - 300.000ms (padrão)
- **10 minutos** - 600.000ms
- **15 minutos** - 900.000ms
- **30 minutos** - 1.800.000ms
- **1 hora** - 3.600.000ms

### Opções

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `enabled` | Ativa/desativa o auto-refresh | `false` |
| `interval` | Intervalo entre atualizações (ms) | `300000` (5 min) |
| `showWarning` | Mostra aviso antes de recarregar | `true` |
| `warningTime` | Tempo de aviso (ms) | `10000` (10s) |
| `pauseOnActivity` | Pausa timer durante atividade | `true` |

## 🚫 Páginas Excluídas

Por padrão, o auto-refresh **NÃO** funciona nas seguintes páginas:

- `/admin/` - Painel administrativo
- `/chat/` - Sistema de chat
- `/support/` - Sistema de suporte

Isso evita interrupções em áreas críticas do sistema.

## 🎨 Aviso de Atualização

Quando o timer está prestes a expirar, um aviso elegante aparece no canto superior direito com:

- **Contador regressivo** - Mostra quantos segundos faltam
- **Botão Cancelar** - Cancela a atualização e reseta o timer
- **Botão Atualizar Agora** - Atualiza imediatamente

## 💾 Persistência de Dados

Todas as configurações são salvas automaticamente no `localStorage` do navegador, então suas preferências são mantidas entre sessões.

## 🔧 Personalização Avançada

### Modificar Páginas Excluídas

Edite o arquivo `static/js/auto-refresh.js` e modifique o array `excludePages`:

```javascript
const CONFIG = {
    // ...
    excludePages: ['/admin/', '/chat/', '/support/', '/sua-pagina/'],
    // ...
};
```

### Alterar Tempo de Aviso

```javascript
const CONFIG = {
    // ...
    warningTime: 15000, // 15 segundos
    // ...
};
```

## 🐛 Solução de Problemas

### Auto-refresh não está funcionando

1. Verifique se está ativado no painel de configurações
2. Verifique se não está em uma página excluída
3. Abra o console e digite `AutoRefresh.getConfig()` para ver o status
4. Limpe o cache do navegador e recarregue a página

### Aviso não aparece

1. Verifique se "Mostrar aviso antes de atualizar" está marcado
2. Verifique se não há bloqueadores de pop-up ativos
3. Teste com `AutoRefresh.updateConfig({ showWarning: true })`

### Timer reseta constantemente

Se você marcou "Pausar durante atividade", o timer reseta quando detecta atividade do usuário (mouse, teclado, scroll). Desmarque essa opção se não quiser esse comportamento.

## 📱 Compatibilidade

- ✅ Chrome/Edge (versões recentes)
- ✅ Firefox (versões recentes)
- ✅ Safari (versões recentes)
- ✅ Opera (versões recentes)
- ✅ Dispositivos móveis (iOS/Android)

## 🎯 Casos de Uso

### Dashboard de Monitoramento

Configure para 1-2 minutos para manter dados sempre atualizados:

```javascript
AutoRefresh.updateConfig({
    enabled: true,
    interval: 120000, // 2 minutos
    showWarning: false, // Sem aviso
    pauseOnActivity: false // Sempre atualiza
});
```

### Página de Notícias

Configure para 5-10 minutos com aviso:

```javascript
AutoRefresh.updateConfig({
    enabled: true,
    interval: 600000, // 10 minutos
    showWarning: true,
    pauseOnActivity: true
});
```

### Desativar Completamente

```javascript
AutoRefresh.disable();
```

## 📝 Notas Importantes

- O auto-refresh é **desativado por padrão** para não interferir com a experiência do usuário
- Usuários devem ativar manualmente através do painel de configurações
- As configurações são específicas por navegador/dispositivo
- O sistema respeita a atividade do usuário para evitar perda de dados em formulários

## 🔐 Segurança

- Não há coleta de dados pessoais
- Todas as configurações são armazenadas localmente no navegador
- Não há comunicação com servidores externos
- O código é open-source e auditável

## 📞 Suporte

Se você encontrar problemas ou tiver sugestões, entre em contato através do sistema de suporte do site.

---

**Desenvolvido para Job Finder** 🚀
