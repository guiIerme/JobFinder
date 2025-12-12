// Accessibility Assistant JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize accessibility features
    initAccessibilityAssistant();
});

function initAccessibilityAssistant() {
    // Get DOM elements
    const accessibilityToggle = document.getElementById('accessibility-toggle');
    const accessibilityPanel = document.getElementById('accessibility-panel');
    const closeAccessibility = document.getElementById('close-accessibility');
    const toggleLibras = document.getElementById('toggle-libras');
    const increaseFont = document.getElementById('increase-font');
    const decreaseFont = document.getElementById('decrease-font');
    const resetFont = document.getElementById('reset-font');
    const toggleContrast = document.getElementById('toggle-contrast');
    const textReader = document.getElementById('text-reader');

    // Load saved preferences
    const isLibrasActive = false; // Disabled auto-load - user must click to activate
    const savedFontSize = localStorage.getItem('fontSize') || 100;
    const contrastMode = localStorage.getItem('contrastMode') || 'normal';

    // Clear any previous libras state to prevent auto-load
    localStorage.removeItem('librasActive');

    // Apply saved settings (Libras auto-load disabled)
    // User must manually click the Libras button to activate

    document.documentElement.style.fontSize = `${savedFontSize}%`;
    document.getElementById('font-size-display').textContent = `${savedFontSize}%`;

    if (contrastMode === 'high') {
        document.body.classList.add('high-contrast');
        document.getElementById('contrast-text').textContent = 'Alto Contraste Ativado';
        toggleContrast.classList.add('active');
    }

    // Event listeners
    accessibilityToggle.addEventListener('click', function() {
        const isVisible = accessibilityPanel.style.display === 'block';
        accessibilityPanel.style.display = isVisible ? 'none' : 'block';
        accessibilityToggle.setAttribute('aria-expanded', !isVisible);

        // If opening accessibility panel, close chat window
        if (!isVisible) {
            console.log('Accessibility panel opened, dispatching event');
            const event = new CustomEvent('accessibility:opened');
            document.dispatchEvent(event);
        }
    });

    closeAccessibility.addEventListener('click', function() {
        accessibilityPanel.style.display = 'none';
        accessibilityToggle.setAttribute('aria-expanded', false);
    });

    // Close panel when clicking outside
    document.addEventListener('click', function(event) {
        if (!accessibilityPanel.contains(event.target) &&
            event.target !== accessibilityToggle &&
            !accessibilityToggle.contains(event.target)) {
            accessibilityPanel.style.display = 'none';
            accessibilityToggle.setAttribute('aria-expanded', false);
        }
    });

    // Close accessibility panel when chat opens
    document.addEventListener('chat:opened', function() {
        if (accessibilityPanel.style.display === 'block') {
            console.log('Chat opened, closing accessibility panel');
            accessibilityPanel.style.display = 'none';
            accessibilityToggle.setAttribute('aria-expanded', false);
        }
    });

    // Libras toggle
    toggleLibras.addEventListener('click', function() {
        const isActive = this.classList.contains('active');
        const optionText = this.querySelector('.option-text');

        if (isActive) {
            // Disable Libras (Hand Talk)
            this.classList.remove('active');
            localStorage.setItem('librasActive', 'false');

            // Update button text
            if (optionText) {
                optionText.textContent = 'Libras';
            }

            // Remove Hand Talk
            const handTalkScript = document.getElementById('handtalk-script');
            if (handTalkScript) {
                handTalkScript.remove();
            }

            // Remove Hand Talk widget
            const handTalkElements = document.querySelectorAll('[class*="ht-"], [id*="ht-"], .handtalk');
            handTalkElements.forEach(element => {
                element.remove();
            });

            // Clear Hand Talk instance
            if (window.ht) {
                window.ht = null;
            }

            console.log('Hand Talk disabled successfully');
        } else {
            // Enable Libras (Hand Talk)
            console.log('Enabling Hand Talk...');
            this.classList.add('active');
            localStorage.setItem('librasActive', 'true');

            // Update button text
            if (optionText) {
                optionText.textContent = 'Carregando...';
            }

            // Load Hand Talk
            loadHandTalk();

            // Update text after loading
            setTimeout(() => {
                if (optionText) {
                    optionText.textContent = 'Libras Ativo ✓';
                }
            }, 2000);
        }
    });

    // Font size controls
    increaseFont.addEventListener('click', function() {
        adjustFontSize(10);
    });

    decreaseFont.addEventListener('click', function() {
        adjustFontSize(-10);
    });

    resetFont.addEventListener('click', function() {
        resetFontSize();
    });

    // Contrast toggle
    toggleContrast.addEventListener('click', function() {
        const isHighContrast = document.body.classList.contains('high-contrast');

        if (isHighContrast) {
            // Disable high contrast
            document.body.classList.remove('high-contrast');
            document.getElementById('contrast-text').textContent = 'Alto Contraste';
            this.classList.remove('active');
            localStorage.setItem('contrastMode', 'normal');
        } else {
            // Enable high contrast
            document.body.classList.add('high-contrast');
            document.getElementById('contrast-text').textContent = 'Alto Contraste Ativado';
            this.classList.add('active');
            localStorage.setItem('contrastMode', 'high');
        }
    });

    // Text reader
    let isReaderActive = localStorage.getItem('textReaderActive') === 'true';
    let speechSynthesis = window.speechSynthesis;
    let currentUtterance = null;

    // Apply saved state
    if (isReaderActive) {
        textReader.classList.add('active');
        enableTextReader();
    }

    textReader.addEventListener('click', function() {
        const optionText = this.querySelector('.option-text');

        if (isReaderActive) {
            // Disable text reader
            isReaderActive = false;
            this.classList.remove('active');
            localStorage.setItem('textReaderActive', 'false');

            if (optionText) {
                optionText.textContent = 'Leitor de Texto';
            }

            disableTextReader();
            console.log('Text reader disabled');
        } else {
            // Enable text reader
            isReaderActive = true;
            this.classList.add('active');
            localStorage.setItem('textReaderActive', 'true');

            if (optionText) {
                optionText.textContent = 'Leitor Ativo ✓';
            }

            enableTextReader();

            // Speak welcome message
            speakText('Leitor de texto ativado. Passe o mouse sobre qualquer texto para ouvi-lo.');
            console.log('Text reader enabled');
        }
    });
}

