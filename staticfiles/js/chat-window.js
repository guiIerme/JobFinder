/**
 * ChatWindow - Manages the chat window interface and WebSocket communication
 * 
 * This class handles the chat window display, message sending/receiving,
 * WebSocket connection management, and user interactions.
 */

class ChatWindow {
    constructor(websocketUrl, options = {}) {
        // Configuration
        this.websocketUrl = websocketUrl || this.getWebSocketUrl();
        this.options = {
            windowId: options.windowId || 'chat-window',
            messagesId: options.messagesId || 'chat-messages',
            inputId: options.inputId || 'chat-input',
            formId: options.formId || 'chat-form',
            sendButtonId: options.sendButtonId || 'chat-send',
            closeButtonId: options.closeButtonId || 'chat-close',
            minimizeButtonId: options.minimizeButtonId || 'chat-minimize',
            typingIndicatorId: options.typingIndicatorId || 'chat-typing-indicator',
            connectionStatusId: options.connectionStatusId || 'chat-connection-status',
            maxHistoryMessages: options.maxHistoryMessages || 50,
            reconnectAttempts: options.reconnectAttempts || 5,
            reconnectDelay: options.reconnectDelay || 1000,
            ...options
        };

        // State
        this.isOpen = false;
        this.isMinimized = false;
        this.isConnected = false;
        this.isConnecting = false;
        this.sessionId = null;
        this.messageHistory = [];
        this.reconnectCount = 0;
        this.reconnectTimer = null;

        // WebSocket
        this.ws = null;

        // DOM elements
        this.window = null;
        this.messagesContainer = null;
        this.input = null;
        this.form = null;
        this.sendButton = null;
        this.closeButton = null;
        this.minimizeButton = null;
        this.typingIndicator = null;
        this.connectionStatus = null;
        this.ratingContainer = null;
        this.ratingStars = null;
        this.ratingSubmitBtn = null;
        this.ratingSkipBtn = null;

        // Rating state
        this.selectedRating = 0;
        this.ratingSubmitted = false;

        // Initialize
        this.init();
    }

