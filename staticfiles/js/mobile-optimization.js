/**
 * Mobile Optimization JavaScript
 * Melhorias específicas para dispositivos móveis
 */

(function() {
    'use strict';

    // Detectar se é dispositivo móvel
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTablet = /iPad|Android(?=.*\bMobile\b)/i.test(navigator.userAgent);
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    // Adicionar classes CSS baseadas no dispositivo
    document.addEventListener('DOMContentLoaded', function() {
        const body = document.body;
        
        if (isMobile) {
            body.classList.add('is-mobile');
        }
        
        if (isTablet) {
            body.classList.add('is-tablet');
        }
        
        if (isTouchDevice) {
            body.classList.add('is-touch');
        }

        // Otimizações específicas para mobile
        if (isMobile || window.innerWidth <= 768) {
            initMobileOptimizations();
        }
    });

    function initMobileOptimizations() {
        // 1. Corrigir problema do viewport com navbar fixa
        adjustViewportForFixedNavbar();

        // 2. Melhorar experiência com modais
        optimizeModalsForMobile();

        // 3. Otimizar formulários para mobile
        optimizeFormsForMobile();

        // 4. Melhorar navegação touch
        improveTouchNavigation();

        // 5. Otimizar scroll e focus
        optimizeScrollAndFocus();

        // 6. Adicionar suporte a gestos
        addGestureSupport();

        // 7. Otimizar performance
        optimizePerformance();
    }

    function adjustViewportForFixedNavbar() {
        const navbar = document.querySelector('.navbar');
        const main = document.querySelector('main');
        
        if (navbar && main) {
            // Calcular altura real da navbar
            const navbarHeight = navbar.offsetHeight;
            
            // Aplicar padding-top ao main
            main.style.paddingTop = navbarHeight + 'px';
            
            // Recalcular quando a orientação mudar
            window.addEventListener('orientationchange', function() {
                setTimeout(function() {
                    const newNavbarHeight = navbar.offsetHeight;
                    main.style.paddingTop = newNavbarHeight + 'px';
                }, 100);
            });
        }
    }

    function optimizeModalsForMobile() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(function(modal) {
            // Prevenir scroll do body quando modal está aberto
            modal.addEventListener('shown.bs.modal', function() {
                document.body.style.overflow = 'hidden';
                document.body.style.position = 'fixed';
                document.body.style.width = '100%';
            });

            modal.addEventListener('hidden.bs.modal', function() {
                document.body.style.overflow = '';
                document.body.style.position = '';
                document.body.style.width = '';
            });

            // Melhorar scroll dentro do modal
            const modalBody = modal.querySelector('.modal-body');
            if (modalBody) {
                modalBody.style.webkitOverflowScrolling = 'touch';
            }

            // Fechar modal ao tocar fora (melhor para touch)
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            });
        });
    }

    function optimizeFormsForMobile() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(function(form) {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(function(input) {
                // Prevenir zoom no iOS
                if (input.type !== 'file') {
                    input.style.fontSize = '16px';
                }

                // Melhorar experiência com teclado virtual
                input.addEventListener('focus', function() {
                    // Scroll suave para o campo em foco
                    setTimeout(function() {
                        input.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 300);
                });

                // Otimizar inputs de senha
                if (input.type === 'password') {
                    const toggleBtn = form.querySelector('[id*="toggle"][id*="assword"]');
                    if (toggleBtn) {
                        toggleBtn.style.minWidth = '44px';
                        toggleBtn.style.minHeight = '44px';
                    }
                }
            });

            // Melhorar feedback de envio
            form.addEventListener('submit', function() {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
                    
                    // Reabilitar após 10 segundos (fallback)
                    setTimeout(function() {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Enviar';
                    }, 10000);
                }
            });
        });
    }

    function improveTouchNavigation() {
        // Melhorar dropdowns para touch
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        
        dropdowns.forEach(function(dropdown) {
            // Adicionar indicador visual de toque
            dropdown.addEventListener('touchstart', function() {
                dropdown.style.backgroundColor = 'rgba(111, 66, 193, 0.1)';
            });

            dropdown.addEventListener('touchend', function() {
                setTimeout(function() {
                    dropdown.style.backgroundColor = '';
                }, 150);
            });
        });

        // Melhorar navegação por cards
        const cards = document.querySelectorAll('.card, .service-card');
        
        cards.forEach(function(card) {
            // Adicionar feedback visual para toque
            card.addEventListener('touchstart', function() {
                card.style.transform = 'scale(0.98)';
                card.style.transition = 'transform 0.1s ease';
            });

            card.addEventListener('touchend', function() {
                card.style.transform = '';
            });
        });
    }

    function optimizeScrollAndFocus() {
        // Melhorar scroll suave
        document.documentElement.style.scrollBehavior = 'smooth';

        // Otimizar focus para elementos interativos
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea');
        
        interactiveElements.forEach(function(element) {
            element.addEventListener('focus', function() {
                // Garantir que o elemento focado seja visível
                setTimeout(function() {
                    const rect = element.getBoundingClientRect();
                    const navbar = document.querySelector('.navbar');
                    const navbarHeight = navbar ? navbar.offsetHeight : 0;
                    
                    if (rect.top < navbarHeight) {
                        window.scrollBy(0, rect.top - navbarHeight - 20);
                    }
                }, 100);
            });
        });

        // Melhorar scroll em listas longas
        const scrollableElements = document.querySelectorAll('.modal-body, .dropdown-menu');
        
        scrollableElements.forEach(function(element) {
            element.style.webkitOverflowScrolling = 'touch';
        });
    }

    function addGestureSupport() {
        // Adicionar suporte a swipe para fechar modais
        const modals = document.querySelectorAll('.modal-dialog');
        
        modals.forEach(function(modal) {
            let startY = 0;
            let currentY = 0;
            let isDragging = false;

            modal.addEventListener('touchstart', function(e) {
                startY = e.touches[0].clientY;
                isDragging = true;
            });

            modal.addEventListener('touchmove', function(e) {
                if (!isDragging) return;
                
                currentY = e.touches[0].clientY;
                const deltaY = currentY - startY;

                // Aplicar transformação visual
                if (deltaY > 0) {
                    modal.style.transform = `translateY(${deltaY * 0.5}px)`;
                    modal.style.opacity = Math.max(0.5, 1 - (deltaY / 300));
                }
            });

            modal.addEventListener('touchend', function() {
                if (!isDragging) return;
                
                const deltaY = currentY - startY;
                
                // Se o swipe foi suficiente, fechar modal
                if (deltaY > 100) {
                    const modalElement = modal.closest('.modal');
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }

                // Resetar transformação
                modal.style.transform = '';
                modal.style.opacity = '';
                isDragging = false;
            });
        });
    }

    function optimizePerformance() {
        // Lazy loading para imagens
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(function(img) {
                imageObserver.observe(img);
            });
        }

        // Debounce para eventos de resize
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                // Recalcular layouts se necessário
                adjustViewportForFixedNavbar();
            }, 250);
        });

        // Otimizar animações para dispositivos com bateria baixa
        if ('getBattery' in navigator) {
            navigator.getBattery().then(function(battery) {
                if (battery.level < 0.2) {
                    document.body.classList.add('low-battery');
                    // Reduzir animações
                    const style = document.createElement('style');
                    style.textContent = `
                        .low-battery * {
                            animation-duration: 0.1s !important;
                            transition-duration: 0.1s !important;
                        }
                    `;
                    document.head.appendChild(style);
                }
            });
        }
    }

    // Adicionar suporte a orientação
    window.addEventListener('orientationchange', function() {
        // Aguardar a mudança de orientação completar
        setTimeout(function() {
            // Recalcular viewport
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                viewport.setAttribute('content', 
                    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
                );
            }

            // Forçar recálculo de layout
            document.body.style.height = '100vh';
            setTimeout(function() {
                document.body.style.height = '';
            }, 100);
        }, 500);
    });

    // Melhorar experiência com teclado virtual
    if (isMobile) {
        let initialViewportHeight = window.innerHeight;

        window.addEventListener('resize', function() {
            const currentHeight = window.innerHeight;
            const heightDifference = initialViewportHeight - currentHeight;

            // Se a diferença for significativa, provavelmente o teclado virtual está aberto
            if (heightDifference > 150) {
                document.body.classList.add('keyboard-open');
            } else {
                document.body.classList.remove('keyboard-open');
            }
        });
    }

    // Adicionar estilos CSS dinâmicos para melhorias mobile
    const mobileStyles = document.createElement('style');
    mobileStyles.textContent = `
        .keyboard-open .footer {
            display: none;
        }
        
        .keyboard-open .chat-widget-container {
            bottom: 10px;
        }
        
        .is-touch .btn:hover {
            transform: none;
        }
        
        .is-touch .card:hover {
            transform: none;
        }
        
        .is-mobile .navbar-collapse {
            max-height: calc(100vh - 60px);
            overflow-y: auto;
        }
    `;
    document.head.appendChild(mobileStyles);

})();