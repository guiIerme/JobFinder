// Dropdown Fix for Profile Menu
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dropdown fix script loaded');

    // Wait for Bootstrap to be fully loaded
    setTimeout(function() {
        initializeDropdowns();
    }, 100);
});

function initializeDropdowns() {
    console.log('Initializing dropdowns...');

    // Find all dropdown toggles
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    console.log('Found dropdown toggles:', dropdownToggles.length);

    dropdownToggles.forEach(function(toggle, index) {
        console.log(`Initializing dropdown ${index + 1}:`, toggle);

        // Remove any existing Bootstrap dropdown instance
        const existingDropdown = bootstrap.Dropdown.getInstance(toggle);
        if (existingDropdown) {
            existingDropdown.dispose();
        }

        // Create new Bootstrap dropdown instance
        const dropdown = new bootstrap.Dropdown(toggle, {
            boundary: 'viewport',
            display: 'dynamic'
        });

        // Add manual click handler as backup
        toggle.addEventListener('click', function(e) {
            console.log('Dropdown clicked:', this);
            e.preventDefault();
            e.stopPropagation();

            // Toggle the dropdown
            const dropdownMenu = this.nextElementSibling;
            if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                const isShown = dropdownMenu.classList.contains('show');

                // Close all other dropdowns first
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    if (menu !== dropdownMenu) {
                        menu.classList.remove('show');
                        menu.parentElement.classList.remove('show');
                    }
                });

                // Toggle current dropdown
                if (isShown) {
                    dropdownMenu.classList.remove('show');
                    this.parentElement.classList.remove('show');
                    this.setAttribute('aria-expanded', 'false');
                } else {
                    dropdownMenu.classList.add('show');
                    this.parentElement.classList.add('show');
                    this.setAttribute('aria-expanded', 'true');
                }
            }
        });

        console.log(`Dropdown ${index + 1} initialized successfully`);
    });

    // Add click outside handler to close dropdowns
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
                menu.parentElement.classList.remove('show');
                const toggle = menu.parentElement.querySelector('.dropdown-toggle');
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    });

    console.log('Dropdown initialization complete');
}

// Alternative initialization for cases where Bootstrap might not be ready
window.addEventListener('load', function() {
    setTimeout(function() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
            console.log('Bootstrap is ready, re-initializing dropdowns');
            initializeDropdowns();
        } else {
            console.error('Bootstrap not found or Dropdown component not available');
        }
    }, 200);
});

// Debug function to check dropdown status
window.checkDropdowns = function() {
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    console.log('Dropdown status check:');
    dropdowns.forEach((dropdown, index) => {
        const instance = bootstrap.Dropdown.getInstance(dropdown);
        console.log(`Dropdown ${index + 1}:`, {
            element: dropdown,
            hasInstance: !!instance,
            ariaExpanded: dropdown.getAttribute('aria-expanded'),
            parentClasses: dropdown.parentElement.className
        });
    });
};

// Force dropdown functionality if Bootstrap fails
window.forceDropdownFix = function() {
    console.log('Forcing dropdown fix...');

    const userDropdown = document.getElementById('userDropdown');
    if (!userDropdown) {
        console.error('User dropdown not found');
        return;
    }

    const dropdownMenu = userDropdown.nextElementSibling;
    if (!dropdownMenu || !dropdownMenu.classList.contains('dropdown-menu')) {
        console.error('Dropdown menu not found');
        return;
    }

    // Remove all existing event listeners
    const newDropdown = userDropdown.cloneNode(true);
    userDropdown.parentNode.replaceChild(newDropdown, userDropdown);

    // Add simple click handler
    newDropdown.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        const menu = this.nextElementSibling;
        const isVisible = menu.classList.contains('show');

        // Close all dropdowns first
        document.querySelectorAll('.dropdown-menu.show').forEach(m => {
            m.classList.remove('show');
            m.parentElement.classList.remove('show');
        });

        // Toggle current dropdown
        if (!isVisible) {
            menu.classList.add('show');
            this.parentElement.classList.add('show');
            this.setAttribute('aria-expanded', 'true');
        }
    });

    console.log('Dropdown fix applied successfully');
};