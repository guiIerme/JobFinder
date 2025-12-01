// Contact page specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Contact page loaded');

    // Get the contact form
    const contactForm = document.getElementById('contact-form');

    if (contactForm) {
        // Add form submission handler
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitContactForm();
        });
    }

    // Add input validation as user types
    const inputs = contactForm.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });

    // Add phone formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', formatPhoneNumber);
    }
});

// Function to format phone numbers
function formatPhoneNumber(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 11) {
        value = value.substring(0, 11);
    }
    if (value.length > 7) {
        value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (value.length > 6) {
        value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
    } else if (value.length > 2) {
        value = value.replace(/(\d{2})(\d{0,5})/, '($1) $2');
    } else if (value.length > 0) {
        value = value.replace(/(\d{0,2})/, '($1');
    }
    e.target.value = value;
}

// Function to validate individual fields
function validateField(field) {
    const fieldName = field.id;
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Remove any existing error classes
    field.classList.remove('is-invalid', 'is-valid');

    // Validate based on field type
    switch (fieldName) {
        case 'name':
            if (value.length < 2) {
                isValid = false;
                errorMessage = 'Por favor, insira seu nome completo';
            }
            break;

        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Por favor, insira um e-mail válido';
            }
            break;

        case 'phone':
            // Phone is optional, but if provided, validate
            if (value && value.replace(/\D/g, '').length < 10) {
                isValid = false;
                errorMessage = 'Por favor, insira um telefone válido';
            }
            break;

        case 'subject':
            if (value === '' || value === 'Selecione um assunto') {
                isValid = false;
                errorMessage = 'Por favor, selecione um assunto';
            }
            break;

        case 'message':
            if (value.length < 10) {
                isValid = false;
                errorMessage = 'Por favor, insira uma mensagem com pelo menos 10 caracteres';
            }
            break;

        case 'privacy':
            if (!field.checked) {
                isValid = false;
                errorMessage = 'Você precisa concordar com a Política de Privacidade';
            }
            break;
    }

    // Show validation feedback
    if (!isValid) {
        field.classList.add('is-invalid');
        // Find or create error message element
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = errorMessage;
    } else {
        field.classList.add('is-valid');
    }

    return isValid;
}

