/**
 * Username Field Fix JavaScript
 * Correção específica para garantir que o campo username apareça no mobile
 */

(function() {
    'use strict';

    // Configurações
    const CONFIG = {
        checkInterval: 100, // ms
        maxChecks: 50, // máximo de verificações
        debugMode: false // ativar para debug
    };

    let checkCount = 0;

    function log(message, data = null) {
        if (CONFIG.debugMode) {
            console.log('[Username Fix]', message, data);
        }
    }

    function ensureUsernameFieldVisibility() {
        const usernameField = document.getElementById('username');
        const usernameContainer = usernameField ? usernameField.closest('.mb-3') : null;
        const inputGroup = usernameField ? usernameField.closest('.input-group') : null;
        
        log('Checking username field visibility', {
            field: !!usernameField,
            container: !!usernameContainer,
            inputGroup: !!inputGroup
        });

        if (!usernameField) {
            log('Username field not found in DOM');
            return false;
        }

        // Verificar se o campo está visível
        const fieldStyles = window.getComputedStyle(usernameField);
        const containerStyles = usernameContainer ? window.getComputedStyle(usernameContainer) : null;
        
        const isFieldVisible = (
            fieldStyles.display !== 'none' &&
            fieldStyles.visibility !== 'hidden' &&
            fieldStyles.opacity !== '0' &&
            usernameField.offsetWidth > 0 &&
            usernameField.offsetHeight > 0
        );

        const isContainerVisible = !usernameContainer || (
            containerStyles.display !== 'none' &&
            containerStyles.visibility !== 'hidden' &&
            containerStyles.opacity !== '0'
        );

        log('Visibility check', {
            fieldVisible: isFieldVisible,
            containerVisible: isContainerVisible,
            fieldStyles: {
                display: fieldStyles.display,
                visibility: fieldStyles.visibility,
                opacity: fieldStyles.opacity,
                width: usernameField.offsetWidth,
                height: usernameField.offsetHeight
            }
        });

        if (!isFieldVisible || !isContainerVisible) {
            log('Field not visible, applying fixes');
            applyVisibilityFixes(usernameField, usernameContainer, inputGroup);
            return false;
        }

        log('Username field is visible');
        return true;
    }

    function applyVisibilityFixes(field, container, inputGroup) {
        // Corrigir o campo
        if (field) {
            field.style.display = 'block';
            field.style.visibility = 'visible';
            field.style.opacity = '1';
            field.style.position = 'relative';
            field.style.zIndex = '1';
            field.style.width = '100%';
            field.style.height = 'auto';
            field.style.minHeight = '44px';
            field.style.fontSize = '16px';
            field.style.padding = '12px 15px';
            field.style.border = '2px solid #e9ecef';
            field.style.borderRadius = '0 8px 8px 0';
            field.style.backgroundColor = '#fff';
            field.style.color = '#495057';
            field.style.boxSizing = 'border-box';
            
            // Garantir atributos corretos
            field.setAttribute('type', 'text');
            field.setAttribute('name', 'username');
            field.setAttribute('id', 'username');
            field.setAttribute('required', 'required');
            
            if (!field.placeholder) {
                field.placeholder = 'Escolha um nome de usuário';
            }
        }

        // Corrigir o container
        if (container) {
            container.style.display = 'block';
            container.style.visibility = 'visible';
            container.style.opacity = '1';
            container.style.position = 'relative';
            container.style.zIndex = '1';
            container.style.marginBottom = '1rem';
        }

        // Corrigir o input-group
        if (inputGroup) {
            inputGroup.style.display = 'flex';
            inputGroup.style.visibility = 'visible';
            inputGroup.style.opacity = '1';
            inputGroup.style.position = 'relative';
            inputGroup.style.zIndex = '1';
            inputGroup.style.width = '100%';
        }

        // Corrigir o label
        const label = container ? container.querySelector('label[for="username"]') : null;
        if (label) {
            label.style.display = 'block';
            label.style.visibility = 'visible';
            label.style.opacity = '1';
            label.style.fontWeight = '600';
            label.style.color = '#495057';
            label.style.marginBottom = '0.5rem';
        }

        // Corrigir o input-group-text
        const inputGroupText = inputGroup ? inputGroup.querySelector('.input-group-text') : null;
        if (inputGroupText) {
            inputGroupText.style.display = 'flex';
            inputGroupText.style.visibility = 'visible';
            inputGroupText.style.opacity = '1';
            inputGroupText.style.alignItems = 'center';
            inputGroupText.style.justifyContent = 'center';
            inputGroupText.style.minWidth = '44px';
            inputGroupText.style.padding = '12px';
            inputGroupText.style.backgroundColor = '#f8f9fa';
            inputGroupText.style.border = '2px solid #e9ecef';
            inputGroupText.style.borderRight = 'none';
            inputGroupText.style.borderRadius = '8px 0 0 8px';
            inputGroupText.style.color = '#6c757d';
        }

        // Corrigir o form-text
        const formText = container ? container.querySelector('.form-text') : null;
        if (formText) {
            formText.style.display = 'block';
            formText.style.visibility = 'visible';
            formText.style.opacity = '1';
            formText.style.fontSize = '14px';
            formText.style.color = '#6c757d';
            formText.style.marginTop = '0.25rem';
        }

        log('Applied visibility fixes');
    }

    function addMobileSpecificStyles() {
        // Adicionar estilos CSS específicos para mobile
        const style = document.createElement('style');
        style.id = 'username-field-mobile-fix';
        style.textContent = `
            /* Username Field Mobile Fix - Inline Styles */
            @media (max-width: 768px) {
                #username {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    position: relative !important;
                    z-index: 1 !important;
                    width: 100% !important;
                    font-size: 16px !important;
                    min-height: 44px !important;
                    padding: 12px 15px !important;
                    border: 2px solid #e9ecef !important;
                    border-left: none !important;
                    border-radius: 0 8px 8px 0 !important;
                    background-color: #fff !important;
                    color: #495057 !important;
                    box-sizing: border-box !important;
                }
                
                .register-form .mb-3:has(#username),
                .register-form .mb-3:first-child {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    position: relative !important;
                    z-index: 1 !important;
                    margin-bottom: 1rem !important;
                }
                
                .register-form .input-group:has(#username) {
                    display: flex !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    position: relative !important;
                    z-index: 1 !important;
                    width: 100% !important;
                }
                
                .register-form label[for="username"] {
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    font-weight: 600 !important;
                    color: #495057 !important;
                    margin-bottom: 0.5rem !important;
                }
            }
        `;
        
        // Remover estilo anterior se existir
        const existingStyle = document.getElementById('username-field-mobile-fix');
        if (existingStyle) {
            existingStyle.remove();
        }
        
        document.head.appendChild(style);
        log('Added mobile-specific styles');
    }

    function startVisibilityCheck() {
        const checkVisibility = () => {
            checkCount++;
            
            if (checkCount > CONFIG.maxChecks) {
                log('Max checks reached, stopping');
                return;
            }

            const isVisible = ensureUsernameFieldVisibility();
            
            if (!isVisible) {
                setTimeout(checkVisibility, CONFIG.checkInterval);
            } else {
                log('Username field is now visible, stopping checks');
            }
        };

        checkVisibility();
    }

    function initUsernameFieldFix() {
        log('Initializing username field fix');
        
        // Adicionar estilos específicos
        addMobileSpecificStyles();
        
        // Iniciar verificação de visibilidade
        startVisibilityCheck();
        
        // Verificar novamente quando a orientação mudar
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                log('Orientation changed, rechecking');
                checkCount = 0;
                startVisibilityCheck();
            }, 500);
        });
        
        // Verificar quando a janela for redimensionada
        window.addEventListener('resize', () => {
            setTimeout(() => {
                ensureUsernameFieldVisibility();
            }, 100);
        });
        
        // Verificar quando o DOM mudar (MutationObserver)
        if (window.MutationObserver) {
            const observer = new MutationObserver(() => {
                ensureUsernameFieldVisibility();
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }
    }

    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUsernameFieldFix);
    } else {
        initUsernameFieldFix();
    }

    // Expor função para debug
    window.debugUsernameField = function() {
        CONFIG.debugMode = true;
        checkCount = 0;
        startVisibilityCheck();
    };

})();