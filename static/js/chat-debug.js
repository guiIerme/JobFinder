/**
 * Chat Debug Script
 * 
 * Este script adiciona logs de debug para ajudar a identificar problemas
 * com o chat widget.
 */

console.log('🔍 Chat Debug Script carregado');

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DOM carregado, verificando elementos do chat...');

    // Verificar botão do widget
    const toggleButton = document.getElementById('chat-widget-toggle');
    if (toggleButton) {
        console.log('✅ Botão do chat encontrado:', toggleButton);
        console.log('   - Display:', window.getComputedStyle(toggleButton).display);
        console.log('   - Visibility:', window.getComputedStyle(toggleButton).visibility);
        console.log('   - Position:', window.getComputedStyle(toggleButton).position);
    } else {
        console.error('❌ Botão do chat NÃO encontrado! ID: chat-widget-toggle');
    }

    // Verificar janela do chat
    const chatWindow = document.getElementById('chat-window');
    if (chatWindow) {
        console.log('✅ Janela do chat encontrada:', chatWindow);
    } else {
        console.error('❌ Janela do chat NÃO encontrada! ID: chat-window');
    }

    // Verificar se os scripts foram carregados
    setTimeout(() => {
        if (window.chatWidget) {
            console.log('✅ ChatWidget inicializado:', window.chatWidget);
        } else {
            console.error('❌ ChatWidget NÃO inicializado!');
        }

        if (window.chatWindow) {
            console.log('✅ ChatWindow inicializado:', window.chatWindow);
        } else {
            console.error('❌ ChatWindow NÃO inicializado!');
        }
    }, 500);

    // Adicionar listener de clique manual para debug
    if (toggleButton) {
        toggleButton.addEventListener('click', function(e) {
            console.log('🖱️ Botão do chat clicado!', e);
            console.log('   - chatWidget existe?', !!window.chatWidget);
            console.log('   - chatWindow existe?', !!window.chatWindow);
        }, true); // Use capture phase para pegar o evento primeiro
    }

    // Monitorar eventos do chat
    document.addEventListener('chat:widget-toggle', function(e) {
        console.log('📢 Evento chat:widget-toggle disparado', e.detail);
    });

    document.addEventListener('chat:open-requested', function(e) {
        console.log('📢 Evento chat:open-requested disparado', e.detail);
    });

    document.addEventListener('chat:opened', function(e) {
        console.log('📢 Evento chat:opened disparado', e.detail);
    });

    document.addEventListener('chat:closed', function(e) {
        console.log('📢 Evento chat:closed disparado', e.detail);
    });

    console.log('🔍 Debug setup completo. Abra o console (F12) para ver os logs.');
});