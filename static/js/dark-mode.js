// Enhanced Dark Mode Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌙 Dark Mode System Initializing...');

    // Check for saved theme preference or respect OS preference
    const savedTheme = localStorage.getItem('theme');
    const osPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (osPrefersDark ? 'dark' : 'light');

    console.log('🎨 Initial theme:', initialTheme);

    // Apply initial theme
    document.documentElement.setAttribute('data-theme', initialTheme);

    // Add transition styles for smooth theme switching
    const style = document.createElement('style');
    style.textContent = `
        * {
            transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                       color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                       border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                       box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .theme-transition {
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .dark-mode-ripple {
            position: fixed;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(90, 50, 163, 0.3) 0%, transparent 70%);
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
            z-index: 9999;
        }
        
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .toggle-icon-spin {
            animation: iconSpin 0.5s ease-in-out;
        }
        
        @keyframes iconSpin {
            0% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(180deg) scale(1.2); }
            100% { transform: rotate(360deg) scale(1); }
        }
    `;
    document.head.appendChild(style);

    // Function to create ripple effect
    function createRippleEffect(event) {
        const ripple = document.createElement('div');
        ripple.classList.add('dark-mode-ripple');

        const size = 60;
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (event.clientX - size / 2) + 'px';
        ripple.style.top = (event.clientY - size / 2) + 'px';

        document.body.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // Function to toggle dark mode with enhanced effects
    window.toggleDarkMode = function(event) {
        console.log('🔄 Toggling dark mode...');
        console.log('Event received:', event);

        // Create ripple effect if event is provided
        if (event) {
            createRippleEffect(event);
        }

        const currentTheme = document.documentElement.getAttribute('data-theme');
        console.log('Current theme:', currentTheme);
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        console.log('New theme will be:', newTheme);

        // Add transition class
        document.body.classList.add('theme-transition');

        // Apply new theme
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        console.log('✨ Theme changed to:', newTheme);

        // Update any toggle buttons
        updateDarkModeToggles(newTheme);

        // Show notification
        showThemeNotification(newTheme);

        // Remove transition class after animation
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 500);
    };

    // Function to show theme change notification
    function showThemeNotification(theme) {
        // Remove existing notification
        const existingNotification = document.querySelector('.theme-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${theme === 'dark' ? 'linear-gradient(135deg, #5a32a3, #3a5fd6)' : 'linear-gradient(135deg, #6f42c1, #4e73df)'};
                color: white;
                padding: 12px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                font-weight: 600;
                font-size: 14px;
                backdrop-filter: blur(10px);
                animation: slideIn 0.3s ease-out;
            ">
                <i class="fas fa-${theme === 'dark' ? 'moon' : 'sun'} me-2"></i>
                Modo ${theme === 'dark' ? 'Escuro' : 'Claro'} Ativado
            </div>
        `;

        // Add slide-in animation
        const slideInStyle = document.createElement('style');
        slideInStyle.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(slideInStyle);

        document.body.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => {
                notification.remove();
                slideInStyle.remove();
            }, 300);
        }, 3000);
    }

    // Function to update toggle buttons with enhanced animations
    function updateDarkModeToggles(theme) {
        const toggleButtons = document.querySelectorAll('[id^="darkModeToggle"], [id^="toggle-dark-mode"]');
        toggleButtons.forEach(button => {
            const icon = button.querySelector('i');
            const text = button.querySelector('.option-text') || button;

            if (icon) {
                // Add spin animation
                icon.classList.add('toggle-icon-spin');

                setTimeout(() => {
                    if (theme === 'dark') {
                        icon.className = icon.className.replace('fa-moon', 'fa-sun');
                    } else {
                        icon.className = icon.className.replace('fa-sun', 'fa-moon');
                    }

                    setTimeout(() => {
                        icon.classList.remove('toggle-icon-spin');
                    }, 250);
                }, 250);
            }

            if (text && text.classList.contains('option-text')) {
                text.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
            }

            // Update checkbox state if it's a settings toggle
            const checkbox = button.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = theme === 'dark';
            }

            // Add button press effect
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 150);
        });
    }

    // Initialize toggle buttons
    updateDarkModeToggles(initialTheme);

    // Add event listeners to all dark mode toggle buttons
    document.addEventListener('click', function(e) {
        console.log('Click detected on:', e.target);
        const toggleButton = e.target.closest('[id^="darkModeToggle"]') || e.target.closest('[id^="toggle-dark-mode"]');
        console.log('Toggle button found:', toggleButton);
        if (toggleButton) {
            console.log('Preventing default and calling toggleDarkMode');
            e.preventDefault();
            toggleDarkMode(e);
        }
    });

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            updateDarkModeToggles(newTheme);
            console.log('🔄 System theme changed to:', newTheme);
        }
    });

    // Keyboard shortcut for dark mode (Ctrl/Cmd + Shift + D)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleDarkMode(e);
            console.log('⌨️ Dark mode toggled via keyboard shortcut');
        }
    });

    console.log('🌙 Dark Mode System initialized successfully!');
    console.log('💡 Tip: Use Ctrl/Cmd + Shift + D to toggle dark mode');
});