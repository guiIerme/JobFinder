// Main JavaScript for Home Services Platform

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing event listeners');

    // Enable Bootstrap dropdowns (they should work automatically with data-bs-toggle="dropdown")
    // But we'll also manually initialize them to ensure they work
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function(dropdownToggleEl) {
        // Initialize the dropdown
        var dropdown = new bootstrap.Dropdown(dropdownToggleEl);

        // Also add click event listener to ensure it works
        dropdownToggleEl.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Toggle the dropdown
            dropdown.toggle();
        });

        return dropdown;
    });

    console.log('Dropdowns initialized:', dropdownList.length);

    // Also attach event listener when modal is shown
    const modal = document.getElementById('serviceRequestModal');
    if (modal) {
        modal.addEventListener('shown.bs.modal', function() {
            console.log('Modal shown, attaching event listeners');

            // Small delay to ensure elements are fully loaded
            setTimeout(function() {
                // Attach event listener directly to the search button
                const searchButton = document.getElementById('modal-searchZipCode');
                if (searchButton) {
                    // Remove any existing event listeners to avoid duplicates
                    searchButton.removeEventListener('click', performCepLookup);
                    searchButton.addEventListener('click', function(e) {
                        console.log('Direct click event fired');
                        // Get the CEP value and search
                        const zipCodeInput = document.getElementById('modal-zip_code');
                        if (zipCodeInput) {
                            const cep = zipCodeInput.value.replace(/\D/g, '');
                            if (cep.length === 8) {
                                searchCEP(cep);
                            } else {
                                showAlert('Por favor, insira um CEP válido com 8 dígitos.', 'danger');
                            }
                        }
                    });
                }

                // Initialize multi-step form when modal is shown
                initializeMultiStepForm();
            }, 100);
        });

        // Add confirmation before closing if form has data
        const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Check if form has any data entered
                const form = document.getElementById('service-request-form');
                let hasData = false;

                if (form) {
                    const inputs = form.querySelectorAll('input, textarea, select');
                    for (let input of inputs) {
                        if (input.type === 'checkbox' || input.type === 'radio') {
                            if (input.checked) {
                                hasData = true;
                                break;
                            }
                        } else if (input.value.trim() !== '') {
                            hasData = true;
                            break;
                        }
                    }
                }

                // If form has data, show confirmation
                if (hasData) {
                    if (!confirm('Você tem certeza que deseja sair? Os dados não salvos serão perdidos.')) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }
                }
            });
        });

        // Ensure the modal can be closed properly
        modal.addEventListener('hidden.bs.modal', function() {
            console.log('Modal hidden, resetting form');
            // Reset the form when modal is closed
            const form = document.getElementById('service-request-form');
            if (form) {
                form.reset();
                // Remove validation classes
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                form.querySelectorAll('.was-validated').forEach(el => el.classList.remove('was-validated'));
            }
            // Reset step navigation
            const steps = modal.querySelectorAll('.step');
            steps.forEach((step, index) => {
                if (index === 0) {
                    step.classList.remove('d-none');
                } else {
                    step.classList.add('d-none');
                }
            });
            // Reset progress bar
            const progressBar = document.getElementById('request-progress');
            if (progressBar) {
                progressBar.style.width = '20%';
                progressBar.setAttribute('aria-valuenow', '1');
            }
            // Reset buttons
            const prevBtn = document.getElementById('prev-step');
            const nextBtn = document.getElementById('next-step');
            const submitBtn = document.getElementById('submit-service-request');
            if (prevBtn) prevBtn.style.display = 'none';
            if (nextBtn) nextBtn.classList.remove('d-none');
            if (submitBtn) submitBtn.classList.add('d-none');
        });
    }

    // Fallback: attach event listener directly if elements exist
    setTimeout(function() {
        const searchButton = document.getElementById('modal-searchZipCode');
        if (searchButton) {
            searchButton.addEventListener('click', function(e) {
                console.log('Fallback click event fired');
                // Get the CEP value and search
                const zipCodeInput = document.getElementById('modal-zip_code');
                if (zipCodeInput) {
                    const cep = zipCodeInput.value.replace(/\D/g, '');
                    if (cep.length === 8) {
                        searchCEP(cep);
                    } else {
                        showAlert('Por favor, insira um CEP válido com 8 dígitos.', 'danger');
                    }
                }
            });
        }
    }, 100);

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover focus'
        });
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Service request form handling
    const serviceRequestForm = document.getElementById('service-request-form');
    if (serviceRequestForm) {
        serviceRequestForm.addEventListener('submit', function(e) {
            // Prevent default submission since we're handling it in the multi-step form
            e.preventDefault();

            // The multi-step form handles submission, so we don't need to do anything here
            // The submit button in the modal will handle the actual submission
        });
    }

    // Profile form handling
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Show loading state
            const submitBtn = profileForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
            submitBtn.disabled = true;

            // Simulate API call
            setTimeout(function() {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                showAlert('Perfil atualizado com sucesso!', 'success');
            }, 1500);
        });
    }

    // Payment method form handling
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Add payment-specific validation
            const paymentType = document.getElementById('payment_type').value;
            const cardNumber = document.getElementById('card_number_last4').value;

            if (paymentType.includes('card') && (!cardNumber || cardNumber.length !== 4)) {
                showAlert('Por favor, insira os últimos 4 dígitos do cartão', 'danger');
                return false;
            }

            // Show loading state
            const submitBtn = paymentForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processando...';
            submitBtn.disabled = true;

            // Simulate API call
            setTimeout(function() {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
                showAlert('Método de pagamento adicionado com sucesso!', 'success');

                // Reset form
                paymentForm.reset();
            }, 1500);
        });
    }

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            performSearch(e.target.value);
        }, 300));
    }

    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            const filterType = this.getAttribute('data-filter');
            applyFilter(filterType);
        });
    });

    // Smooth scrolling for anchor links
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

    // Back to top button - Modern Design
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'back-to-top-btn';
    backToTopButton.setAttribute('aria-label', 'Voltar ao topo');
    backToTopButton.setAttribute('title', 'Voltar ao topo');
    document.body.appendChild(backToTopButton);

    // Add modern styles
    const style = document.createElement('style');
    style.textContent = `
        .back-to-top-btn {
            position: fixed;
            bottom: 30px;
            left: 25px;
            width: 55px;
            height: 55px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 1.3rem;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transform: translateY(20px) scale(0.8);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 9998;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .back-to-top-btn.show {
            opacity: 1;
            visibility: visible;
            transform: translateY(0) scale(1);
        }
        
        .back-to-top-btn:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .back-to-top-btn:active {
            transform: translateY(-2px) scale(1.05);
        }
        
        .back-to-top-btn i {
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-8px);
            }
            60% {
                transform: translateY(-4px);
            }
        }
        
        .back-to-top-btn:hover i {
            animation: none;
            transform: translateY(-3px);
        }
        
        @media (max-width: 768px) {
            .back-to-top-btn {
                bottom: 20px;
                left: 15px;
                width: 50px;
                height: 50px;
                font-size: 1.1rem;
            }
        }
    `;
    document.head.appendChild(style);

    // Show/hide button with smooth animation
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);

        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });

    // Smooth scroll to top with progress indication
    backToTopButton.addEventListener('click', function() {
        const scrollDuration = 600;
        const scrollStep = -window.scrollY / (scrollDuration / 15);

        const scrollInterval = setInterval(function() {
            if (window.scrollY !== 0) {
                window.scrollBy(0, scrollStep);
            } else {
                clearInterval(scrollInterval);
                // Add a little bounce effect when reaching top
                backToTopButton.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    backToTopButton.style.transform = '';
                }, 200);
            }
        }, 15);
    });
});

