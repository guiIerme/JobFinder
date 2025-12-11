/**
 * Auto Refresh System
 * Recarrega a página automaticamente após um período configurável
 */

(function() {
    'use strict';

    // Configurações
    const CONFIG = {
        enabled: false, // Ativar/desativar auto-refresh
        interval: 300000, // Intervalo em milissegundos (padrão: 5 minutos = 300000ms)
        showWarning: true, // Mostrar aviso antes de recarregar
        warningTime: 10000, // Tempo de aviso antes do refresh (10 segundos)
        excludePages: ['/admin/', '/chat/', '/support/'], // Páginas que não devem ter auto-refresh
        pauseOnActivity: true, // Pausar timer quando houver atividade do usuário
        storageKey: 'autoRefreshSettings'
    };

    let refreshTimer = null;
    let warningTimer = null;
    let lastActivity = Date.now();
    let warningElement = null;

    /**
     * Verifica se a página atual deve ter auto-refresh
     */
    function shouldEnableAutoRefresh() {
        const currentPath = window.location.pathname;

        // Verifica se está em uma página excluída
        for (let excludePath of CONFIG.excludePages) {
            if (currentPath.includes(excludePath)) {
                return false;
            }
        }

        return true;
    }

    /**
     * Carrega configurações do localStorage
     */
    function loadSettings() {
        try {
            const saved = localStorage.getItem(CONFIG.storageKey);
            if (saved) {
                const settings = JSON.parse(saved);
                Object.assign(CONFIG, settings);
            }
        } catch (e) {
            console.warn('Erro ao carregar configurações de auto-refresh:', e);
        }
    }

    /**
     * Salva configurações no localStorage
     */
    function saveSettings() {
        try {
            localStorage.setItem(CONFIG.storageKey, JSON.stringify({
                enabled: CONFIG.enabled,
                interval: CONFIG.interval,
                showWarning: CONFIG.showWarning,
                warningTime: CONFIG.warningTime,
                pauseOnActivity: CONFIG.pauseOnActivity
            }));
        } catch (e) {
            console.warn('Erro ao salvar configurações de auto-refresh:', e);
        }
    }

    /**
     * Cria elemento de aviso
     */
    function createWarningElement() {
        const div = document.createElement('div');
        div.id = 'auto-refresh-warning';
        div.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 10000;
            display: none;
            min-width: 320px;
            animation: slideInRight 0.5s ease;
        `;

        div.innerHTML = `
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <i class="fas fa-sync-alt" style="font-size: 24px; margin-right: 12px; animation: spin 2s linear infinite;"></i>
                <div>
                    <strong style="display: block; font-size: 16px;">Atualização Automática</strong>
                    <span style="font-size: 13px; opacity: 0.9;">A página será recarregada em <span id="refresh-countdown">10</span>s</span>
                </div>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button id="cancel-refresh-btn" style="
                    flex: 1;
                    background: rgba(255,255,255,0.2);
                    border: 1px solid rgba(255,255,255,0.3);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s;
                ">
                    <i class="fas fa-times"></i> Cancelar
                </button>
                <button id="refresh-now-btn" style="
                    flex: 1;
                    background: rgba(255,255,255,0.9);
                    border: none;
                    color: #667eea;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 14px;
                    transition: all 0.3s;
                ">
                    <i class="fas fa-sync"></i> Atualizar Agora
                </button>
            </div>
        `;

        document.body.appendChild(div);
        return div;
    }

    /**
     * Mostra aviso de refresh
     */
    function showWarning() {
        if (!CONFIG.showWarning) {
            performRefresh();
            return;
        }

        if (!warningElement) {
            warningElement = createWarningElement();
        }

        warningElement.style.display = 'block';

        let countdown = Math.floor(CONFIG.warningTime / 1000);
        const countdownElement = document.getElementById('refresh-countdown');

        const countdownInterval = setInterval(() => {
            countdown--;
            if (countdownElement) {
                countdownElement.textContent = countdown;
            }

            if (countdown <= 0) {
                clearInterval(countdownInterval);
                performRefresh();
            }
        }, 1000);

        // Botão cancelar
        document.getElementById('cancel-refresh-btn').onclick = () => {
            clearInterval(countdownInterval);
            hideWarning();
            resetTimer();
        };

        // Botão atualizar agora
        document.getElementById('refresh-now-btn').onclick = () => {
            clearInterval(countdownInterval);
            performRefresh();
        };
    }

    /**
     * Esconde aviso
     */
    function hideWarning() {
        if (warningElement) {
            warningElement.style.display = 'none';
        }
    }

    /**
     * Executa o refresh da página
     */
    function performRefresh() {
        console.log('Auto-refresh: Recarregando página...');
        window.location.reload();
    }

    /**
     * Inicia o timer de refresh
     */
    function startTimer() {
        if (!CONFIG.enabled || !shouldEnableAutoRefresh()) {
            return;
        }

        clearTimers();

        const timeUntilWarning = CONFIG.interval - CONFIG.warningTime;

        refreshTimer = setTimeout(() => {
            showWarning();
        }, timeUntilWarning);

        console.log(`Auto-refresh ativado. Próxima atualização em ${CONFIG.interval / 1000} segundos.`);
    }

    /**
     * Reseta o timer
     */
    function resetTimer() {
        if (CONFIG.pauseOnActivity) {
            const timeSinceActivity = Date.now() - lastActivity;

            // Se houve atividade recente (últimos 30 segundos), reseta o timer
            if (timeSinceActivity < 30000) {
                clearTimers();
                startTimer();
            }
        }
    }

    /**
     * Limpa todos os timers
     */
    function clearTimers() {
        if (refreshTimer) {
            clearTimeout(refreshTimer);
            refreshTimer = null;
        }
        if (warningTimer) {
            clearTimeout(warningTimer);
            warningTimer = null;
        }
    }

    /**
     * Registra atividade do usuário
     */
    function registerActivity() {
        lastActivity = Date.now();
    }

    /**
     * Inicializa o sistema
     */
    function init() {
        loadSettings();

        // Eventos de atividade do usuário
        if (CONFIG.pauseOnActivity) {
            ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
                document.addEventListener(event, registerActivity, {
                    passive: true
                });
            });
        }

        // Inicia o timer
        startTimer();

        // Adiciona estilos de animação
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            #auto-refresh-warning button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * API pública
     */
    window.AutoRefresh = {
        enable: function() {
            CONFIG.enabled = true;
            saveSettings();
            startTimer();
            console.log('Auto-refresh ativado');
        },

        disable: function() {
            CONFIG.enabled = false;
            saveSettings();
            clearTimers();
            hideWarning();
            console.log('Auto-refresh desativado');
        },

        setInterval: function(milliseconds) {
            CONFIG.interval = milliseconds;
            saveSettings();
            if (CONFIG.enabled) {
                startTimer();
            }
            console.log(`Intervalo de auto-refresh definido para ${milliseconds / 1000} segundos`);
        },

        getConfig: function() {
            return {
                ...CONFIG
            };
        },

        updateConfig: function(newConfig) {
            Object.assign(CONFIG, newConfig);
            saveSettings();
            if (CONFIG.enabled) {
                startTimer();
            }
        }
    };

    // Inicializa quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();