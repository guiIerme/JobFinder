/**
 * ChatWidget - Manages the floating chat button and unread message badge
 * 
 * This class handles the chat widget button that opens/closes the chat window,
 * displays unread message counts, and manages the widget's visibility and state.
 */

class ChatWidget {
    constructor(options = {}) {
        // Configuration
        this.options = {
            toggleButtonId: options.toggleButtonId || 'chat-widget-toggle',
            unreadBadgeId: options.unreadBadgeId || 'chat-unread-badge',
            onToggle: options.onToggle || null,
            ...options
        };

        // State
        this.isVisible = true;
        this.unreadCount = 0;
        this.isLoading = false;

        // DOM elements
        this.toggleButton = null;
        this.unreadBadge = null;

        // Initialize
        this.init();
    }

    /**
     * Initialize the chat widget
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
     * Setup the widget after DOM is ready
     */
    setup() {
        // Get DOM elements
        this.toggleButton = document.getElementById(this.options.toggleButtonId);
        this.unreadBadge = document.getElementById(this.options.unreadBadgeId);

        if (!this.toggleButton) {
            console.error('Chat widget toggle button not found');
            return;
        }

        // Attach event listeners
        this.attachEventListeners();

        // Load saved state from localStorage
        this.loadState();

        console.log('Chat widget initialized');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Click event on toggle button
        this.toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggle();
        });

        // Keyboard accessibility
        this.toggleButton.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggle();
            }
        });

        // Listen for custom events from chat window
        document.addEventListener('chat:opened', () => {
            this.clearUnreadCount();
        });

        document.addEventListener('chat:message-received', (e) => {
            if (e.detail && e.detail.fromAssistant) {
                this.incrementUnreadCount();
            }
        });

        document.addEventListener('chat:closed', () => {
            // Widget remains visible when chat closes
        });
    }

    /**
     * Toggle the chat widget visibility
     */
    toggle() {
        if (this.isLoading) {
            return;
        }

        // Dispatch toggle event
        const event = new CustomEvent('chat:widget-toggle', {
            detail: {
                isVisible: this.isVisible
            }
        });
        document.dispatchEvent(event);

        // Call callback if provided
        if (typeof this.options.onToggle === 'function') {
            this.options.onToggle();
        }

        // Add visual feedback
        this.addClickFeedback();
    }

    /**
     * Show the chat widget
     */
    show() {
        if (!this.toggleButton) return;

        this.isVisible = true;
        this.toggleButton.style.display = 'flex';
        this.toggleButton.setAttribute('aria-hidden', 'false');

        this.saveState();
    }

    /**
     * Hide the chat widget
     */
    hide() {
        if (!this.toggleButton) return;

        this.isVisible = false;
        this.toggleButton.style.display = 'none';
        this.toggleButton.setAttribute('aria-hidden', 'true');

        this.saveState();
    }

    /**
     * Set the unread message count
     * @param {number} count - Number of unread messages
     */
    setUnreadCount(count) {
        if (!this.unreadBadge) return;

        this.unreadCount = Math.max(0, parseInt(count) || 0);

        if (this.unreadCount > 0) {
            this.unreadBadge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            this.unreadBadge.style.display = 'flex';
            this.unreadBadge.setAttribute('aria-label', `${this.unreadCount} mensagens não lidas`);

            // Update button title
            this.toggleButton.setAttribute('title',
                `Chat com Sophie - ${this.unreadCount} mensagem${this.unreadCount > 1 ? 's' : ''} não lida${this.unreadCount > 1 ? 's' : ''}`
            );
        } else {
            this.unreadBadge.style.display = 'none';
            this.toggleButton.setAttribute('title', 'Chat com Sophie - Assistente Virtual');
        }

        this.saveState();
    }

    /**
     * Increment the unread count by 1
     */
    incrementUnreadCount() {
        this.setUnreadCount(this.unreadCount + 1);
    }

    /**
     * Clear the unread count
     */
    clearUnreadCount() {
        this.setUnreadCount(0);
    }

    /**
     * Set loading state
     * @param {boolean} loading - Whether widget is loading
     */
    setLoading(loading) {
        if (!this.toggleButton) return;

        this.isLoading = loading;

        if (loading) {
            this.toggleButton.classList.add('loading');
            this.toggleButton.setAttribute('aria-busy', 'true');
        } else {
            this.toggleButton.classList.remove('loading');
            this.toggleButton.setAttribute('aria-busy', 'false');
        }
    }

    /**
     * Update the widget position
     * Useful when other floating elements change
     */
    updatePosition() {
        // This can be extended to dynamically adjust position
        // based on other floating elements
        console.log('Widget position updated');
    }

    /**
     * Add visual click feedback
     */
    addClickFeedback() {
        if (!this.toggleButton) return;

        this.toggleButton.style.transform = 'scale(0.95)';

        setTimeout(() => {
            this.toggleButton.style.transform = '';
        }, 150);
    }

    /**
     * Save widget state to localStorage
     */
    saveState() {
        try {
            const state = {
                isVisible: this.isVisible,
                unreadCount: this.unreadCount
            };
            localStorage.setItem('chatWidgetState', JSON.stringify(state));
        } catch (error) {
            console.error('Error saving chat widget state:', error);
        }
    }

    /**
     * Load widget state from localStorage
     */
    loadState() {
        try {
            const savedState = localStorage.getItem('chatWidgetState');
            if (savedState) {
                const state = JSON.parse(savedState);

                if (state.isVisible !== undefined) {
                    this.isVisible = state.isVisible;
                    if (!this.isVisible) {
                        this.hide();
                    }
                }

                // Don't restore unread count on page load
                // It will be set by the chat system
            }
        } catch (error) {
            console.error('Error loading chat widget state:', error);
        }
    }

    /**
     * Destroy the widget and clean up
     */
    destroy() {
        if (this.toggleButton) {
            this.toggleButton.removeEventListener('click', this.toggle);
            this.toggleButton.removeEventListener('keydown', this.toggle);
        }

        document.removeEventListener('chat:opened', this.clearUnreadCount);
        document.removeEventListener('chat:message-received', this.incrementUnreadCount);
        document.removeEventListener('chat:closed', () => {});

        this.toggleButton = null;
        this.unreadBadge = null;
    }
}

// Initialize chat widget when DOM is ready
let chatWidget = null;

document.addEventListener('DOMContentLoaded', function() {
    chatWidget = new ChatWidget({
        onToggle: function() {
            // This will be connected to the chat window in task 9
            console.log('Chat widget toggled - chat window will open here');

            // For now, just show a message
            const event = new CustomEvent('chat:open-requested');
            document.dispatchEvent(event);
        }
    });

    // Make it globally accessible for debugging and integration
    window.chatWidget = chatWidget;
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWidget;
}