// Function to confirm service requests
function confirmServiceRequest(serviceId, serviceName) {
    if (confirm(`Tem certeza que deseja solicitar o serviço: ${serviceName}?`)) {
        // Show loading state
        showAlert('Processando solicitação...', 'info');

        // Simulate API call
        setTimeout(function() {
            showAlert('Solicitação enviada com sucesso! Você será redirecionado para a confirmação.', 'success');

            // Redirect to request page
            // window.location.href = `/request-service/${serviceId}/`;
        }, 2000);
    }
}

// Function to toggle password visibility
function togglePassword(fieldId, buttonId) {
    const field = document.getElementById(fieldId);
    const button = document.getElementById(buttonId);

    if (field.type === 'password') {
        field.type = 'text';
        button.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        field.type = 'password';
        button.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

// Function to format phone numbers
function formatPhoneNumber(value) {
    // Remove all non-digit characters
    const phoneNumber = value.replace(/\D/g, '');

    // Format as (XX) XXXXX-XXXX for Brazilian mobile numbers or (XX) XXXX-XXXX for landlines
    if (phoneNumber.length >= 11) {
        // Mobile number (11 digits): (XX) XXXXX-XXXX
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2, 7)}-${phoneNumber.slice(7, 11)}`;
    } else if (phoneNumber.length >= 10) {
        // Landline (10 digits): (XX) XXXX-XXXX
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2, 6)}-${phoneNumber.slice(6, 10)}`;
    } else if (phoneNumber.length >= 6) {
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2, 6)}-${phoneNumber.slice(6)}`;
    } else if (phoneNumber.length >= 2) {
        return `(${phoneNumber.slice(0, 2)}) ${phoneNumber.slice(2)}`;
    } else {
        return phoneNumber;
    }
}

// Apply phone number formatting to phone input fields
document.addEventListener('input', function(e) {
    if (e.target.type === 'tel') {
        e.target.value = formatPhoneNumber(e.target.value);
    }
});

// Add real-time formatting for phone field in modal
document.addEventListener('input', function(e) {
    if (e.target.id === 'modal-contact-phone') {
        e.target.value = formatPhoneNumber(e.target.value);
    }
});

// Function to show/hide payment method fields based on type
function updatePaymentFields() {
    const paymentType = document.getElementById('payment_type').value;
    const cardFields = document.getElementById('card-fields');

    if (paymentType.includes('card')) {
        cardFields.style.display = 'block';
    } else {
        cardFields.style.display = 'none';
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
                window.notifications.error(message, 0); // Error messages should stay until manually dismissed
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

    // Auto dismiss after 5 seconds (except for danger/error messages)
    if (type !== 'danger') {
        setTimeout(function() {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Perform search function
function performSearch(query) {
    if (query.length < 2) {
        // Reset search results
        document.querySelectorAll('.search-result').forEach(item => {
            item.style.display = 'block';
        });
        return;
    }

    // Show loading indicator
    const loadingIndicator = document.getElementById('search-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }

    // Simulate API call
    setTimeout(function() {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }

        // Filter results based on query
        document.querySelectorAll('.search-result').forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query.toLowerCase())) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });

        // Update result count
        const visibleItems = document.querySelectorAll('.search-result[style*="display: block"], .search-result:not([style*="display: none"])');
        const resultCount = document.getElementById('result-count');
        if (resultCount) {
            resultCount.textContent = `${visibleItems.length} resultados encontrados`;
        }
    }, 500);
}

// Apply filter function
function applyFilter(filterType) {
    // Show loading indicator
    const loadingIndicator = document.getElementById('filter-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }

    // Simulate API call
    setTimeout(function() {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }

        // Apply filter logic
        document.querySelectorAll('.filterable-item').forEach(item => {
            const itemCategory = item.getAttribute('data-category');
            const itemRating = parseFloat(item.getAttribute('data-rating'));
            const itemPrice = parseFloat(item.getAttribute('data-price'));

            let show = true;

            switch (filterType) {
                case 'all':
                    show = true;
                    break;
                case 'high-rated':
                    show = itemRating >= 4.5;
                    break;
                case 'low-price':
                    show = itemPrice <= 100;
                    break;
                case 'urgent':
                    // This would depend on availability data
                    show = true;
                    break;
                default:
                    if (itemCategory) {
                        show = itemCategory === filterType;
                    }
                    break;
            }

            item.style.display = show ? 'block' : 'none';
        });

        // Update result count
        const visibleItems = document.querySelectorAll('.filterable-item[style*="display: block"], .filterable-item:not([style*="display: none"])');
        const resultCount = document.getElementById('result-count');
        if (resultCount) {
            resultCount.textContent = `${visibleItems.length} resultados encontrados`;
        }
    }, 300);
}

// Function to open the service request modal
function openServiceRequestModal(serviceId, serviceName, serviceDescription, servicePrice, serviceCategory) {
    console.log('Opening service request modal with:', {
        serviceId,
        serviceName,
        serviceDescription,
        servicePrice,
        serviceCategory
    });

    // Set the service details in the modal
    document.getElementById('modal-service-name').textContent = serviceName || 'Serviço Personalizado';
    document.getElementById('modal-service-description').textContent = serviceDescription || 'Descreva suas necessidades específicas';
    document.getElementById('modal-service-price').textContent = 'R$ ' + (servicePrice || '0,00');
    document.getElementById('modal-service-category').textContent = serviceCategory || 'Personalizado';

    // Store service ID in a data attribute for form submission
    const modal = document.getElementById('serviceRequestModal');
    if (serviceId) {
        modal.setAttribute('data-service-id', serviceId);
    } else {
        modal.removeAttribute('data-service-id');
    }

    // Set minimum date to today
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');

    const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    const scheduledDateInput = document.getElementById('modal-scheduled_date');
    if (scheduledDateInput) {
        scheduledDateInput.min = minDateTime;
    }

    // Clear form fields
    const form = document.getElementById('service-request-form');
    if (form) {
        form.reset();
        // Remove validation classes
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.was-validated').forEach(el => el.classList.remove('was-validated'));
    }

    // Auto-populate user contact information if available
    if (typeof window.userProfile !== 'undefined') {
        console.log('Populating user profile data');
        if (window.userProfile.name) {
            document.getElementById('modal-contact-name').value = window.userProfile.name;
        }
        if (window.userProfile.email) {
            document.getElementById('modal-contact-email').value = window.userProfile.email;
        }
        if (window.userProfile.phone) {
            document.getElementById('modal-contact-phone').value = window.userProfile.phone;
        }
        if (window.userProfile.address) {
            document.getElementById('modal-address').value = window.userProfile.address;
        }
        if (window.userProfile.number) {
            document.getElementById('modal-number').value = window.userProfile.number;
        }
        if (window.userProfile.complement) {
            document.getElementById('modal-complement').value = window.userProfile.complement;
        }
        if (window.userProfile.city) {
            document.getElementById('modal-city').value = window.userProfile.city;
        }
        if (window.userProfile.state) {
            document.getElementById('modal-state').value = window.userProfile.state;
        }
        if (window.userProfile.zipCode) {
            document.getElementById('modal-zip_code').value = window.userProfile.zipCode;
        }
    } else {
        console.log('No user profile data available');
    }

    // Show the modal
    console.log('Showing modal');
    var modalInstance = new bootstrap.Modal(document.getElementById('serviceRequestModal'));
    modalInstance.show();

    // Initialize multi-step form after a small delay to ensure modal is fully shown
    setTimeout(function() {
        console.log('Initializing multi-step form');
        initializeMultiStepForm();
    }, 100);
}

// Format CEP input
document.addEventListener('input', function(e) {
    if (e.target.id === 'modal-zip_code' || e.target.id === 'zip_code') {
        console.log('CEP input changed:', e.target.value);
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 5) {
            value = value.substring(0, 5) + '-' + value.substring(5, 8);
        }
        e.target.value = value;
        console.log('Formatted CEP:', value);
    }
});

// Unified CEP lookup function
function lookupCEP() {
    console.log('Performing CEP lookup via lookupCEP function');
    performCepLookup();
}

// Function to perform CEP lookup - unified function
function performCepLookup() {
    console.log('Performing CEP lookup');
    const zipCodeInput = document.getElementById('modal-zip_code');
    if (!zipCodeInput) {
        console.log('ZIP code input not found');
        return;
    }

    const zipCode = zipCodeInput.value.replace(/\D/g, '');
    console.log('ZIP code:', zipCode);

    if (zipCode.length !== 8) {
        showAlert('Por favor, insira um CEP válido com 8 dígitos.', 'danger');
        return;
    }

    // Show loading state
    const searchButton = document.getElementById('modal-searchZipCode');
    if (!searchButton) {
        console.log('Search button not found');
        return;
    }

    const originalText = searchButton.innerHTML;
    searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
    searchButton.disabled = true;

    // Make API call to ViaCEP service
    fetch(`https://viacep.com.br/ws/${zipCode}/json/`)
        .then(response => {
            console.log('Response received:', response);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data);
            // Check if the response contains an error
            if (data.erro) {
                showAlert('CEP não encontrado. Por favor, verifique o número e tente novamente.', 'danger');
                return;
            }

            // Populate fields with returned data
            const addressInput = document.getElementById('modal-address');
            const cityInput = document.getElementById('modal-city');
            const stateSelect = document.getElementById('modal-state');

            if (addressInput && data.logradouro) {
                addressInput.value = data.logradouro;
            }
            if (cityInput && data.localidade) {
                cityInput.value = data.localidade;
            }

            // Set state value by finding the option that matches the UF
            if (stateSelect && data.uf) {
                for (let i = 0; i < stateSelect.options.length; i++) {
                    if (stateSelect.options[i].value === data.uf) {
                        stateSelect.selectedIndex = i;
                        break;
                    }
                }
            }

            // Show success message
            showAlert('CEP encontrado com sucesso!', 'success');
        })
        .catch(error => {
            console.error('Error fetching CEP data:', error);
            showAlert('Erro ao buscar CEP. Por favor, tente novamente.', 'danger');
        })
        .finally(() => {
            // Restore button
            searchButton.innerHTML = originalText;
            searchButton.disabled = false;
        });
}

