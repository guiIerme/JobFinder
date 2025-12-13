/**
 * Enhanced Dark Mode JavaScript
 * Melhorias para o modo escuro com correções de visibilidade
 */

(function() {
    'use strict';

    // Configurações do modo escuro
    const DARK_MODE_CONFIG = {
        storageKey: 'theme',
        defaultTheme: 'light',
        transitionDuration: 300,
        autoDetectPreference: true
    };

    // Elementos que precisam de atenção especial no modo escuro
    const SPECIAL_ELEMENTS = {
        images: 'img:not([data-dark-mode-ignore])',
        videos: 'video:not([data-dark-mode-ignore])',
        iframes: 'iframe:not([data-dark-mode-ignore])',
        svgs: 'svg:not([data-dark-mode-ignore])',
        canvases: 'canvas:not([data-dark-mode-ignore])'
    };

    class DarkModeManager {
        constructor() {
            this.currentTheme = this.getStoredTheme();
            this.systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.transitionTimeout = null;
            
            this.init();
        }

        init() {
            // Aplicar tema inicial
            this.applyTheme(this.currentTheme, false);
            
            // Configurar listeners
            this.setupEventListeners();
            
            // Configurar observador de mudanças no sistema
            this.setupSystemThemeObserver();
            
            // Configurar observador de mutações DOM
            this.setupDOMObserver();
            
            // Processar elementos especiais
            this.processSpecialElements();
            
            // Configurar transições suaves
            this.setupSmoothTransitions();
        }

        getStoredTheme() {
            const stored = localStorage.getItem(DARK_MODE_CONFIG.storageKey);
            if (stored && ['light', 'dark'].includes(stored)) {
                return stored;
            }
            
            // Fallback para compatibilidade com versão anterior
            const oldDarkMode = localStorage.getItem('darkMode');
            if (oldDarkMode === 'true') {
                return 'dark';
            }
            
            // Auto-detectar preferência do sistema se habilitado
            if (DARK_MODE_CONFIG.autoDetectPreference && this.systemPrefersDark) {
                return 'dark';
            }
            
            return DARK_MODE_CONFIG.defaultTheme;
        }

        setStoredTheme(theme) {
            localStorage.setItem(DARK_MODE_CONFIG.storageKey, theme);
            
            // Manter compatibilidade com versão anterior
            localStorage.setItem('darkMode', theme === 'dark' ? 'true' : 'false');
        }

        applyTheme(theme, withTransition = true) {
            const html = document.documentElement;
            const body = document.body;
            
            // Adicionar classe de transição se necessário
            if (withTransition) {
                body.classList.add('theme-transitioning');
                
                // Remover classe após transição
                clearTimeout(this.transitionTimeout);
                this.transitionTimeout = setTimeout(() => {
                    body.classList.remove('theme-transitioning');
                }, DARK_MODE_CONFIG.transitionDuration);
            }
            
            // Aplicar tema
            html.setAttribute('data-theme', theme);
            body.setAttribute('data-theme', theme);
            
            // Atualizar botão de toggle
            this.updateToggleButton(theme);
            
            // Processar elementos especiais
            this.processSpecialElements();
            
            // Aplicar correções específicas
            this.applyThemeSpecificFixes(theme);
            
            // Disparar evento customizado
            this.dispatchThemeChangeEvent(theme);
            
            this.currentTheme = theme;
        }

        updateToggleButton(theme) {
            const toggleBtn = document.getElementById('darkModeToggle');
            if (!toggleBtn) return;

            const icon = toggleBtn.querySelector('i');
            const text = toggleBtn.querySelector('span');

            if (theme === 'dark') {
                if (icon) icon.className = 'fas fa-sun me-1';
                if (text) text.textContent = 'Claro';
                toggleBtn.classList.remove('btn-outline-light');
                toggleBtn.classList.add('btn-outline-warning');
                toggleBtn.setAttribute('title', 'Alternar para modo claro');
            } else {
                if (icon) icon.className = 'fas fa-moon me-1';
                if (text) text.textContent = 'Escuro';
                toggleBtn.classList.remove('btn-outline-warning');
                toggleBtn.classList.add('btn-outline-light');
                toggleBtn.setAttribute('title', 'Alternar para modo escuro');
            }
        }

        processSpecialElements() {
            // Processar imagens
            this.processImages();
            
            // Processar SVGs
            this.processSVGs();
            
            // Processar elementos com background-image
            this.processBackgroundImages();
            
            // Processar elementos de código
            this.processCodeElements();
            
            // Processar elementos de formulário
            this.processFormElements();
        }

        processImages() {
            const images = document.querySelectorAll(SPECIAL_ELEMENTS.images);
            
            images.forEach(img => {
                if (this.currentTheme === 'dark') {
                    // Aplicar filtro para modo escuro se a imagem não tiver versão dark específica
                    if (!img.dataset.darkSrc && !img.classList.contains('no-dark-filter')) {
                        img.style.filter = 'brightness(0.8) contrast(1.1)';
                    }
                    
                    // Trocar src se houver versão dark
                    if (img.dataset.darkSrc) {
                        if (!img.dataset.originalSrc) {
                            img.dataset.originalSrc = img.src;
                        }
                        img.src = img.dataset.darkSrc;
                    }
                } else {
                    // Remover filtros
                    img.style.filter = '';
                    
                    // Restaurar src original
                    if (img.dataset.originalSrc) {
                        img.src = img.dataset.originalSrc;
                    }
                }
            });
        }

        processSVGs() {
            const svgs = document.querySelectorAll(SPECIAL_ELEMENTS.svgs);
            
            svgs.forEach(svg => {
                if (this.currentTheme === 'dark') {
                    // Aplicar filtro para SVGs no modo escuro
                    if (!svg.classList.contains('no-dark-filter')) {
                        svg.style.filter = 'invert(0.9) hue-rotate(180deg)';
                    }
                } else {
                    svg.style.filter = '';
                }
            });
        }

        processBackgroundImages() {
            const elements = document.querySelectorAll('[style*="background-image"]');
            
            elements.forEach(el => {
                if (this.currentTheme === 'dark') {
                    if (!el.classList.contains('no-dark-filter')) {
                        el.style.filter = 'brightness(0.7) contrast(1.2)';
                    }
                } else {
                    el.style.filter = '';
                }
            });
        }

        processCodeElements() {
            const codeElements = document.querySelectorAll('code, pre, kbd');
            
            codeElements.forEach(el => {
                if (this.currentTheme === 'dark') {
                    el.classList.add('dark-mode-code');
                } else {
                    el.classList.remove('dark-mode-code');
                }
            });
        }

        processFormElements() {
            const formElements = document.querySelectorAll('input, textarea, select');
            
            formElements.forEach(el => {
                if (this.currentTheme === 'dark') {
                    // Garantir que elementos de formulário tenham o color-scheme correto
                    el.style.colorScheme = 'dark';
                } else {
                    el.style.colorScheme = 'light';
                }
            });
        }

        applyThemeSpecificFixes(theme) {
            if (theme === 'dark') {
                this.applyDarkModeFixes();
            } else {
                this.removeDarkModeFixes();
            }
        }

        applyDarkModeFixes() {
            // Corrigir elementos com texto branco em fundo branco
            const problematicElements = document.querySelectorAll('.text-white, .bg-white');
            
            problematicElements.forEach(el => {
                if (el.classList.contains('text-white') && !el.closest('.bg-dark, .bg-primary, .bg-secondary')) {
                    el.classList.add('dark-mode-text-fix');
                }
            });

            // Corrigir dropdowns do Bootstrap
            const dropdowns = document.querySelectorAll('.dropdown-menu');
            dropdowns.forEach(dropdown => {
                dropdown.classList.add('dark-mode-dropdown');
            });

            // Corrigir modais
            const modals = document.querySelectorAll('.modal-content');
            modals.forEach(modal => {
                modal.classList.add('dark-mode-modal');
            });

            // Corrigir tooltips e popovers
            const tooltips = document.querySelectorAll('.tooltip, .popover');
            tooltips.forEach(tooltip => {
                tooltip.classList.add('dark-mode-tooltip');
            });
        }

        removeDarkModeFixes() {
            // Remover classes de correção
            const fixedElements = document.querySelectorAll('.dark-mode-text-fix, .dark-mode-dropdown, .dark-mode-modal, .dark-mode-tooltip');
            
            fixedElements.forEach(el => {
                el.classList.remove('dark-mode-text-fix', 'dark-mode-dropdown', 'dark-mode-modal', 'dark-mode-tooltip');
            });
        }

        setupEventListeners() {
            // Listener para o botão de toggle
            const toggleBtn = document.getElementById('darkModeToggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => {
                    this.toggleTheme();
                });
            }

            // Listener para atalho de teclado (Ctrl+Shift+D)
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });

            // Listener para mudanças de visibilidade da página
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    // Reprocessar elementos quando a página volta a ficar visível
                    setTimeout(() => {
                        this.processSpecialElements();
                    }, 100);
                }
            });
        }

        setupSystemThemeObserver() {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addEventListener('change', (e) => {
                this.systemPrefersDark = e.matches;
                
                // Se o usuário não definiu uma preferência manual, seguir o sistema
                if (DARK_MODE_CONFIG.autoDetectPreference && !localStorage.getItem(DARK_MODE_CONFIG.storageKey)) {
                    const newTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(newTheme);
                }
            });
        }

        setupDOMObserver() {
            // Observar mudanças no DOM para processar novos elementos
            const observer = new MutationObserver((mutations) => {
                let shouldReprocess = false;
                
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        // Verificar se foram adicionados elementos que precisam de processamento
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                const hasSpecialElements = 
                                    node.matches && (
                                        node.matches(SPECIAL_ELEMENTS.images) ||
                                        node.matches(SPECIAL_ELEMENTS.svgs) ||
                                        node.querySelector(SPECIAL_ELEMENTS.images) ||
                                        node.querySelector(SPECIAL_ELEMENTS.svgs)
                                    );
                                
                                if (hasSpecialElements) {
                                    shouldReprocess = true;
                                }
                            }
                        });
                    }
                });
                
                if (shouldReprocess) {
                    // Debounce para evitar processamento excessivo
                    clearTimeout(this.reprocessTimeout);
                    this.reprocessTimeout = setTimeout(() => {
                        this.processSpecialElements();
                    }, 100);
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }

        setupSmoothTransitions() {
            // Adicionar CSS para transições suaves
            const style = document.createElement('style');
            style.textContent = `
                .theme-transitioning * {
                    transition: background-color ${DARK_MODE_CONFIG.transitionDuration}ms ease,
                                color ${DARK_MODE_CONFIG.transitionDuration}ms ease,
                                border-color ${DARK_MODE_CONFIG.transitionDuration}ms ease,
                                box-shadow ${DARK_MODE_CONFIG.transitionDuration}ms ease !important;
                }
                
                .dark-mode-text-fix {
                    color: var(--dark-text-primary) !important;
                }
                
                .dark-mode-dropdown {
                    background-color: var(--dark-bg-elevated) !important;
                    border-color: var(--dark-border) !important;
                }
                
                .dark-mode-modal {
                    background-color: var(--dark-bg-secondary) !important;
                    color: var(--dark-text-primary) !important;
                }
                
                .dark-mode-tooltip {
                    background-color: var(--dark-bg-elevated) !important;
                    color: var(--dark-text-primary) !important;
                }
                
                .dark-mode-code {
                    background-color: var(--dark-bg-tertiary) !important;
                    color: var(--dark-accent-primary) !important;
                    border-color: var(--dark-border) !important;
                }
            `;
            document.head.appendChild(style);
        }

        toggleTheme() {
            const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
            this.setStoredTheme(newTheme);
            this.applyTheme(newTheme);
        }

        dispatchThemeChangeEvent(theme) {
            const event = new CustomEvent('themechange', {
                detail: { theme, previousTheme: this.currentTheme }
            });
            document.dispatchEvent(event);
        }

        // Métodos públicos para uso externo
        getCurrentTheme() {
            return this.currentTheme;
        }

        setTheme(theme) {
            if (['light', 'dark'].includes(theme)) {
                this.setStoredTheme(theme);
                this.applyTheme(theme);
            }
        }

        isSystemDarkMode() {
            return this.systemPrefersDark;
        }
    }

    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.darkModeManager = new DarkModeManager();
        });
    } else {
        window.darkModeManager = new DarkModeManager();
    }

    // Expor funcionalidades globalmente para compatibilidade
    window.toggleDarkMode = function() {
        if (window.darkModeManager) {
            window.darkModeManager.toggleTheme();
        }
    };

    window.setTheme = function(theme) {
        if (window.darkModeManager) {
            window.darkModeManager.setTheme(theme);
        }
    };

    // Listener para eventos de tema de outros componentes
    document.addEventListener('themechange', (e) => {
        console.log(`Tema alterado para: ${e.detail.theme}`);
        
        // Notificar outros componentes se necessário
        if (window.chatWidget) {
            window.chatWidget.updateTheme(e.detail.theme);
        }
        
        if (window.accessibilityAssistant) {
            window.accessibilityAssistant.updateTheme(e.detail.theme);
        }
    });

})();