    /**
     * Initialize the chat window
     */
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    /**
     * Setup the chat window after DOM is ready
     */
    setup() {
        // Get DOM elements
        this.window = document.getElementById(this.options.windowId);
        this.messagesContainer = document.getElementById(this.options.messagesId);
        this.input = document.getElementById(this.options.inputId);
        this.form = document.getElementById(this.options.formId);
        this.sendButton = document.getElementById(this.options.sendButtonId);
        this.closeButton = document.getElementById(this.options.closeButtonId);
        this.minimizeButton = document.getElementById(this.options.minimizeButtonId);
        this.typingIndicator = document.getElementById(this.options.typingIndicatorId);
        this.connectionStatus = document.getElementById(this.options.connectionStatusId);
        this.ratingContainer = document.getElementById('chat-rating-container');
        this.ratingStars = document.querySelectorAll('.rating-star');
        this.ratingSubmitBtn = document.getElementById('rating-submit');
        this.ratingSkipBtn = document.getElementById('rating-skip');

        if (!this.window) {
            console.error('Chat window element not found');
            return;
        }

        // Attach event listeners
        this.attachEventListeners();

        // Load session from localStorage
        this.loadSession();

        console.log('Chat window initialized');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Form submission
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSendMessage();
            });
        }

        // Close button
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.close());
        }

        // Minimize button
        if (this.minimizeButton) {
            this.minimizeButton.addEventListener('click', () => this.minimize());
        }

        // Input auto-resize
        if (this.input) {
            this.input.addEventListener('input', () => {
                this.autoResizeInput();
                this.updateCharCount();
            });

            // Handle Enter key (send) and Shift+Enter (new line)
            this.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });
        }

        // Listen for open request
        document.addEventListener('chat:open-requested', () => {
            this.open();
        });

        // Close chat when accessibility panel opens
        document.addEventListener('accessibility:opened', () => {
            if (this.isOpen) {
                console.log('Accessibility opened, closing chat');
                this.close();
            }
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Rating stars
        if (this.ratingStars) {
            this.ratingStars.forEach(star => {
                star.addEventListener('click', () => {
                    this.handleRatingSelect(parseInt(star.dataset.rating));
                });

                star.addEventListener('mouseenter', () => {
                    this.handleRatingHover(parseInt(star.dataset.rating));
                });
            });

            // Reset hover effect when leaving stars container
            const starsContainer = document.querySelector('.rating-stars');
            if (starsContainer) {
                starsContainer.addEventListener('mouseleave', () => {
                    this.updateRatingStars(this.selectedRating);
                });
            }
        }

        // Rating submit button
        if (this.ratingSubmitBtn) {
            this.ratingSubmitBtn.addEventListener('click', () => {
                this.submitRating();
            });
        }

        // Rating skip button
        if (this.ratingSkipBtn) {
            this.ratingSkipBtn.addEventListener('click', () => {
                this.skipRating();
            });
        }
    }

    /**
     * Get WebSocket URL based on current location
     */
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/chat/`;
    }

    /**
     * Open the chat window
     */
    open() {
        if (this.isOpen) {
            return;
        }

        this.isOpen = true;
        this.isMinimized = false;

        // Show window with animation
        this.window.style.display = 'flex';
        this.window.classList.add('opening');
        this.window.classList.remove('closing', 'minimized');

        // Remove animation class after animation completes
        setTimeout(() => {
            this.window.classList.remove('opening');
        }, 300);

        // Connect WebSocket if not connected
        if (!this.isConnected && !this.isConnecting) {
            this.connect();
        }

        // Focus input
        if (this.input) {
            setTimeout(() => this.input.focus(), 100);
        }

        // Load history if available
        this.loadHistory();

        // Dispatch event
        const event = new CustomEvent('chat:opened');
        document.dispatchEvent(event);

        // Save state
        this.saveState();

        console.log('Chat window opened');
    }

    /**
     * Close the chat window
     */
    close() {
        if (!this.isOpen) {
            return;
        }

        // Show rating prompt if there are messages and rating not submitted
        const hasMessages = this.messageHistory.length > 0;
        if (hasMessages && !this.ratingSubmitted) {
            this.showRatingPrompt();
            return; // Don't close yet, wait for rating
        }

        this.isOpen = false;

        // Close with animation
        this.window.classList.add('closing');
        this.window.classList.remove('opening');

        setTimeout(() => {
            this.window.style.display = 'none';
            this.window.classList.remove('closing');
        }, 300);

        // Dispatch event
        const event = new CustomEvent('chat:closed');
        document.dispatchEvent(event);

        // Save state
        this.saveState();

        console.log('Chat window closed');
    }

    /**
     * Toggle the chat window
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Minimize the chat window
     */
    minimize() {
        if (!this.isOpen) {
            return;
        }

        this.isMinimized = !this.isMinimized;

        if (this.isMinimized) {
            this.window.classList.add('minimized');
        } else {
            this.window.classList.remove('minimized');
        }

        // Save state
        this.saveState();

        console.log('Chat window minimized:', this.isMinimized);
    }

    /**
     * Maximize the chat window (un-minimize)
     */
    maximize() {
        if (!this.isMinimized) {
            return;
        }

        this.isMinimized = false;
        this.window.classList.remove('minimized');

        // Save state
        this.saveState();

        console.log('Chat window maximized');
    }

    /**
     * Send a message
     * @param {string} text - Message text
     */
    sendMessage(text) {
        if (!text || !text.trim()) {
            return;
        }

        const message = {
            type: 'user_message',
            content: text.trim(),
            timestamp: new Date().toISOString()
        };

        // Add to UI immediately
        this.addMessage({
            sender_type: 'user',
            content: message.content,
            created_at: message.timestamp
        });

        // Clear input
        if (this.input) {
            this.input.value = '';
            this.autoResizeInput();
            this.updateCharCount();
        }

        // Send via REST API
        this.sendMessageViaAPI(message.content);
    }

    /**
     * Send message via REST API
     * @param {string} messageText - Message text
     */
    async sendMessageViaAPI(messageText) {
        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Get current page context
            const context = {
                current_page: window.location.pathname,
                referrer: document.referrer
            };

            // Send to API
            const response = await fetch('/api/chat/message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    message: messageText,
                    session_id: this.sessionId,
                    context: context
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            // Update session ID
            if (data.session_id) {
                this.sessionId = data.session_id;
                this.saveSession();
            }

            // Add Sophie's response
            if (data.message) {
                this.receiveMessage({
                    sender_type: 'assistant',
                    content: data.message.content,
                    created_at: data.message.created_at,
                    metadata: data.message.metadata
                });
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showError('Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.');
        }
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.displayTypingIndicator();
    }

    /**
     * Connect to WebSocket
     */
    connect() {
        if (this.isConnecting || this.isConnected) {
            return;
        }

        this.isConnecting = true;
        this.showConnectionStatus('Conectando...');

        // Check if WebSocket backend is available
        // For now, use mock mode since backend is not implemented
        console.log('⚠️ WebSocket backend not available, using mock mode');

        // Simulate connection success
        setTimeout(() => {
            this.isConnected = true;
            this.isConnecting = false;
            this.reconnectCount = 0;
            this.hideConnectionStatus();
            console.log('✅ Mock chat mode activated');
        }, 500);

        /* Original WebSocket code - will be used when backend is ready
        try {
            this.ws = new WebSocket(this.websocketUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.isConnecting = false;
                this.reconnectCount = 0;
                this.hideConnectionStatus();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showConnectionStatus('Erro de conexão');
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.isConnecting = false;
                this.ws = null;

                // Try to reconnect
                if (this.isOpen && this.reconnectCount < this.options.reconnectAttempts) {
                    this.reconnect();
                }
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.isConnecting = false;
            this.showConnectionStatus('Falha na conexão');
        }
        */
    }

    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.isConnecting = false;
    }

    /**
     * Reconnect to WebSocket
     */
    reconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }

        this.reconnectCount++;
        const delay = this.options.reconnectDelay * this.reconnectCount;

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectCount}/${this.options.reconnectAttempts})`);
        this.showConnectionStatus(`Reconectando em ${Math.ceil(delay / 1000)}s...`);

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Handle incoming WebSocket message
     * @param {Object} data - Message data
     */
    handleWebSocketMessage(data) {
        console.log('WebSocket message received:', data);

        if (data.type === 'assistant_message') {
            this.receiveMessage({
                sender_type: 'assistant',
                content: data.content,
                created_at: data.timestamp || new Date().toISOString()
            });
        } else if (data.type === 'typing') {
            if (data.is_typing) {
                this.showTypingIndicator();
            } else {
                this.hideTypingIndicator();
            }
        } else if (data.type === 'error') {
            this.showError(data.message || 'Ocorreu um erro');
        }
    }

    /**
     * Receive a message
     * @param {Object} message - Message object
     */
    receiveMessage(message) {
        console.log('Message received:', message);

        // Hide typing indicator
        this.hideTypingIndicator();

        // Add message to UI
        this.addMessage(message);

        // Dispatch event for unread count
        if (message.sender_type === 'assistant' && !this.isOpen) {
            const event = new CustomEvent('chat:message-received', {
                detail: {
                    fromAssistant: true
                }
            });
            document.dispatchEvent(event);
        }
    }

    /**
     * Add a message to the chat
     * @param {Object} message - Message object
     */
    addMessage(message) {
        if (!this.messagesContainer) {
            return;
        }

        // Add to history
        this.messageHistory.push(message);

        // Limit history size
        if (this.messageHistory.length > this.options.maxHistoryMessages) {
            this.messageHistory.shift();
        }

        // Create message element
        const messageEl = this.createMessageElement(message);

        // Remove welcome message if this is the first real message
        if (this.messageHistory.length === 1) {
            const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.remove();
            }
        }

        // Add to container
        this.messagesContainer.appendChild(messageEl);

        // Scroll to bottom
        this.scrollToBottom();

        // Save history
        this.saveHistory();
    }

    /**
     * Create a message element using the Message class
     * @param {Object} message - Message object
     * @returns {HTMLElement} Message element
     */
    createMessageElement(message) {
        // Use Message class if available, otherwise fallback to basic rendering
        if (typeof Message !== 'undefined') {
            const messageObj = new Message(message);
            return messageObj.render();
        } else {
            // Fallback to basic rendering
            return this.createBasicMessageElement(message);
        }
    }

    /**
     * Create a basic message element (fallback)
     * @param {Object} message - Message object
     * @returns {HTMLElement} Message element
     */
    createBasicMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.sender_type}-message`;

        // Avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';

        if (message.sender_type === 'assistant') {
            avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
        } else if (message.sender_type === 'user') {
            avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
        } else {
            avatarDiv.innerHTML = '<i class="fas fa-info-circle"></i>';
        }

        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.innerHTML = this.formatMessageContent(message.content);

        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = this.formatTime(message.created_at);

        contentDiv.appendChild(bubbleDiv);
        contentDiv.appendChild(timeSpan);

        // Assemble message
        if (message.sender_type === 'system') {
            messageDiv.appendChild(contentDiv);
        } else {
            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(contentDiv);
        }

        return messageDiv;
    }

    /**
     * Format message content (basic fallback)
     * @param {string} content - Message content
     * @returns {string} Formatted HTML
     */
    formatMessageContent(content) {
        // Escape HTML
        const div = document.createElement('div');
        div.textContent = content;
        let formatted = div.innerHTML;

        // Convert line breaks to <br>
        formatted = formatted.replace(/\n/g, '<br>');

        // Convert URLs to links
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        return formatted;
    }

    /**
     * Format timestamp
     * @param {string} timestamp - ISO timestamp
     * @returns {string} Formatted time
     */
    formatTime(timestamp) {
        if (!timestamp) {
            return 'Agora';
        }

        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        // Less than 1 minute
        if (diff < 60000) {
            return 'Agora';
        }

        // Less than 1 hour
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}min atrÃ¡s`;
        }

        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h atrÃ¡s`;
        }

        // Format as time
        return date.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Display typing indicator
     */
    displayTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
            this.scrollToBottom();
        }
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    /**
     * Load message history
     */
    loadHistory() {
        // This will be implemented when backend is ready
        // For now, load from localStorage
        try {
            const savedHistory = localStorage.getItem('chatHistory');
            if (savedHistory) {
                this.messageHistory = JSON.parse(savedHistory);

                // Clear current messages (except welcome)
                if (this.messagesContainer) {
                    const messages = this.messagesContainer.querySelectorAll('.chat-message:not(.welcome-message)');
                    messages.forEach(msg => msg.remove());

                    // Re-render history
                    this.messageHistory.forEach(message => {
                        const messageEl = this.createMessageElement(message);
                        this.messagesContainer.appendChild(messageEl);
                    });

                    this.scrollToBottom();
                }
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    /**
     * Clear message history
     */
    clearHistory() {
        this.messageHistory = [];
        localStorage.removeItem('chatHistory');

        if (this.messagesContainer) {
            // Remove all messages except welcome
            const messages = this.messagesContainer.querySelectorAll('.chat-message:not(.welcome-message)');
            messages.forEach(msg => msg.remove());
        }

        console.log('Chat history cleared');
    }

    /**
     * Handle send message button click
     */
    handleSendMessage() {
        if (!this.input) {
            return;
        }

        const text = this.input.value.trim();
        if (text) {
            this.sendMessage(text);
        }
    }

    /**
     * Auto-resize input textarea
     */
    autoResizeInput() {
        if (!this.input) {
            return;
        }

        // Reset height to auto to get correct scrollHeight
        this.input.style.height = 'auto';

        // Set new height based on content
        const newHeight = Math.min(this.input.scrollHeight, 120);
        this.input.style.height = newHeight + 'px';
    }

    /**
     * Update character count
     */
    updateCharCount() {
        const currentEl = document.getElementById('chat-char-current');
        if (currentEl && this.input) {
            currentEl.textContent = this.input.value.length;
        }
    }

    /**
     * Scroll messages to bottom
     */
    scrollToBottom() {
        if (this.messagesContainer) {
            setTimeout(() => {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }, 100);
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Adjust window for mobile
        if (window.innerWidth <= 768 && this.isOpen) {
            this.scrollToBottom();
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // Add system message
        this.addMessage({
            sender_type: 'system',
            content: message,
            created_at: new Date().toISOString()
        });
    }

    /**
     * Save state to localStorage
     */
    saveState() {
        try {
            const state = {
                isOpen: this.isOpen,
                isMinimized: this.isMinimized,
                sessionId: this.sessionId
            };
            localStorage.setItem('chatWindowState', JSON.stringify(state));
        } catch (error) {
            console.error('Error saving chat window state:', error);
        }
    }

    /**
     * Load state from localStorage
     */
    loadSession() {
        try {
            const savedState = localStorage.getItem('chatWindowState');
            if (savedState) {
                const state = JSON.parse(savedState);
                this.sessionId = state.sessionId;

                // Don't auto-open on page load
                // User must click to open
            }
        } catch (error) {
            console.error('Error loading chat window state:', error);
        }
    }

    /**
     * Save session to localStorage
     */
    saveSession() {
        try {
            const state = {
                sessionId: this.sessionId
            };
            localStorage.setItem('chatWindowState', JSON.stringify(state));
        } catch (error) {
            console.error('Error saving session:', error);
        }
    }

    /**
     * Save history to localStorage
     */
    saveHistory() {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(this.messageHistory));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    /**
     * Show satisfaction rating prompt
     */
    showRatingPrompt() {
        if (this.ratingSubmitted || !this.ratingContainer) {
            return;
        }

        // Show rating container
        this.ratingContainer.style.display = 'block';

        // Reset rating state
        this.selectedRating = 0;
        this.updateRatingStars(0);

        // Disable submit button
        if (this.ratingSubmitBtn) {
            this.ratingSubmitBtn.disabled = true;
        }

        console.log('Rating prompt shown');
    }

    /**
     * Hide satisfaction rating prompt
     */
    hideRatingPrompt() {
        if (this.ratingContainer) {
            this.ratingContainer.style.display = 'none';
        }
    }

    /**
     * Handle rating star selection
     * @param {number} rating - Rating value (1-5)
     */
    handleRatingSelect(rating) {
        this.selectedRating = rating;
        this.updateRatingStars(rating);

        // Enable submit button
        if (this.ratingSubmitBtn) {
            this.ratingSubmitBtn.disabled = false;
        }

        // Update aria-checked attributes
        if (this.ratingStars) {
            this.ratingStars.forEach(star => {
                const starRating = parseInt(star.dataset.rating);
                star.setAttribute('aria-checked', starRating <= rating ? 'true' : 'false');
            });
        }

        console.log('Rating selected:', rating);
    }

    /**
     * Handle rating star hover
     * @param {number} rating - Rating value (1-5)
     */
    handleRatingHover(rating) {
        this.updateRatingStars(rating);
    }

    /**
     * Update rating stars visual state
     * @param {number} rating - Rating value (1-5)
     */
    updateRatingStars(rating) {
        if (!this.ratingStars) {
            return;
        }

        this.ratingStars.forEach(star => {
            const starRating = parseInt(star.dataset.rating);
            if (starRating <= rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    /**
     * Submit satisfaction rating
     */
    submitRating() {
        if (this.selectedRating === 0) {
            return;
        }

        console.log('Submitting rating:', this.selectedRating);

        // Send rating via WebSocket
        if (this.isConnected && this.ws) {
            try {
                const ratingMessage = {
                    type: 'satisfaction_rating',
                    rating: this.selectedRating,
                    session_id: this.sessionId,
                    timestamp: new Date().toISOString()
                };

                this.ws.send(JSON.stringify(ratingMessage));
                console.log('Rating sent via WebSocket');
            } catch (error) {
                console.error('Error sending rating via WebSocket:', error);
            }
        }

        // Also send via HTTP as fallback
        this.sendRatingHttp(this.selectedRating);

        // Mark as submitted
        this.ratingSubmitted = true;

        // Show thank you message
        this.showRatingThankYou();

        // Hide rating prompt and close window after delay
        setTimeout(() => {
            this.hideRatingPrompt();

            // Now actually close the window
            this.isOpen = false;

            // Close with animation
            this.window.classList.add('closing');
            this.window.classList.remove('opening');

            setTimeout(() => {
                this.window.style.display = 'none';
                this.window.classList.remove('closing');
            }, 300);

            // Dispatch event
            const event = new CustomEvent('chat:closed');
            document.dispatchEvent(event);

            // Save state
            this.saveState();
        }, 3000);
    }

    /**
     * Send rating via HTTP
     * @param {number} rating - Rating value (1-5)
     */
    sendRatingHttp(rating) {
        // Get CSRF token
        const csrfToken = this.getCsrfToken();

        // Send rating
        fetch('/chat/rating/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    rating: rating,
                    session_id: this.sessionId
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Rating saved:', data);
            })
            .catch(error => {
                console.error('Error saving rating:', error);
            });
    }

    /**
     * Skip satisfaction rating
     */
    skipRating() {
        console.log('Rating skipped');

        // Mark as submitted to prevent showing again
        this.ratingSubmitted = true;

        // Hide rating prompt
        this.hideRatingPrompt();

        // Now actually close the window
        this.isOpen = false;

        // Close with animation
        this.window.classList.add('closing');
        this.window.classList.remove('opening');

        setTimeout(() => {
            this.window.style.display = 'none';
            this.window.classList.remove('closing');
        }, 300);

        // Dispatch event
        const event = new CustomEvent('chat:closed');
        document.dispatchEvent(event);

        // Save state
        this.saveState();
    }

    /**
     * Show thank you message after rating
     */
    showRatingThankYou() {
        if (!this.ratingContainer) {
            return;
        }

        // Replace content with thank you message
        this.ratingContainer.innerHTML = `
            <div class="rating-thank-you">
                <div class="rating-thank-you-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h4 class="rating-thank-you-title">Obrigado pelo feedback!</h4>
                <p class="rating-thank-you-message">Sua avaliaÃ§Ã£o nos ajuda a melhorar continuamente.</p>
            </div>
        `;
    }

    /**
     * Get CSRF token from cookie
     * @returns {string} CSRF token
     */
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }

        return cookieValue || '';
    }

    /**
     * Destroy the chat window and clean up
     */
    destroy() {
        // Disconnect WebSocket
        this.disconnect();

        // Remove event listeners
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSendMessage);
        }

        if (this.closeButton) {
            this.closeButton.removeEventListener('click', this.close);
        }

        if (this.minimizeButton) {
            this.minimizeButton.removeEventListener('click', this.minimize);
        }

        // Clear references
        this.window = null;
        this.messagesContainer = null;
        this.input = null;
        this.form = null;
        this.sendButton = null;
        this.closeButton = null;
        this.minimizeButton = null;
        this.typingIndicator = null;
        this.connectionStatus = null;
        this.ratingContainer = null;
        this.ratingStars = null;
        this.ratingSubmitBtn = null;
        this.ratingSkipBtn = null;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWindow;
}

// Initialize chat window when DOM is ready
let chatWindow = null;

document.addEventListener('DOMContentLoaded', function() {
    // Get WebSocket URL from data attribute or construct it
    const wsUrl = document.body.dataset.chatWebsocketUrl || null;

    chatWindow = new ChatWindow(wsUrl, {
        reconnectAttempts: 5,
        reconnectDelay: 1000,
        maxHistoryMessages: 50
    });

    // Make it globally accessible for debugging and integration
    window.chatWindow = chatWindow;

    // Connect chat widget to chat window
    document.addEventListener('chat:open-requested', function() {
        if (chatWindow) {
            chatWindow.open();
        }
    });

    // Listen for widget toggle
    document.addEventListener('chat:widget-toggle', function() {
        if (chatWindow) {
            chatWindow.toggle();
        }
    });

    console.log('Chat window ready and connected to widget');
});