// Function to save ZIP code to user profile
function saveZipCodeToProfile(zipCode) {
    // Get CSRF token
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        showAlert('Erro de segurança. Por favor, recarregue a página.', 'danger');
        return;
    }

    // Make AJAX request to save ZIP code
    fetch('/save-zip-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: 'zip_code=' + encodeURIComponent(zipCode)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
            } else {
                showAlert(data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error saving ZIP code:', error);
            showAlert('Erro ao salvar CEP no perfil', 'danger');
        });
}

// Helper function to get CSRF token - unified approach
function getCSRFToken() {
    // First try to get from meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }

    // Fallback: try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }

    // Final fallback: try to get from hidden input in forms
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }

    console.warn('CSRF token not found');
    return null;
}

// Submit service request
document.addEventListener('click', function(e) {
    if (e.target.id === 'submit-service-request') {
        // Get form data
        const form = document.getElementById('service-request-form');
        const formData = new FormData(form);

        // Add CSRF token
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken);
        }

        // Form validation
        if (form.checkValidity()) {
            // Show loading state
            const submitBtn = document.getElementById('submit-service-request');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processando...';
            submitBtn.disabled = true;

            // Get service ID from modal data attribute
            const modal = document.getElementById('serviceRequestModal');
            const serviceId = modal.getAttribute('data-service-id');

            // Submit form via AJAX
            fetch(`/request-service-from-search/${serviceId}/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success notification
                        showAlert(data.message, 'success');

                        // Close the modal after a short delay
                        setTimeout(function() {
                            var modal = bootstrap.Modal.getInstance(document.getElementById('serviceRequestModal'));
                            modal.hide();

                            // Optionally redirect to confirmation page
                            if (data.redirect_url) {
                                window.location.href = data.redirect_url;
                            }
                        }, 2000);
                    } else {
                        // Show error notification
                        showAlert(data.message, 'danger');

                        // Highlight error fields if provided
                        if (data.errors) {
                            // Clear previous error highlights
                            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

                            // Highlight fields with errors
                            Object.keys(data.errors).forEach(fieldName => {
                                const field = document.getElementById(`modal-${fieldName}`) || document.querySelector(`[name="${fieldName}"]`);
                                if (field) {
                                    field.classList.add('is-invalid');

                                    // Add specific error message if available
                                    const feedback = field.parentNode.querySelector('.invalid-feedback');
                                    if (feedback) {
                                        feedback.textContent = data.errors[fieldName];
                                    }
                                }
                            });
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Show error notification
                    showAlert('Erro ao enviar solicitação de serviço', 'danger');
                })
                .finally(() => {
                    // Restore button state
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                });
        } else {
            // Show validation error notification
            showAlert('Por favor, preencha todos os campos obrigatórios', 'danger');
        }
    }
});

// Mobile menu toggle
document.addEventListener('click', function(e) {
    // Close mobile menu when clicking outside
    const navbarCollapse = document.getElementById('navbar-collapse');
    const navbarToggler = document.getElementById('navbar-toggler');

    if (navbarCollapse && navbarToggler) {
        if (navbarCollapse.classList.contains('show') &&
            !navbarCollapse.contains(e.target) &&
            e.target !== navbarToggler &&
            !navbarToggler.contains(e.target)) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                toggle: false
            });
            bsCollapse.hide();
        }
    }
});

// Add loading state to all buttons on click
document.addEventListener('click', function(e) {
    const button = e.target.closest('button');
    if (button && !button.disabled && !button.classList.contains('no-loading')) {
        // Don't add loading state to modal navigation buttons to avoid conflicts
        if (button.id !== 'prev-step' && button.id !== 'next-step' && button.id !== 'submit-service-request') {
            button.addEventListener('click', function() {
                if (this.type !== 'submit') {
                    const originalContent = this.innerHTML;
                    this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
                    this.disabled = true;

                    setTimeout(() => {
                        this.innerHTML = originalContent;
                        this.disabled = false;
                    }, 1000);
                }
            }, {
                once: true
            });
        }
    }
});

// Floating Menu Functionality
document.addEventListener('DOMContentLoaded', function() {
    const floatingMenu = document.getElementById('floatingMenu');
    const floatingMenuToggle = document.getElementById('floatingMenuToggle');
    const floatingMenuItems = document.getElementById('floatingMenuItems');

    if (floatingMenu && floatingMenuToggle && floatingMenuItems) {
        // Toggle menu on button click
        floatingMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            floatingMenuItems.classList.toggle('open');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!floatingMenu.contains(e.target) && !floatingMenuToggle.contains(e.target)) {
                floatingMenuToggle.classList.remove('active');
                floatingMenuItems.classList.remove('open');
            }
        });

        // Close menu when clicking on a menu item
        const menuItems = floatingMenuItems.querySelectorAll('.floating-menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                floatingMenuToggle.classList.remove('active');
                floatingMenuItems.classList.remove('open');
            });
        });
    }

    // Top Navigation Menu for Services Page
    const topNavLinks = document.querySelectorAll('.top-nav-menu a');
    if (topNavLinks.length > 0) {
        topNavLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Remove active class from all links
                topNavLinks.forEach(l => {
                    l.classList.remove('text-primary');
                    l.classList.add('text-muted');
                });

                // Add active class to clicked link
                this.classList.remove('text-muted');
                this.classList.add('text-primary');

                // Handle specific actions based on the link clicked
                const linkText = this.querySelector('span').textContent;

                switch (linkText) {
                    case 'Próximos':
                        // Filter by nearby professionals
                        filterByNearby();
                        break;
                    case 'Melhor Avaliados':
                        // Filter by highly rated professionals
                        filterByRating();
                        break;
                    case 'Urgentes':
                        // Filter by urgent services
                        filterByUrgent();
                        break;
                    default:
                        // For 'Buscar' and 'Filtros', no special action needed
                        break;
                }
            });
        });
    }
});

// Filter functions for the top navigation menu
function filterByNearby() {
    // This would filter the results by nearby professionals
    // In a real implementation, this would make an AJAX call to filter the results
    console.log('Filtering by nearby professionals');
    showAlert('Filtrando por profissionais próximos', 'info');
}

function filterByRating() {
    // This would filter the results by highly rated professionals
    console.log('Filtering by highly rated professionals');
    showAlert('Filtrando por profissionais bem avaliados', 'info');

    // In a real implementation, you would sort the results by rating
    // For now, we'll just show an alert
}

function filterByUrgent() {
    // This would filter the results by urgent services
    console.log('Filtering by urgent services');
    showAlert('Filtrando por serviços urgentes', 'info');

    // In a real implementation, you would filter the results by urgent services
    // For now, we'll just show an alert
}

// Multi-step service request form functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking for service request modal');

    // Also attach event listener when modal is shown
    const modal = document.getElementById('serviceRequestModal');
    if (modal) {
        console.log('Service request modal found');

        modal.addEventListener('shown.bs.modal', function() {
            console.log('Modal shown, attaching event listeners');

            // Small delay to ensure elements are fully loaded
            setTimeout(function() {
                // Attach event listener directly to the search button
                const searchButton = document.getElementById('modal-searchZipCode');
                if (searchButton) {
                    console.log('Search button found, attaching event listener');
                    // Remove any existing event listeners to avoid duplicates
                    searchButton.removeEventListener('click', performCepLookup);
                    searchButton.addEventListener('click', function(e) {
                        console.log('Direct click event fired on search button');
                        performCepLookup();
                    });
                } else {
                    console.log('Search button not found');
                }

                // Initialize multi-step form when modal is shown
                initializeMultiStepForm();
            }, 100);
        });

        // Add confirmation before closing if form has data
        const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Check if form has any data entered
                const form = document.getElementById('service-request-form');
                let hasData = false;

                if (form) {
                    const inputs = form.querySelectorAll('input, textarea, select');
                    for (let input of inputs) {
                        if (input.type === 'checkbox' || input.type === 'radio') {
                            if (input.checked) {
                                hasData = true;
                                break;
                            }
                        } else if (input.value.trim() !== '') {
                            hasData = true;
                            break;
                        }
                    }
                }

                // If form has data, show confirmation
                if (hasData) {
                    if (!confirm('Você tem certeza que deseja sair? Os dados não salvos serão perdidos.')) {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }
                }
            });
        });

        // Ensure the modal can be closed properly
        modal.addEventListener('hidden.bs.modal', function() {
            console.log('Modal hidden, resetting form');
            // Reset the form when modal is closed
            const form = document.getElementById('service-request-form');
            if (form) {
                form.reset();
                // Remove validation classes
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                form.querySelectorAll('.was-validated').forEach(el => el.classList.remove('was-validated'));
            }
            // Reset step navigation
            const steps = modal.querySelectorAll('.step');
            steps.forEach((step, index) => {
                if (index === 0) {
                    step.classList.remove('d-none');
                } else {
                    step.classList.add('d-none');
                }
            });
            // Reset progress bar
            const progressBar = document.getElementById('request-progress');
            if (progressBar) {
                progressBar.style.width = '20%';
                progressBar.setAttribute('aria-valuenow', '1');
            }
            // Reset buttons
            const prevBtn = document.getElementById('prev-step');
            const nextBtn = document.getElementById('next-step');
            const submitBtn = document.getElementById('submit-service-request');
            if (prevBtn) prevBtn.style.display = 'none';
            if (nextBtn) nextBtn.classList.remove('d-none');
            if (submitBtn) submitBtn.classList.add('d-none');
        });
    } else {
        console.log('Service request modal not found');
    }

    // Fallback: attach event listener directly if elements exist
    setTimeout(function() {
        const searchButton = document.getElementById('modal-searchZipCode');
        if (searchButton) {
            console.log('Attaching fallback event listener to search button');
            searchButton.addEventListener('click', function(e) {
                console.log('Fallback click event fired');
                performCepLookup();
            });
        }
    }, 100);

    // Initialize multi-step form (fallback for direct page loads)
    // Note: The main initialization happens when the modal is shown
});

function initializeMultiStepForm() {
    const modal = document.getElementById('serviceRequestModal');
    if (!modal) return;

    // Check if multi-step form is already initialized
    if (modal.dataset.multistepInitialized) {
        return;
    }

    // Mark as initialized
    modal.dataset.multistepInitialized = 'true';

    // Get all step elements
    const steps = modal.querySelectorAll('.step');
    const prevBtn = document.getElementById('prev-step');
    const nextBtn = document.getElementById('next-step');
    const submitBtn = document.getElementById('submit-service-request');
    const progressBar = document.getElementById('request-progress');

    if (!steps.length || !prevBtn || !nextBtn || !submitBtn || !progressBar) return;

    let currentStep = 1;
    const totalSteps = steps.length;

    // Show the first step
    showStep(currentStep);

    // Previous button event
    prevBtn.addEventListener('click', function() {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    });

    // Next button event
    nextBtn.addEventListener('click', function() {
        // Validate current step before proceeding
        if (validateStep(currentStep)) {
            if (currentStep < totalSteps) {
                currentStep++;
                showStep(currentStep);
            }
        } else {
            // Show validation error notification
            if (typeof window.notifications !== 'undefined') {
                window.notifications.error('Por favor, corrija os erros no formulário antes de continuar');
            }
        }
    });

    // Submit button event
    submitBtn.addEventListener('click', function() {
        // Validate last step before submitting
        if (validateStep(currentStep)) {
            // Get form data
            const form = document.getElementById('service-request-form');
            const formData = new FormData(form);

            // Get service ID from modal data attribute
            const modal = document.getElementById('serviceRequestModal');
            const serviceId = modal.getAttribute('data-service-id');

            // Add CSRF token
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken);
            }

            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processando...';
            this.disabled = true;
            prevBtn.disabled = true;
            nextBtn.disabled = true;

            // Submit form via AJAX
            fetch(`/request-service-from-search/${serviceId}/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success animation
                        showSuccessAnimation();

                        // Show success notification
                        showAlert(data.message, 'success');

                        // Close the modal after a short delay
                        setTimeout(function() {
                            var modal = bootstrap.Modal.getInstance(document.getElementById('serviceRequestModal'));
                            modal.hide();

                            // Optionally redirect to confirmation page
                            if (data.redirect_url) {
                                window.location.href = data.redirect_url;
                            }
                        }, 2000);
                    } else {
                        // Show error notification
                        showAlert(data.message, 'danger');

                        // Highlight error fields if provided
                        if (data.errors) {
                            // Clear previous error highlights
                            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

                            // Highlight fields with errors
                            Object.keys(data.errors).forEach(fieldName => {
                                const field = document.getElementById(`modal-${fieldName}`) || document.querySelector(`[name="${fieldName}"]`);
                                if (field) {
                                    field.classList.add('is-invalid');

                                    // Add specific error message if available
                                    const feedback = field.parentNode.querySelector('.invalid-feedback');
                                    if (feedback) {
                                        feedback.textContent = data.errors[fieldName];
                                    }
                                }
                            });
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Show error notification
                    showAlert('Erro ao enviar solicitação de serviço. Por favor, verifique sua conexão e tente novamente.', 'danger');
                })
                .finally(() => {
                    // Restore button state
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    prevBtn.disabled = false;
                    nextBtn.disabled = false;
                });
        } else {
            // Show validation error notification
            if (typeof window.notifications !== 'undefined') {
                window.notifications.error('Por favor, preencha todos os campos obrigatórios corretamente.');
            } else {
                alert('Por favor, preencha todos os campos obrigatórios corretamente.');
            }
        }
    });

    // Function to show a specific step
    function showStep(stepNumber) {
        // Hide all steps
        steps.forEach(step => {
            step.classList.add('d-none');
        });

        // Show current step
        document.getElementById(`step-${stepNumber}`).classList.remove('d-none');

        // Update progress bar
        const progressPercentage = (stepNumber / totalSteps) * 100;
        progressBar.style.width = `${progressPercentage}%`;
        progressBar.setAttribute('aria-valuenow', stepNumber);

        // Update button visibility
        if (stepNumber === 1) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'inline-block';
        }

        if (stepNumber === totalSteps) {
            nextBtn.classList.add('d-none');
            submitBtn.classList.remove('d-none');
        } else {
            nextBtn.classList.remove('d-none');
            submitBtn.classList.add('d-none');
        }

        // Update payment amount if on payment step
        if (stepNumber === 5) {
            const servicePrice = document.getElementById('modal-service-price').textContent;
            document.getElementById('payment-amount').textContent = servicePrice;
        }
    }

    // Function to validate a step
    function validateStep(stepNumber) {
        const currentStepElement = document.getElementById(`step-${stepNumber}`);
        const inputs = currentStepElement.querySelectorAll('input[required], select[required], textarea[required]');

        let isValid = true;

        inputs.forEach(input => {
            if (!input.checkValidity()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });

        // Special validation for step 1 (address)
        if (stepNumber === 1) {
            const zipCode = document.getElementById('modal-zip_code');

            // Validate CEP format (8 digits with optional hyphen)
            const zipCodeValue = zipCode.value.replace(/\D/g, '');
            if (zipCode.value && zipCodeValue.length !== 8) {
                zipCode.classList.add('is-invalid');
                isValid = false;
            } else {
                zipCode.classList.remove('is-invalid');
            }
        }

        // Special validation for step 2 (schedule)
        if (stepNumber === 2) {
            const scheduledDate = document.getElementById('modal-scheduled_date');
            const now = new Date();
            const selectedDate = new Date(scheduledDate.value);

            if (scheduledDate.value && selectedDate < now) {
                scheduledDate.setCustomValidity('A data deve ser futura');
                scheduledDate.classList.add('is-invalid');
                isValid = false;
            } else {
                scheduledDate.setCustomValidity('');
                scheduledDate.classList.remove('is-invalid');
            }
        }

        // Special validation for step 3 (contact)
        if (stepNumber === 3) {
            const email = document.getElementById('modal-contact-email');
            const phone = document.getElementById('modal-contact-phone');

            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email.value && !emailRegex.test(email.value)) {
                email.classList.add('is-invalid');
                isValid = false;
            } else {
                email.classList.remove('is-invalid');
            }

            // Validate phone format (Brazilian format: (61) 98196-1144 or (61) 8196-1144)
            const phoneRegex = /^\(?[0-9]{2}\)? [0-9]{4,5}-[0-9]{4}$/;
            if (phone.value && !phoneRegex.test(phone.value)) {
                phone.classList.add('is-invalid');
                isValid = false;
            } else {
                phone.classList.remove('is-invalid');
            }
        }

        // Special validation for step 5 (payment)
        if (stepNumber === 5) {
            const terms = document.getElementById('modal-terms');
            if (!terms.checked) {
                terms.classList.add('is-invalid');
                isValid = false;
            } else {
                terms.classList.remove('is-invalid');
            }
        }

        return isValid;
    }

    // Add real-time validation for inputs
    modal.addEventListener('input', function(e) {
        if (e.target.hasAttribute('required') || e.target.type === 'email' || e.target.type === 'tel') {
            if (e.target.checkValidity()) {
                e.target.classList.remove('is-invalid');
            }
        }
    });

    // Add validation for CEP input
    const zipCodeInput = document.getElementById('modal-zip_code');
    if (zipCodeInput) {
        zipCodeInput.addEventListener('input', function() {
            // Remove any existing invalid class when user types
            this.classList.remove('is-invalid');

            // Format CEP as user types (XXXXX-XXX)
            let value = this.value.replace(/\D/g, '');
            if (value.length > 5) {
                value = value.substring(0, 5) + '-' + value.substring(5, 8);
            }
            this.value = value;
        });

        // Add blur event to search CEP when user finishes typing
        zipCodeInput.addEventListener('blur', function() {
            const cep = this.value.replace(/\D/g, '');
            if (cep.length === 8) {
                searchCEP(cep);
            }
        });
    }

    // Search CEP button click event
    const searchCEPButton = document.getElementById('modal-searchZipCode');
    if (searchCEPButton) {
        searchCEPButton.addEventListener('click', function() {
            const cep = zipCodeInput.value.replace(/\D/g, '');
            if (cep.length === 8) {
                searchCEP(cep);
            }
        });
    }

    // Function to search CEP using ViaCEP API
    function searchCEP(cep) {
        // Show loading state
        const searchButton = document.getElementById('modal-searchZipCode');
        const originalButtonText = searchButton.innerHTML;
        searchButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';
        searchButton.disabled = true;

        // Make API call to ViaCEP
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.erro) {
                    throw new Error('CEP não encontrado');
                }

                // Populate fields with returned data
                if (data.logradouro) {
                    document.getElementById('modal-address').value = data.logradouro;
                }
                if (data.bairro) {
                    // We don't have a bairro field in the form, but we could add one
                }
                if (data.localidade) {
                    document.getElementById('modal-city').value = data.localidade;
                }
                if (data.uf) {
                    document.getElementById('modal-state').value = data.uf;
                }

                // Show success notification
                showAlert('CEP encontrado com sucesso!', 'success');
            })
            .catch(error => {
                console.error('Error fetching CEP:', error);
                showAlert('Erro ao buscar CEP. Por favor, verifique o número e tente novamente.', 'danger');
            })
            .finally(() => {
                // Restore button
                searchButton.innerHTML = originalButtonText;
                searchButton.disabled = false;
            });
    }
}