function adjustFontSize(change) {
    const currentSize = parseFloat(document.documentElement.style.fontSize) || 100;
    const newSize = Math.min(Math.max(currentSize + change, 80), 150);

    document.documentElement.style.fontSize = `${newSize}%`;
    document.getElementById('font-size-display').textContent = `${newSize}%`;
    localStorage.setItem('fontSize', newSize.toString());
}

function resetFontSize() {
    document.documentElement.style.fontSize = '100%';
    document.getElementById('font-size-display').textContent = '100%';
    localStorage.setItem('fontSize', '100');
}

// VLibras removed - using Hand Talk instead
function loadLibrasWidget_DEPRECATED() {
    console.log('[VLibras] Starting load process...');

    // Check if widget is already loaded
    if (document.getElementById('vlibras-plugin') || document.querySelector('[vw]')) {
        console.log('[VLibras] Widget already loaded');
        return;
    }

    console.log('[VLibras] Creating container using official method...');

    // Method 1: Try the official HTML structure
    const vLibrasHTML = `
        <div vw class="enabled">
            <div vw-access-button class="active"></div>
            <div vw-plugin-wrapper>
                <div class="vw-plugin-top-wrapper"></div>
            </div>
        </div>
    `;

    // Insert at the end of body
    document.body.insertAdjacentHTML('beforeend', vLibrasHTML);
    console.log('[VLibras] Container HTML inserted');

    // Load the VLibras script - using the full plugin version
    const script = document.createElement('script');
    script.id = 'vlibras-plugin';
    script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
    script.async = false; // Load synchronously for better initialization
    script.crossOrigin = 'anonymous';

    script.onload = function() {
        console.log('[VLibras] Script loaded successfully');
        console.log('[VLibras] Waiting for initialization...');

        // Initialize VLibras with longer delay
        setTimeout(() => {
            try {
                console.log('[VLibras] Checking if VLibras object exists...');
                console.log('[VLibras] window.VLibras:', typeof window.VLibras);

                if (typeof window.VLibras !== 'undefined') {
                    console.log('[VLibras] VLibras object found, initializing...');

                    try {
                        // Try multiple initialization methods
                        console.log('[VLibras] Attempting initialization method 1...');

                        // Method 1: Standard Widget
                        let widget = new window.VLibras.Widget('https://vlibras.gov.br/app');
                        console.log('[VLibras] Widget created:', widget);

                        // Method 2: Try to manually initialize if Widget didn't work
                        if (typeof window.VLibras.init === 'function') {
                            console.log('[VLibras] Calling VLibras.init()...');
                            window.VLibras.init();
                        }

                        // Method 3: Try Plugin if available
                        if (typeof window.VLibras.Plugin === 'function') {
                            console.log('[VLibras] Trying Plugin method...');
                            new window.VLibras.Plugin();
                        }

                        console.log('[VLibras] ✅ Initialization complete!');

                        // Wait and inspect what was created
                        setTimeout(() => {
                            const iframes = document.querySelectorAll('[vw] iframe');
                            console.log('[VLibras] Iframes found:', iframes.length);

                            if (iframes.length === 0) {
                                console.warn('[VLibras] ⚠️ No iframes found! Creating manual player...');

                                // Create a simplified VLibras player as fallback
                                console.log('[VLibras] Creating simplified player...');
                                const wrapper = document.querySelector('[vw-plugin-wrapper]');
                                if (wrapper) {
                                    const topWrapper = wrapper.querySelector('.vw-plugin-top-wrapper');
                                    if (topWrapper) {
                                        // Create a simple message with link to VLibras
                                        topWrapper.innerHTML = `
                                            <div style="padding: 30px; background: white; border-radius: 12px; max-width: 550px;">
                                                <div style="text-align: center; margin-bottom: 25px;">
                                                    <i class="fas fa-hands" style="font-size: 48px; color: #1976d2; display: block; margin-bottom: 15px;"></i>
                                                    <h3 style="color: #1976d2; margin: 0 0 10px 0; font-size: 24px;">
                                                        Tradução para Libras
                                                    </h3>
                                                    <p style="color: #666; font-size: 14px; margin: 0;">
                                                        Escolha uma das opções abaixo para acessar o tradutor de Libras
                                                    </p>
                                                </div>
                                                
                                                <div style="margin-bottom: 20px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white;">
                                                    <h4 style="margin: 0 0 10px 0; font-size: 16px; color: white;">
                                                        <i class="fas fa-star" style="margin-right: 8px;"></i>
                                                        Recomendado: Hand Talk
                                                    </h4>
                                                    <p style="margin: 0 0 12px 0; font-size: 14px; opacity: 0.95;">
                                                        Tradutor de Libras mais estável e confiável do Brasil
                                                    </p>
                                                    <button id="activate-handtalk" 
                                                           style="padding: 10px 20px; background: white; color: #667eea; 
                                                                  border: none; border-radius: 6px; font-weight: 600; 
                                                                  font-size: 14px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                                                        Ativar Hand Talk
                                                    </button>
                                                </div>
                                                
                                                <div style="margin-bottom: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #1976d2;">
                                                    <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">
                                                        <i class="fas fa-external-link-alt" style="margin-right: 8px;"></i>
                                                        Opção 2: VLibras Online
                                                    </h4>
                                                    <p style="margin: 0 0 12px 0; font-size: 14px; color: #666;">
                                                        Tradutor oficial do governo (pode estar instável)
                                                    </p>
                                                    <a href="https://vlibras.gov.br/" target="_blank" 
                                                       style="display: inline-block; padding: 10px 20px; background: #1976d2; 
                                                              color: white; text-decoration: none; border-radius: 6px; 
                                                              font-weight: 600; font-size: 14px;">
                                                        Abrir VLibras
                                                    </a>
                                                </div>
                                                
                                                <div style="margin-bottom: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #10b981;">
                                                    <h4 style="margin: 0 0 10px 0; font-size: 16px; color: #333;">
                                                        <i class="fas fa-puzzle-piece" style="margin-right: 8px;"></i>
                                                        Opção 3: Extensões do Navegador
                                                    </h4>
                                                    <p style="margin: 0 0 12px 0; font-size: 14px; color: #666;">
                                                        Instale para traduzir qualquer site automaticamente
                                                    </p>
                                                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                                        <a href="https://chrome.google.com/webstore/detail/vlibras/kihbpjjcjgmfnmdpfkdnbdlnlkfkjkjk" target="_blank" 
                                                           style="display: inline-block; padding: 8px 16px; background: #10b981; 
                                                                  color: white; text-decoration: none; border-radius: 6px; 
                                                                  font-weight: 600; font-size: 13px;">
                                                            Chrome
                                                        </a>
                                                        <a href="https://addons.mozilla.org/pt-BR/firefox/addon/vlibras/" target="_blank" 
                                                           style="display: inline-block; padding: 8px 16px; background: #10b981; 
                                                                  color: white; text-decoration: none; border-radius: 6px; 
                                                                  font-weight: 600; font-size: 13px;">
                                                            Firefox
                                                        </a>
                                                    </div>
                                                </div>
                                            </div>
                                        `;

                                        // Add Hand Talk activation
                                        setTimeout(() => {
                                            const handTalkBtn = document.getElementById('activate-handtalk');
                                            if (handTalkBtn) {
                                                handTalkBtn.addEventListener('click', function() {
                                                    console.log('[Hand Talk] Activating...');
                                                    this.textContent = 'Carregando...';
                                                    this.disabled = true;

                                                    // Load Hand Talk script
                                                    loadHandTalk();

                                                    // Close modal after 2 seconds
                                                    setTimeout(() => {
                                                        wrapper.style.display = 'none';
                                                        topWrapper.style.display = 'none';
                                                        closeBtn.remove();
                                                        const backdrop = document.getElementById('vlibras-backdrop');
                                                        if (backdrop) backdrop.remove();
                                                    }, 2000);
                                                });
                                            }
                                        }, 100);

                                        // Create close button OUTSIDE the content, directly on wrapper
                                        const closeBtn = document.createElement('button');
                                        closeBtn.innerHTML = '✕ FECHAR';
                                        closeBtn.style.cssText = `
                                            position: fixed;
                                            top: 50%;
                                            left: 50%;
                                            transform: translate(-50%, calc(-50% + 320px));
                                            padding: 12px 30px;
                                            background: #f44336;
                                            color: white;
                                            border: none;
                                            border-radius: 8px;
                                            cursor: pointer;
                                            font-size: 16px;
                                            font-weight: 700;
                                            z-index: 100000;
                                            box-shadow: 0 4px 12px rgba(244, 67, 54, 0.5);
                                        `;

                                        closeBtn.addEventListener('click', function(e) {
                                            e.preventDefault();
                                            e.stopPropagation();
                                            console.log('[VLibras] CLOSE BUTTON CLICKED!');

                                            // Hide wrapper and topWrapper
                                            wrapper.style.display = 'none';
                                            topWrapper.style.display = 'none';

                                            // Remove button
                                            this.remove();

                                            // Remove backdrop
                                            const backdrop = document.getElementById('vlibras-backdrop');
                                            if (backdrop) backdrop.remove();
                                        });

                                        document.body.appendChild(closeBtn);

                                        // Create a backdrop that closes on click
                                        const backdrop = document.createElement('div');
                                        backdrop.id = 'vlibras-backdrop';
                                        backdrop.style.cssText = `
                                            position: fixed;
                                            top: 0;
                                            left: 0;
                                            right: 0;
                                            bottom: 0;
                                            background: rgba(0, 0, 0, 0.5);
                                            z-index: 99998;
                                            cursor: pointer;
                                        `;

                                        backdrop.addEventListener('click', function() {
                                            console.log('[VLibras] Backdrop clicked - closing');

                                            // Hide wrapper and topWrapper
                                            wrapper.style.display = 'none';
                                            topWrapper.style.display = 'none';

                                            // Remove button and backdrop
                                            closeBtn.remove();
                                            this.remove();
                                        });

                                        document.body.appendChild(backdrop);
                                        console.log('[VLibras] ✅ Fallback player created with backdrop and close button');

                                        // Make button functional with proper toggle
                                        const btn = document.querySelector('[vw-access-button]');
                                        if (btn) {
                                            // Remove any existing handlers
                                            btn.onclick = null;

                                            btn.addEventListener('click', function(e) {
                                                e.preventDefault();
                                                e.stopPropagation();
                                                console.log('[VLibras] Button clicked - toggling player');

                                                const isVisible = wrapper.style.display === 'block';
                                                if (isVisible) {
                                                    wrapper.style.display = 'none';
                                                    console.log('[VLibras] Player hidden');
                                                } else {
                                                    wrapper.style.display = 'block';
                                                    topWrapper.style.display = 'block';
                                                    console.log('[VLibras] Player shown');
                                                }
                                            });
                                            console.log('[VLibras] Button click handler attached');
                                        }
                                    }
                                }
                            } else {
                                console.log('[VLibras] ✅ VLibras loaded successfully with', iframes.length, 'iframe(s)');
                                iframes.forEach((iframe, i) => {
                                    console.log(`[VLibras] Iframe ${i} src:`, iframe.src || 'no src');
                                    // Ensure iframe is visible
                                    iframe.style.display = 'block';
                                    iframe.style.visibility = 'visible';
                                });
                            }
                        }, 2000);

                    } catch (error) {
                        console.error('[VLibras] ❌ Error during initialization:', error);
                        throw error;
                    }

                    // Add custom styles
                    addVLibrasStyles();

                    // Check if button was created and add fallback icon
                    setTimeout(() => {
                        const button = document.querySelector('[vw-access-button]');
                        if (button) {
                            console.log('[VLibras] ✅ Button found!', button);
                            console.log('[VLibras] Button position:', window.getComputedStyle(button).position);
                            console.log('[VLibras] Button display:', window.getComputedStyle(button).display);
                            console.log('[VLibras] Button z-index:', window.getComputedStyle(button).zIndex);

                            // Add fallback icon if button is empty
                            if (!button.innerHTML.trim() || button.innerHTML.trim() === '') {
                                console.log('[VLibras] Adding fallback icon to button');
                                button.innerHTML = '<i class="fas fa-hands" style="font-size: 32px; color: white;"></i>';
                            }

                            // Add title for accessibility
                            button.setAttribute('title', 'Ativar VLibras - Tradução para Libras');
                            button.setAttribute('aria-label', 'Ativar VLibras - Tradução para Libras');

                            // Check if plugin wrapper exists
                            const wrapper = document.querySelector('[vw-plugin-wrapper]');
                            console.log('[VLibras] Plugin wrapper found:', !!wrapper);

                            // Check if VLibras container has the right structure
                            const container = document.querySelector('[vw]');
                            if (container) {
                                console.log('[VLibras] Container classes:', container.className);
                                console.log('[VLibras] Container children:', container.children.length);
                            }

                            // Force VLibras to be interactive
                            if (wrapper) {
                                wrapper.style.display = 'block';
                                wrapper.style.visibility = 'visible';
                                wrapper.style.opacity = '1';
                                console.log('[VLibras] Wrapper visibility forced');

                                // Add close button to wrapper
                                const closeBtn = document.createElement('button');
                                closeBtn.innerHTML = '✕';
                                closeBtn.style.cssText = `
                                    position: absolute;
                                    top: 10px;
                                    right: 10px;
                                    width: 30px;
                                    height: 30px;
                                    border: none;
                                    background: #f44336;
                                    color: white;
                                    border-radius: 50%;
                                    cursor: pointer;
                                    font-size: 20px;
                                    z-index: 100000;
                                    display: none;
                                `;
                                closeBtn.onclick = function() {
                                    wrapper.style.display = 'none';
                                    this.style.display = 'none';
                                };

                                // Show close button when wrapper is visible
                                const observer = new MutationObserver(() => {
                                    if (wrapper.style.display !== 'none' && wrapper.querySelector('.vw-plugin-top-wrapper')) {
                                        closeBtn.style.display = 'block';
                                    } else {
                                        closeBtn.style.display = 'none';
                                    }
                                });
                                observer.observe(wrapper, {
                                    attributes: true,
                                    childList: true,
                                    subtree: true
                                });

                                wrapper.appendChild(closeBtn);
                            }

                            // Check if there are any VLibras event listeners
                            console.log('[VLibras] Setup complete. Click the blue button to open the player.');
                        } else {
                            console.error('[VLibras] ❌ Button NOT found in DOM!');
                        }
                    }, 2000);
                } else {
                    console.error('[VLibras] VLibras object not available after script load');
                    showLibrasError('Erro ao inicializar Libras. Tente recarregar a página.');
                }
            } catch (e) {
                console.error('[VLibras] Error initializing:', e);
                console.error('[VLibras] Error stack:', e.stack);
                showLibrasError('Erro ao inicializar Libras: ' + e.message);
            }
        }, 1000);
    };

    script.onerror = function() {
        console.error('Failed to load VLibras script');
        showLibrasError('Falha ao carregar Libras. Verifique sua conexão.');

        // Remove the div if script fails
        if (vLibrasDiv && vLibrasDiv.parentNode) {
            vLibrasDiv.parentNode.removeChild(vLibrasDiv);
        }
    };

    document.head.appendChild(script);
}

