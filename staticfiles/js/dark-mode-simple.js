// Simplified Dark Mode Toggle - Backup Implementation
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌙 Simple Dark Mode System Starting...');

    // Get saved theme or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

    // Apply initial theme
    document.documentElement.setAttribute('data-theme', initialTheme);
    console.log('Initial theme:', initialTheme);

    // Simple toggle function
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        console.log('Switching from', currentTheme, 'to', newTheme);

        // Apply new theme
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update button icons and text
        updateButtons(newTheme);

        return newTheme;
    }

    // Update button appearance
    function updateButtons(theme) {
        // Update navbar button
        const navButton = document.getElementById('darkModeToggle');
        if (navButton) {
            const icon = navButton.querySelector('i');
            const text = navButton.querySelector('span');

            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun me-1' : 'fas fa-moon me-1';
            }
            if (text) {
                text.textContent = theme === 'dark' ? 'Claro' : 'Escuro';
            }
        }

        // Update accessibility panel button
        const accessButton = document.getElementById('toggle-dark-mode');
        if (accessButton) {
            const icon = accessButton.querySelector('i');
            const text = accessButton.querySelector('.option-text');

            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun option-icon' : 'fas fa-moon option-icon';
            }
            if (text) {
                text.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
            }
        }
    }

    // Initialize buttons
    updateButtons(initialTheme);

    // Add click listeners
    document.addEventListener('click', function(e) {
        if (e.target.closest('#darkModeToggle') || e.target.closest('#toggle-dark-mode')) {
            e.preventDefault();
            const newTheme = toggleTheme();
            console.log('Theme toggled to:', newTheme);
        }
    });

    // Keyboard shortcut (Ctrl+Shift+D)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleTheme();
        }
    });

    console.log('✅ Simple Dark Mode System Ready!');
});