// Function to show success animation
function showSuccessAnimation() {
    const modalContent = document.querySelector('#serviceRequestModal .modal-content');
    if (modalContent) {
        // Add a temporary success animation class
        modalContent.classList.add('success-animation');

        // Remove the class after animation completes
        setTimeout(() => {
            modalContent.classList.remove('success-animation');
        }, 2000);
    }
}

// Function to ensure footer appears only when scrolling to bottom
function handleFooterPosition() {
    const footer = document.querySelector('footer');
    if (footer) {
        // Remove any fixed positioning classes that might force footer to always be visible
        footer.classList.remove('fixed-bottom');

        // Ensure footer is positioned naturally in the document flow
        footer.style.position = 'relative';
        footer.style.bottom = 'auto';
    }
}

// Call the function when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    handleFooterPosition();
});

// Function to get CSRF token
function getCSRFToken() {
    // Try to get CSRF token from meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }

    // Try to get CSRF token from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }

    // Try to get CSRF token from form
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }

    return null;
}

// Function to open the service request modal
function openServiceRequestModal(serviceId, serviceName, serviceDescription, servicePrice, serviceCategory) {
    // Reset form and show first step
    const form = document.getElementById('service-request-form');
    if (form) {
        form.reset();
        // Remove validation classes
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('.was-validated').forEach(el => el.classList.remove('was-validated'));
    }

    // Reset step navigation
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        if (index === 0) {
            step.classList.remove('d-none');
        } else {
            step.classList.add('d-none');
        }
    });

    // Reset progress bar
    const progressBar = document.getElementById('request-progress');
    if (progressBar) {
        progressBar.style.width = '20%';
        progressBar.setAttribute('aria-valuenow', '1');
    }

    // Reset buttons
    const prevBtn = document.getElementById('prev-step');
    const nextBtn = document.getElementById('next-step');
    const submitBtn = document.getElementById('submit-service-request');
    if (prevBtn) prevBtn.style.display = 'none';
    if (nextBtn) nextBtn.classList.remove('d-none');
    if (submitBtn) submitBtn.classList.add('d-none');

    // Set service details
    if (serviceName) document.getElementById('service_name').value = serviceName;
    if (serviceDescription) document.getElementById('description').value = serviceDescription;

    // Set price details
    if (servicePrice) {
        document.getElementById('summary-service-name').textContent = serviceName;
        document.getElementById('summary-base-price').textContent = `R$ ${parseFloat(servicePrice).toFixed(2)}`;
        document.getElementById('summary-total-price').textContent = `R$ ${parseFloat(servicePrice).toFixed(2)}`;
    }

    // Load payment methods
    loadPaymentMethods();

    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('serviceRequestModal'));
    modal.show();
}