function addVLibrasStyles_DEPRECATED() {
    // Check if styles already exist
    if (document.getElementById('vlibras-custom-styles')) {
        return;
    }

    const style = document.createElement('style');
    style.id = 'vlibras-custom-styles';
    style.textContent = `
        /* VLibras Custom Positioning - Make it VERY visible */
        [vw] {
            position: fixed !important;
            z-index: 99999 !important;
            pointer-events: none !important;
        }
        
        [vw] * {
            pointer-events: auto !important;
        }
        
        [vw-access-button] {
            position: fixed !important;
            bottom: 20px !important;
            left: 20px !important;
            width: 70px !important;
            height: 70px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
            box-shadow: 0 6px 20px rgba(25, 118, 210, 0.8) !important;
            transition: all 0.3s ease !important;
            z-index: 99999 !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 4px solid white !important;
            animation: vlibras-pulse 2s infinite !important;
        }
        
        @keyframes vlibras-pulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 6px 20px rgba(25, 118, 210, 0.8);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 8px 25px rgba(25, 118, 210, 1);
            }
        }
        
        [vw-access-button]:hover {
            transform: scale(1.15) !important;
            box-shadow: 0 6px 20px rgba(25, 118, 210, 0.8) !important;
            background: #1565c0 !important;
        }
        
        [vw-plugin-wrapper] {
            position: fixed !important;
            z-index: 99999 !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        [vw-plugin-wrapper] * {
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        /* VLibras player/modal - smaller and centered */
        .vw-plugin-top-wrapper {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            z-index: 99999 !important;
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
            width: 500px !important;
            height: auto !important;
            max-width: 90vw !important;
            max-height: 80vh !important;
            overflow: auto !important;
            pointer-events: auto !important;
        }
        
        /* Loading indicator */
        .vw-plugin-top-wrapper:empty::after {
            content: 'Carregando VLibras...' !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100% !important;
            font-size: 18px !important;
            color: #666 !important;
        }
        
        /* Ensure the player is visible */
        [vw] .enabled {
            display: block !important;
        }
        
        /* VLibras iframe and content */
        [vw-plugin-wrapper] iframe,
        .vw-plugin-top-wrapper iframe {
            border: none !important;
            width: 100% !important;
            height: 100% !important;
            display: block !important;
            background: white !important;
        }
        
        /* All VLibras content should be visible */
        [vw-plugin-wrapper] *,
        .vw-plugin-top-wrapper * {
            max-width: 100% !important;
        }
        
        /* VLibras canvas (where avatar appears) */
        [vw-plugin-wrapper] canvas,
        .vw-plugin-top-wrapper canvas {
            display: block !important;
            width: 100% !important;
            height: auto !important;
        }
        
        /* Remove backdrop - it was blocking clicks */
        [vw-plugin-wrapper]::before {
            display: none !important;
        }
        
        /* Make wrapper not block the whole screen */
        [vw-plugin-wrapper] {
            pointer-events: none !important;
        }
        
        [vw-plugin-wrapper] * {
            pointer-events: auto !important;
        }
        
        /* Make sure the button icon is visible */
        [vw-access-button] img,
        [vw-access-button] svg {
            width: 35px !important;
            height: 35px !important;
            filter: brightness(0) invert(1) !important;
        }
        
        /* Adjust for mobile */
        @media (max-width: 768px) {
            [vw-access-button] {
                bottom: 15px !important;
                left: 15px !important;
                width: 55px !important;
                height: 55px !important;
            }
        }
    `;
    document.head.appendChild(style);
    console.log('[VLibras] Custom styles applied - button should be visible at bottom-left');
}

