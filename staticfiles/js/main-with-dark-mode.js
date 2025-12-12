// Main JavaScript for Home Services Platform with Dark Mode Support

// Initialize dark mode
function initializeDarkMode() {
    // Check for saved theme preference or respect OS preference
    const savedTheme = localStorage.getItem('theme');
    const osPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (osPrefersDark ? 'dark' : 'light');
    
    // Apply initial theme
    document.documentElement.setAttribute('data-theme', initialTheme);
    
    // Update toggle buttons
    updateDarkModeToggles(initialTheme);
}

// Function to update dark mode toggle buttons
function updateDarkModeToggles(theme) {
    // Update navbar button
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        const icon = darkModeToggle.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                darkModeToggle.classList.add('btn-primary');
                darkModeToggle.classList.remove('btn-outline-primary');
            } else {
                icon.className = 'fas fa-moon';
                darkModeToggle.classList.add('btn-outline-primary');
                darkModeToggle.classList.remove('btn-primary');
            }
        }
    }
    
    // Update accessibility panel button
    const accessibilityToggle = document.getElementById('toggle-dark-mode');
    if (accessibilityToggle) {
        const text = accessibilityToggle.querySelector('.option-text');
        if (text) {
            text.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Escuro';
        }
        const icon = accessibilityToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun option-icon' : 'fas fa-moon option-icon';
        }
        if (theme === 'dark') {
            accessibilityToggle.classList.add('active');
        } else {
            accessibilityToggle.classList.remove('active');
        }
    }
}

// Toggle dark mode
function toggleDarkMode() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateDarkModeToggles(newTheme);
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initializeDarkMode();
    
    console.log('DOM loaded, initializing event listeners');
    
    // Add event listeners for dark mode toggle buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('#darkModeToggle') || e.target.closest('#toggle-dark-mode')) {
            toggleDarkMode();
        }
    });
    
    // Rest of the existing main.js code would go here
    // For brevity, we're not including the full file content
    // In a real implementation, you would merge this with your existing main.js
});