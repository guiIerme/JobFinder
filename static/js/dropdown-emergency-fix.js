// Emergency Dropdown Fix - Fallback solution
(function() {
    'use strict';

    // Wait for DOM to be ready
    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }

    // Emergency dropdown implementation
    function emergencyDropdownFix() {
        console.log('🚨 Emergency dropdown fix activated');

        const userDropdown = document.getElementById('userDropdown');
        if (!userDropdown) {
            console.log('❌ User dropdown not found');
            return;
        }

        const dropdownMenu = userDropdown.nextElementSibling;
        if (!dropdownMenu || !dropdownMenu.classList.contains('dropdown-menu')) {
            console.log('❌ Dropdown menu not found');
            return;
        }

        console.log('✅ Dropdown elements found, applying emergency fix');

        // Remove all existing event listeners by cloning the element
        const newUserDropdown = userDropdown.cloneNode(true);
        userDropdown.parentNode.replaceChild(newUserDropdown, userDropdown);

        // Add our own click handler
        newUserDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            console.log('🖱️ Emergency dropdown clicked');

            const menu = this.nextElementSibling;
            const isVisible = menu.classList.contains('show');

            // Close all other dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(otherMenu => {
                if (otherMenu !== menu) {
                    otherMenu.classList.remove('show');
                    const otherToggle = otherMenu.previousElementSibling;
                    if (otherToggle) {
                        otherToggle.setAttribute('aria-expanded', 'false');
                    }
                }
            });

            // Toggle current dropdown
            if (isVisible) {
                menu.classList.remove('show');
                this.setAttribute('aria-expanded', 'false');
                console.log('📤 Dropdown closed');
            } else {
                menu.classList.add('show');
                this.setAttribute('aria-expanded', 'true');
                console.log('📥 Dropdown opened');
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                    const toggle = menu.previousElementSibling;
                    if (toggle) {
                        toggle.setAttribute('aria-expanded', 'false');
                    }
                });
            }
        });

        // Close dropdown when pressing Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                    const toggle = menu.previousElementSibling;
                    if (toggle) {
                        toggle.setAttribute('aria-expanded', 'false');
                        toggle.focus(); // Return focus to toggle
                    }
                });
            }
        });

        console.log('✅ Emergency dropdown fix applied successfully');
    }

    // Check if Bootstrap dropdown is working
    function checkBootstrapDropdown() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const userDropdown = document.getElementById('userDropdown');
                if (!userDropdown) {
                    resolve(false);
                    return;
                }

                try {
                    // Try to create Bootstrap dropdown instance
                    const instance = new bootstrap.Dropdown(userDropdown);

                    // Test if it works by trying to show/hide
                    instance.show();
                    const menu = userDropdown.nextElementSibling;
                    const isWorking = menu && menu.classList.contains('show');
                    instance.hide();

                    resolve(isWorking);
                } catch (error) {
                    console.log('Bootstrap dropdown failed:', error);
                    resolve(false);
                }
            }, 500);
        });
    }

    // Main initialization
    ready(function() {
        console.log('🔧 Dropdown emergency fix script loaded');

        // Wait a bit for other scripts to load
        setTimeout(async () => {
            if (typeof bootstrap === 'undefined') {
                console.log('⚠️ Bootstrap not found, applying emergency fix immediately');
                emergencyDropdownFix();
                return;
            }

            console.log('✅ Bootstrap found, testing dropdown functionality');
            const isWorking = await checkBootstrapDropdown();

            if (!isWorking) {
                console.log('⚠️ Bootstrap dropdown not working, applying emergency fix');
                emergencyDropdownFix();
            } else {
                console.log('✅ Bootstrap dropdown is working correctly');
            }
        }, 1000);
    });

    // Expose emergency fix function globally for manual activation
    window.activateEmergencyDropdownFix = emergencyDropdownFix;

})();