function showLibrasError_DEPRECATED(message) {
    // Create a temporary notification instead of alert
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f44336;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        z-index: 999999;
        font-family: Arial, sans-serif;
        font-size: 14px;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove notification after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// High contrast CSS (dynamically added)
function addHighContrastCSS() {
    const style = document.createElement('style');
    style.textContent = `
        .high-contrast {
            background: #000 !important;
            color: #fff !important;
        }
        
        .high-contrast .accessibility-toggle {
            background: #fff;
            color: #000;
            border: 2px solid #000;
        }
        
        .high-contrast .accessibility-panel {
            background: #000;
            border: 2px solid #fff;
            color: #fff;
        }
        
        .high-contrast .accessibility-header {
            background: #fff;
            color: #000;
        }
        
        .high-contrast .close-btn {
            color: #000;
        }
        
        .high-contrast .close-btn:hover {
            background: rgba(0, 0, 0, 0.2);
        }
        
        .high-contrast .toggle-btn {
            background: #333;
            border-color: #fff;
            color: #fff;
        }
        
        .high-contrast .toggle-btn:hover {
            background: #444;
        }
        
        .high-contrast .toggle-btn.active {
            background: #fff;
            color: #000;
            border-color: #000;
        }
        
        .high-contrast .control-btn,
        .high-contrast .reset-btn {
            background: #333;
            border-color: #fff;
            color: #fff;
        }
        
        .high-contrast .control-btn:hover,
        .high-contrast .reset-btn:hover {
            background: #444;
        }
    `;
    document.head.appendChild(style);
}

// Text Reader Functions
function speakText(text) {
    if (!window.speechSynthesis) {
        console.error('Speech Synthesis not supported');
        return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    // Create utterance
    const utterance = new SpeechSynthesisUtterance(text);

    // Configure voice settings
    utterance.lang = 'pt-BR';
    utterance.rate = 1.0; // Normal speed
    utterance.pitch = 1.0; // Normal pitch
    utterance.volume = 1.0; // Full volume

    // Try to use a Portuguese voice if available
    const voices = window.speechSynthesis.getVoices();
    const portugueseVoice = voices.find(voice =>
        voice.lang.startsWith('pt-BR') || voice.lang.startsWith('pt')
    );

    if (portugueseVoice) {
        utterance.voice = portugueseVoice;
    }

    // Speak
    window.speechSynthesis.speak(utterance);

    return utterance;
}

function enableTextReader() {
    // Add body attribute for styling
    document.body.setAttribute('data-reader-active', 'true');

    // Add hover listeners to readable elements
    const readableElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, a, button, label, span, li, td, th');

    readableElements.forEach(element => {
        element.addEventListener('mouseenter', handleTextHover);
        element.addEventListener('mouseleave', handleTextLeave);
        element.setAttribute('data-reader-enabled', 'true');
    });

    // Add click listener to stop speech
    document.addEventListener('click', stopSpeech);
}

function disableTextReader() {
    // Remove body attribute
    document.body.removeAttribute('data-reader-active');

    // Remove hover listeners
    const readableElements = document.querySelectorAll('[data-reader-enabled="true"]');

    readableElements.forEach(element => {
        element.removeEventListener('mouseenter', handleTextHover);
        element.removeEventListener('mouseleave', handleTextLeave);
        element.removeAttribute('data-reader-enabled');
    });

    // Remove click listener
    document.removeEventListener('click', stopSpeech);

    // Stop any ongoing speech
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}

function handleTextHover(event) {
    const element = event.target;
    let text = '';

    // Get text content based on element type
    if (element.tagName === 'IMG') {
        text = element.alt || 'Imagem sem descrição';
    } else if (element.tagName === 'A') {
        text = element.textContent.trim() || element.getAttribute('aria-label') || 'Link';
    } else if (element.tagName === 'BUTTON') {
        text = element.textContent.trim() || element.getAttribute('aria-label') || 'Botão';
    } else {
        text = element.textContent.trim();
    }

    // Only speak if there's text and it's not too long
    if (text && text.length > 0 && text.length < 500) {
        // Debounce: only speak if mouse stays for a moment
        clearTimeout(element.speakTimeout);
        element.speakTimeout = setTimeout(() => {
            speakText(text);
        }, 300);
    }
}

function handleTextLeave(event) {
    const element = event.target;
    // Clear timeout if mouse leaves before speaking
    if (element.speakTimeout) {
        clearTimeout(element.speakTimeout);
    }
}

function stopSpeech(event) {
    // Stop speech on click
    if (window.speechSynthesis && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }
}

// Load voices when available
if (window.speechSynthesis) {
    // Chrome loads voices asynchronously
    window.speechSynthesis.onvoiceschanged = function() {
        const voices = window.speechSynthesis.getVoices();
        console.log('Available voices:', voices.length);
    };
}

// Libras Integration - Simplified approach
function loadHandTalk() {
    console.log('[Libras] Showing Libras options...');

    // Create a modal with Libras options
    const modal = document.createElement('div');
    modal.id = 'libras-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: 100000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;

    modal.innerHTML = `
        <div style="background: white; border-radius: 16px; padding: 40px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;">
            <div style="text-align: center; margin-bottom: 30px;">
                <i class="fas fa-hands" style="font-size: 64px; color: #667eea; margin-bottom: 20px;"></i>
                <h2 style="margin: 0 0 10px 0; color: #333; font-size: 28px;">Tradução para Libras</h2>
                <p style="color: #666; font-size: 16px; margin: 0;">Escolha como deseja acessar o tradutor de Libras</p>
            </div>
            
            <div style="display: grid; gap: 20px;">
                <!-- Opção 1: VLibras -->
                <div style="padding: 25px; background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%); border-radius: 12px; color: white; cursor: pointer;" onclick="window.open('https://vlibras.gov.br/', '_blank')">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <i class="fas fa-globe" style="font-size: 40px;"></i>
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 8px 0; font-size: 20px;">VLibras Online</h3>
                            <p style="margin: 0; font-size: 14px; opacity: 0.95;">Tradutor oficial do Governo Federal</p>
                        </div>
                        <i class="fas fa-external-link-alt" style="font-size: 20px;"></i>
                    </div>
                </div>
                
                <!-- Opção 2: Hand Talk -->
                <div style="padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white; cursor: pointer;" onclick="window.open('https://www.handtalk.me/br/plugin', '_blank')">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <i class="fas fa-robot" style="font-size: 40px;"></i>
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 8px 0; font-size: 20px;">Hand Talk</h3>
                            <p style="margin: 0; font-size: 14px; opacity: 0.95;">Tradutor de Libras mais popular do Brasil</p>
                        </div>
                        <i class="fas fa-external-link-alt" style="font-size: 20px;"></i>
                    </div>
                </div>
                
                <!-- Opção 3: Extensões -->
                <div style="padding: 25px; background: #f8f9fa; border-radius: 12px; border: 2px solid #e2e8f0;">
                    <div style="margin-bottom: 15px;">
                        <h3 style="margin: 0 0 8px 0; color: #333; font-size: 18px;">
                            <i class="fas fa-puzzle-piece" style="margin-right: 10px; color: #10b981;"></i>
                            Extensões do Navegador
                        </h3>
                        <p style="margin: 0; color: #666; font-size: 14px;">Instale para traduzir qualquer site automaticamente</p>
                    </div>
                    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                        <a href="https://chrome.google.com/webstore/detail/vlibras/kihbpjjcjgmfnmdpfkdnbdlnlkfkjkjk" target="_blank" 
                           style="flex: 1; min-width: 140px; padding: 12px 20px; background: #10b981; color: white; text-decoration: none; 
                                  border-radius: 8px; font-weight: 600; text-align: center; font-size: 14px;">
                            <i class="fab fa-chrome" style="margin-right: 8px;"></i>Chrome
                        </a>
                        <a href="https://addons.mozilla.org/pt-BR/firefox/addon/vlibras/" target="_blank" 
                           style="flex: 1; min-width: 140px; padding: 12px 20px; background: #ff7139; color: white; text-decoration: none; 
                                  border-radius: 8px; font-weight: 600; text-align: center; font-size: 14px;">
                            <i class="fab fa-firefox" style="margin-right: 8px;"></i>Firefox
                        </a>
                    </div>
                </div>
                
                <!-- Informação -->
                <div style="padding: 20px; background: #fff3cd; border-radius: 12px; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                        <i class="fas fa-info-circle" style="margin-right: 8px;"></i>
                        <strong>Dica:</strong> As extensões do navegador são a melhor opção, pois funcionam em todos os sites automaticamente.
                    </p>
                </div>
            </div>
            
            <button onclick="document.getElementById('libras-modal').remove()" 
                    style="width: 100%; margin-top: 25px; padding: 15px; background: #f44336; color: white; 
                           border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer;">
                Fechar
            </button>
        </div>
    `;

    // Close on backdrop click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });

    document.body.appendChild(modal);
    console.log('[Libras] Modal displayed');
}

// Add high contrast styles when DOM is loaded
document.addEventListener('DOMContentLoaded', addHighContrastCSS);