// Function to validate the entire form
function validateForm() {
    const form = document.getElementById('contact-form');
    const inputs = form.querySelectorAll('input, textarea, select, checkbox');
    let isFormValid = true;

    inputs.forEach(input => {
        if (!validateField(input)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

// Function to submit the contact form
function submitContactForm() {
    console.log('Submitting contact form');

    // Validate form
    if (!validateForm()) {
        showAlert('Por favor, corrija os erros no formulário antes de enviar.', 'warning');
        return;
    }

    // Get form data
    const form = document.getElementById('contact-form');
    const formData = new FormData(form);

    // Show loading state
    const submitButton = document.querySelector('#contact-form button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
    submitButton.disabled = true;

    // Submit form via AJAX
    fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                showAlert(data.message, 'success');

                // Reset form
                form.reset();

                // Remove validation classes
                const inputs = document.querySelectorAll('#contact-form .is-valid, #contact-form .is-invalid');
                inputs.forEach(input => {
                    input.classList.remove('is-valid', 'is-invalid');
                });

                // Show success animation
                showSuccessAnimation();

                // Scroll to top to show success message
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            } else {
                // Show error message
                showAlert(data.message || 'Erro ao enviar mensagem. Tente novamente.', 'danger');

                // Show field-specific errors
                if (data.errors) {
                    Object.keys(data.errors).forEach(fieldName => {
                        const field = document.getElementById(fieldName);
                        if (field) {
                            field.classList.add('is-invalid');
                            const errorElement = field.parentNode.querySelector('.invalid-feedback');
                            if (errorElement) {
                                errorElement.textContent = data.errors[fieldName];
                            }
                        }
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Erro de conexão. Verifique sua internet e tente novamente.', 'danger');
        })
        .finally(() => {
            // Restore button
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        });
}

// Function to show success animation
function showSuccessAnimation() {
    const form = document.getElementById('contact-form');
    const successAnimation = document.getElementById('successAnimation');

    if (form && successAnimation) {
        form.style.display = 'none';
        successAnimation.style.display = 'block';

        // Add event listener to reset button
        document.getElementById('resetFormBtn').addEventListener('click', function() {
            successAnimation.style.display = 'none';
            form.style.display = 'block';
            form.reset();
        });
    }
}

// Function to show alerts
function showAlert(message, type) {
    // Use the notification system if available
    if (typeof window.notifications !== 'undefined') {
        switch (type) {
            case 'success':
                window.notifications.success(message, 5000);
                break;
            case 'danger':
                window.notifications.error(message, 5000);
                break;
            case 'warning':
                window.notifications.warning(message, 7000);
                break;
            case 'info':
                window.notifications.info(message, 5000);
                break;
            default:
                window.notifications.info(message, 5000);
        }
        return;
    }

    // Fallback to old alert system if notifications are not available
    // Remove existing alerts
    const existingAlert = document.querySelector('.alert-fixed');
    if (existingAlert) {
        existingAlert.remove();
    }

    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-fixed position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
    alert.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'danger' ? 'fa-exclamation-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'} me-2"></i>
            <div>${message}</div>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // Add to body
    document.body.appendChild(alert);

    // Auto dismiss after 5 seconds
    setTimeout(function() {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Function to initialize map (if needed)
function initMap() {
    // This would initialize a map showing the company location
    // For now, we'll just log that it's called
    console.log('Initializing map');
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Live chat functionality
document.addEventListener('DOMContentLoaded', function() {
    const liveChatBtn = document.getElementById('liveChatBtn');
    if (liveChatBtn) {
        liveChatBtn.addEventListener('click', function() {
            var liveChatModal = new bootstrap.Modal(document.getElementById('liveChatModal'));
            liveChatModal.show();
        });
    }

    // Add smooth animations to stats
    const statsNumbers = document.querySelectorAll('.stats-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateNumber(entry.target);
            }
        });
    });

    statsNumbers.forEach(stat => {
        observer.observe(stat);
    });

    // Add hover effects to contact cards
    const contactCards = document.querySelectorAll('.contact-info-card');
    contactCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Function to animate numbers
function animateNumber(element) {
    const text = element.textContent;
    const number = parseInt(text.replace(/\D/g, ''));

    if (isNaN(number)) return;

    const duration = 2000;
    const increment = number / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
        current += increment;
        if (current >= number) {
            element.textContent = text;
            clearInterval(timer);
        } else {
            const suffix = text.replace(/[\d,]/g, '');
            element.textContent = Math.floor(current) + suffix;
        }
    }, 16);
}

// Add form auto-save functionality
let formAutoSave = {};

function saveFormData() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        if (key !== 'csrfmiddlewaretoken') {
            data[key] = value;
        }
    }

    localStorage.setItem('contactFormData', JSON.stringify(data));
}

function loadFormData() {
    const savedData = localStorage.getItem('contactFormData');
    if (!savedData) return;

    try {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = data[key] === 'on';
                } else {
                    field.value = data[key];
                }
            }
        });
    } catch (e) {
        console.error('Error loading form data:', e);
    }
}

// Auto-save form data as user types
document.addEventListener('DOMContentLoaded', function() {
    loadFormData();

    const form = document.getElementById('contact-form');
    if (form) {
        form.addEventListener('input', saveFormData);
        form.addEventListener('change', saveFormData);

        // Clear saved data on successful submission
        form.addEventListener('submit', function() {
            setTimeout(() => {
                localStorage.removeItem('contactFormData');
            }, 3000);
        });
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('contact-form');
        if (form && document.activeElement.closest('#contact-form')) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    }

    // Escape to close modal
    if (e.key === 'Escape') {
        const modal = bootstrap.Modal.getInstance(document.getElementById('liveChatModal'));
        if (modal) {
            modal.hide();
        }
    }
});