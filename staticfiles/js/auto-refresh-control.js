/**
 * Controle de Auto-Refresh
 * Interface para configurar o sistema de auto-refresh
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Aguarda o AutoRefresh estar disponível
    const checkAutoRefresh = setInterval(() => {
        if (window.AutoRefresh) {
            clearInterval(checkAutoRefresh);
            initControls();
        }
    }, 100);

    function initControls() {
        const config = window.AutoRefresh.getConfig();

        // Cria botão de controle flutuante
        createFloatingControl(config);

        // Adiciona atalho de teclado (Ctrl+Shift+R)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                e.preventDefault();
                toggleControlPanel();
            }
        });
    }

    function createFloatingControl(config) {
        // Verifica se já existe
        if (document.getElementById('auto-refresh-control')) {
            return;
        }

        const control = document.createElement('div');
        control.id = 'auto-refresh-control';
        control.innerHTML = `
            <button id="auto-refresh-toggle-btn" class="floating-control-btn" title="Configurar Auto-Refresh (Ctrl+Shift+R)">
                <i class="fas fa-sync-alt"></i>
            </button>
            
            <div id="auto-refresh-panel" class="control-panel" style="display: none;">
                <div class="panel-header">
                    <h4><i class="fas fa-cog"></i> Auto-Refresh</h4>
                    <button id="close-panel-btn" class="close-btn">&times;</button>
                </div>
                
                <div class="panel-body">
                    <div class="control-group">
                        <label class="switch-label">
                            <input type="checkbox" id="enable-refresh" ${config.enabled ? 'checked' : ''}>
                            <span class="switch-slider"></span>
                            <span class="switch-text">Ativar Auto-Refresh</span>
                        </label>
                    </div>
                    
                    <div class="control-group">
                        <label for="refresh-interval">Intervalo de Atualização</label>
                        <select id="refresh-interval" class="form-select">
                            <option value="60000" ${config.interval === 60000 ? 'selected' : ''}>1 minuto</option>
                            <option value="120000" ${config.interval === 120000 ? 'selected' : ''}>2 minutos</option>
                            <option value="300000" ${config.interval === 300000 ? 'selected' : ''}>5 minutos</option>
                            <option value="600000" ${config.interval === 600000 ? 'selected' : ''}>10 minutos</option>
                            <option value="900000" ${config.interval === 900000 ? 'selected' : ''}>15 minutos</option>
                            <option value="1800000" ${config.interval === 1800000 ? 'selected' : ''}>30 minutos</option>
                            <option value="3600000" ${config.interval === 3600000 ? 'selected' : ''}>1 hora</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="show-warning" ${config.showWarning ? 'checked' : ''}>
                            <span>Mostrar aviso antes de atualizar</span>
                        </label>
                    </div>
                    
                    <div class="control-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="pause-on-activity" ${config.pauseOnActivity ? 'checked' : ''}>
                            <span>Pausar durante atividade</span>
                        </label>
                    </div>
                    
                    <div class="control-group">
                        <button id="apply-settings-btn" class="btn-apply">
                            <i class="fas fa-check"></i> Aplicar Configurações
                        </button>
                    </div>
                    
                    <div class="info-box">
                        <i class="fas fa-info-circle"></i>
                        <small>Use Ctrl+Shift+R para abrir este painel rapidamente</small>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(control);

        // Adiciona estilos
        addStyles();

        // Event listeners
        setupEventListeners();
    }

    function addStyles() {
        const style = document.crent('style');
        style.textContent = `
            #auto-refresh-control {
                position: fixed;
                bottom: 80px;
                right: 20px;
                z-index: 9999;
            }
            
            .floating-control-btn {
                width: 56px;
                height: 56px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .floating-control-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            .floating-control-btn i {
                animation: rotate 3s linear infinite;
            }
            
            @keyframes rotate {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            .control-panel {
                position: absolute;
                bottom: 70px;
                right: 0;
                width: 350px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                animation: slideUp 0.3s ease;
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .panel-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .panel-header h4 {
                margin: 0;
                font-size: 18px;
                color: #333;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .close-btn {
                background: none;
                border: none;
                font-size: 24px;
                color: #999;
                cursor: pointer;
                transition: color 0.3s;
            }
            
            .close-btn:hover {
                color: #333;
            }
            
            .panel-body {
                padding: 20px;
            }
            
            .control-group {
                margin-bottom: 20px;
            }
            
            .control-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #555;
                font-size: 14px;
            }
            
            .form-select {
                width: 100%;
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            
            .form-select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .switch-label {
                display: flex;
                align-items: center;
                cursor: pointer;
                user-select: none;
            }
            
            .switch-label input[type="checkbox"] {
                display: none;
            }
            
            .switch-slider {
                position: relative;
                width: 50px;
                height: 26px;
                background: #ccc;
                border-radius: 13px;
                transition: background 0.3s;
                margin-right: 12px;
            }
            
            .switch-slider::before {
                content: '';
                position: absolute;
                width: 20px;
                height: 20px;
                background: white;
                border-radius: 50%;
                top: 3px;
                left: 3px;
                transition: transform 0.3s;
            }
            
            .switch-label input:checked + .switch-slider {
                background: #667eea;
            }
            
            .switch-label input:checked + .switch-slider::before {
                transform: translateX(24px);
            }
            
            .switch-text {
                font-weight: 500;
                color: #333;
            }
            
            .checkbox-label {
                display: flex;
                align-items: center;
                cursor: pointer;
                user-select: none;
            }
            
            .checkbox-label input[type="checkbox"] {
                margin-right: 10px;
                width: 18px;
                height: 18px;
                cursor: pointer;
            }
            
            .btn-apply {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 14px;
            }
            
            .btn-apply:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            .info-box {
                background: #f5f5f5;
                padding: 12px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                gap: 10px;
                margin-top: 15px;
            }
            
            .info-box i {
                color: #667eea;
                font-size: 16px;
            }
            
            .info-box small {
                color: #666;
                font-size: 12px;
            }
            
            /* Dark mode support */
            [data-theme="dark"] .control-panel {
                background: #2d2d2d;
            }
            
            [data-theme="dark"] .panel-header {
                border-bottom-color: #444;
            }
            
            [data-theme="dark"] .panel-header h4,
            [data-theme="dark"] .switch-text,
            [data-theme="dark"] .checkbox-label span {
                color: #e0e0e0;
            }
            
            [data-theme="dark"] .control-group label {
                color: #ccc;
            }
            
            [data-theme="dark"] .form-select {
                background: #3d3d3d;
                color: #e0e0e0;
                border-color: #555;
            }
            
            [data-theme="dark"] .info-box {
                background: #3d3d3d;
            }
            
            [data-theme="dark"] .info-box small {
                color: #aaa;
            }
        `;
        document.head.appendChild(style);
    }

    function setupEventListeners() {
        const toggleBtn = document.getElementById('auto-refresh-toggle-btn');
        const closeBtn = document.getElementById('close-panel-btn');
        const panel = document.getElementById('auto-refresh-panel');
        const applyBtn = document.getElementById('apply-settings-btn');

        toggleBtn.addEventListener('click', toggleControlPanel);
        closeBtn.addEventListener('click', () => {
            panel.style.display = 'none';
        });

        applyBtn.addEventListener('click', applySettings);

        // Fecha o painel ao clicar fora
        document.addEventListener('click', function(e) {
            if (!e.target.closest('#auto-refresh-control')) {
                panel.style.display = 'none';
            }
        });
    }

    function toggleControlPanel() {
        const panel = document.getElementById('auto-refresh-panel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }

    function applySettings() {
        const enabled = document.getElementById('enable-refresh').checked;
        const interval = parseInt(document.getElementById('refresh-interval').value);
        const showWarning = document.getElementById('show-warning').checked;
        const pauseOnActivity = document.getElementById('pause-on-activity').checked;

        window.AutoRefresh.updateConfig({
            enabled: enabled,
            interval: interval,
            showWarning: showWarning,
            pauseOnActivity: pauseOnActivity
        });

        // Feedback visual
        const applyBtn = document.getElementById('apply-settings-btn');
        const originalText = applyBtn.innerHTML;
        applyBtn.innerHTML = '<i class="fas fa-check"></i> Configurações Salvas!';
        applyBtn.style.background = '#28a745';

        setTimeout(() => {
            applyBtn.innerHTML = originalText;
            applyBtn.style.background = '';
            document.getElementById('auto-refresh-panel').style.display = 'none';
        }, 2000);
    }
});
eat