// Function to load payment methods for the current user
function loadPaymentMethods() {
    // In a real implementation, this would fetch payment methods from the server
    // For now, we'll simulate with sample data
    const container = document.getElementById('payment-methods-container');
    if (!container) return;

    // Check if user has payment methods (simulated)
    const hasPaymentMethods = true; // This would come from the server

    if (hasPaymentMethods) {
        // Sample payment methods (in a real app, this would come from the server)
        const paymentMethods = [{
                id: 1,
                type: 'credit_card',
                last4: '1234',
                name: 'Cartão de Crédito',
                isDefault: true
            },
            {
                id: 2,
                type: 'debit_card',
                last4: '5678',
                name: 'Cartão de Débito',
                isDefault: false
            }
        ];

        let html = '';
        paymentMethods.forEach(method => {
            html += `
                <div class="form-check mb-3 border rounded-3 p-3 ${method.isDefault ? 'border-primary' : ''}">
                    <input class="form-check-input" type="radio" name="payment_method" id="payment-${method.id}" value="${method.id}" ${method.isDefault ? 'checked' : ''}>
                    <label class="form-check-label d-flex align-items-center" for="payment-${method.id}">
                        <div class="bg-primary text-white rounded me-3 d-flex align-items-center justify-content-center" style="width: 50px; height: 30px;">
                            <span class="small fw-bold">
                                ${method.type === 'credit_card' ? 'VISA' : method.type === 'debit_card' ? 'DEBIT' : method.type === 'pix' ? 'PIX' : 'BANK'}
                            </span>
                        </div>
                        <div>
                            <div class="fw-bold">${method.name}</div>
                            ${method.last4 ? `<div class="small text-muted">•••• ${method.last4}</div>` : ''}
                            ${method.isDefault ? `<span class="badge bg-primary ms-2">Padrão</span>` : ''}
                        </div>
                    </label>
                </div>
            `;
        });

        container.innerHTML = html;
    } else {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-credit-card fa-2x text-muted mb-3"></i>
                <p class="text-muted mb-0">Nenhum método de pagamento cadastrado</p>
            </div>
        `;
    }
}

// Function to toggle the new payment method form
function toggleNewPaymentMethodForm() {
    const form = document.getElementById('new-payment-method-form');
    if (form) {
        form.classList.toggle('d-none');
    }
}

// Function to initialize the multi-step form
function initializeMultiStepForm() {
    const steps = document.querySelectorAll('.step');
    const progressBar = document.getElementById('request-progress');
    const prevBtn = document.getElementById('prev-step');
    const nextBtn = document.getElementById('next-step');
    const submitBtn = document.getElementById('submit-service-request');

    let currentStep = 1;
    const totalSteps = steps.length;

    // Update step display
    function updateStep() {
        // Hide all steps
        steps.forEach(step => step.classList.add('d-none'));

        // Show current step
        if (steps[currentStep - 1]) {
            steps[currentStep - 1].classList.remove('d-none');
        }

        // Update progress bar
        if (progressBar) {
            const progress = (currentStep / totalSteps) * 100;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', currentStep);
        }

        // Update buttons
        if (prevBtn) {
            prevBtn.style.display = currentStep === 1 ? 'none' : 'block';
        }

        if (nextBtn && submitBtn) {
            if (currentStep === totalSteps) {
                nextBtn.classList.add('d-none');
                submitBtn.classList.remove('d-none');
            } else {
                nextBtn.classList.remove('d-none');
                submitBtn.classList.add('d-none');
            }
        }
    }

    // Next button click handler
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            // Validate current step before proceeding
            const currentStepElement = steps[currentStep - 1];
            if (currentStepElement) {
                const inputs = currentStepElement.querySelectorAll('input, select, textarea');
                let isValid = true;

                // Check required fields
                inputs.forEach(input => {
                    if (input.hasAttribute('required') && !input.value.trim()) {
                        input.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        input.classList.remove('is-invalid');
                    }
                });

                // Special validation for email
                const emailInput = currentStepElement.querySelector('input[type="email"]');
                if (emailInput && emailInput.value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(emailInput.value)) {
                        emailInput.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        emailInput.classList.remove('is-invalid');
                    }
                }

                // Special validation for phone
                const phoneInput = currentStepElement.querySelector('input[type="tel"]');
                if (phoneInput && phoneInput.value) {
                    const phoneRegex = /^\(\d{2}\) \d{4,5}-\d{4}$/;
                    if (!phoneRegex.test(phoneInput.value)) {
                        phoneInput.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        phoneInput.classList.remove('is-invalid');
                    }
                }

                if (isValid && currentStep < totalSteps) {
                    currentStep++;
                    updateStep();
                }
            }
        });
    }

    // Previous button click handler
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            if (currentStep > 1) {
                currentStep--;
                updateStep();
            }
        });
    }

    // Add event listener for the "Add New Payment Method" button
    const addPaymentBtn = document.getElementById('add-new-payment-method');
    if (addPaymentBtn) {
        addPaymentBtn.addEventListener('click', toggleNewPaymentMethodForm);
    }

    // Initialize the form
    updateStep();
}

// Function to submit the service request
function submitServiceRequest() {
    // Get form data
    const form = document.getElementById('service-request-form');
    if (!form) return;

    // Show loading state
    const submitBtn = document.getElementById('submit-service-request');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processando...';
    submitBtn.disabled = true;

    // In a real implementation, this would send the data to the server
    // For now, we'll simulate a successful submission
    setTimeout(function() {
        // Reset button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;

        // Show success message
        alert('Solicitação de serviço enviada com sucesso!');

        // Close the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('serviceRequestModal'));
        if (modal) {
            modal.hide();
        }

        // Reset form
        form.reset();
    }, 1500);
}