// Enhanced microinteractions and site performance improvements

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add microinteractions to buttons
    addButtonInteractions();
    
    // Add hover effects to cards
    addCardInteractions();
    
    // Initialize form enhancements
    initFormEnhancements();
    
    // Add scroll animations
    initScrollAnimations();
});

// Button microinteractions
function addButtonInteractions() {
    const buttons = document.querySelectorAll('button, .btn, a.btn');
    
    buttons.forEach(button => {
        // Add ripple effect
        button.addEventListener('click', function(e) {
            createRipple(e, this);
        });
        
        // Add hover effects
        button.addEventListener('mouseenter', function() {
            this.classList.add('hovered');
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('hovered');
        });
    });
}

// Create ripple effect on button click
function createRipple(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Card hover interactions
function addCardInteractions() {
    const cards = document.querySelectorAll('.card, .service-card, .provider-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15)';
        });
    });
}

// Form enhancements
function initFormEnhancements() {
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        // Add focus effects
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
        
        // Add floating labels for better UX
        if (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA') {
            input.addEventListener('input', function() {
                if (this.value) {
                    this.classList.add('has-value');
                } else {
                    this.classList.remove('has-value');
                }
            });
        }
    });
}

// Scroll animations
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('scrolled');
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Add CSS for microinteractions
function addMicrointeractionCSS() {
    const style = document.createElement('style');
    style.textContent = `
        /* Ripple effect */
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.7);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        }
        
        @keyframes ripple {
            to {
                transform: scale(2.5);
                opacity: 0;
            }
        }
        
        /* Button hover effects */
        .btn.hovered, button.hovered {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Form focus effects */
        .focused {
            border-color: #6f42c1 !important;
            box-shadow: 0 0 0 0.2rem rgba(111, 66, 193, 0.25) !important;
        }
        
        /* Floating labels */
        .form-floating > .form-control.has-value ~ label,
        .form-floating > .form-control:focus ~ label {
            opacity: 0.75;
            transform: scale(0.85) translateY(-0.5rem) translateX(0.15rem);
        }
        
        /* Scroll animations */
        .animate-on-scroll {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .animate-on-scroll.scrolled {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);
}

// Add microinteraction styles when DOM is loaded
document.addEventListener('DOMContentLoaded', addMicrointeractionCSS);

// Enhanced notification system
window.notifications = {
    show: function(message, type = 'info', timeout = 5000) {
        // Remove any existing notifications of the same type
        const existingAlerts = document.querySelectorAll(`.alert-${type}`);
        existingAlerts.forEach(alert => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 500px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-left: 4px solid ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'};
        `;
        
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(alert);
        
        // Auto dismiss after specified timeout (except for error messages which should stay longer)
        if (type !== 'error' || timeout > 0) {
            setTimeout(function() {
                if (alert.parentNode) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, timeout);
        }
    },
    
    success: function(message, timeout = 5000) {
        this.show(message, 'success', timeout);
    },
    
    error: function(message, timeout = 0) {
        // Error messages should stay until manually dismissed, but we allow override
        this.show(message, 'error', timeout);
    },
    
    warning: function(message, timeout = 7000) {
        this.show(message, 'warning', timeout);
    },
    
    info: function(message, timeout = 5000) {
        this.show(message, 'info', timeout);
    }
};