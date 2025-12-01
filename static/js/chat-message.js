/**
 * Message - Handles individual message rendering with markdown support
 * 
 * This class creates and formats chat messages with markdown parsing,
 * link rendering, and click tracking.
 */

class Message {
    constructor(data) {
        this.data = {
            sender_type: data.sender_type || 'user',
            content: data.content || '',
            created_at: data.created_at || new Date().toISOString(),
            metadata: data.metadata || {}
        };

        this.element = null;
    }

    /**
     * Render the message as a DOM element
     * @returns {HTMLElement} Message element
     */
    render() {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${this.data.sender_type}-message`;
        messageDiv.dataset.messageId = this.data.metadata.message_id || '';

        // Create avatar
        const avatarDiv = this.createAvatar();

        // Create content
        const contentDiv = this.createContent();

        // Assemble message
        if (this.data.sender_type === 'system') {
            messageDiv.appendChild(contentDiv);
        } else {
            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(contentDiv);
        }

        this.element = messageDiv;
        return messageDiv;
    }

    /**
     * Create avatar element
     * @returns {HTMLElement} Avatar element
     */
    createAvatar() {
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';

        let icon = 'fa-info-circle';
        if (this.data.sender_type === 'assistant') {
            icon = 'fa-robot';
        } else if (this.data.sender_type === 'user') {
            icon = 'fa-user';
        }

        avatarDiv.innerHTML = `<i class="fas ${icon}"></i>`;
        return avatarDiv;
    }

    /**
     * Create content element
     * @returns {HTMLElement} Content element
     */
    createContent() {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Create bubble with formatted content
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        // Render markdown for assistant messages, plain text for others
        if (this.data.sender_type === 'assistant') {
            bubbleDiv.innerHTML = this.renderMarkdown(this.data.content);
        } else {
            bubbleDiv.innerHTML = this.escapeAndFormat(this.data.content);
        }

        // Add click tracking to links
        this.addLinkTracking(bubbleDiv);

        // Create timestamp
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = this.formatTimestamp(this.data.created_at);

        contentDiv.appendChild(bubbleDiv);
        contentDiv.appendChild(timeSpan);

        return contentDiv;
    }

    /**
     * Render markdown to HTML
     * @param {string} markdown - Markdown text
     * @returns {string} HTML string
     */
    renderMarkdown(markdown) {
        if (!markdown) {
            return '';
        }

        let html = markdown;

        // Escape HTML first
        html = this.escapeHtml(html);

        // Bold: **text** or __text__
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

        // Italic: *text* or _text_
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.+?)_/g, '<em>$1</em>');

        // Code: `code`
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');

        // Links: [text](url)
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
            return this.renderLink(url, text);
        });

        // Auto-link URLs
        html = html.replace(
            /(?<!href="|src=")(?<!">)(https?:\/\/[^\s<]+)/g,
            (url) => this.renderLink(url)
        );

        // Line breaks
        html = html.replace(/\n/g, '<br>');

        // Lists: - item or * item
        html = this.renderLists(html);

        // Numbered lists: 1. item
        html = this.renderNumberedLists(html);

        return html;
    }

    /**
     * Render lists
     * @param {string} html - HTML string
     * @returns {string} HTML with lists
     */
    renderLists(html) {
        const lines = html.split('<br>');
        let inList = false;
        let result = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();

            if (line.match(/^[-*]\s+(.+)/)) {
                const content = line.replace(/^[-*]\s+/, '');

                if (!inList) {
                    result.push('<ul>');
                    inList = true;
                }

                result.push(`<li>${content}</li>`);
            } else {
                if (inList) {
                    result.push('</ul>');
                    inList = false;
                }

                if (line) {
                    result.push(line);
                }
            }
        }

        if (inList) {
            result.push('</ul>');
        }

        return result.join('<br>').replace(/<br><ul>/g, '<ul>').replace(/<\/ul><br>/g, '</ul>');
    }

    /**
     * Render numbered lists
     * @param {string} html - HTML string
     * @returns {string} HTML with numbered lists
     */
    renderNumberedLists(html) {
        const lines = html.split('<br>');
        let inList = false;
        let result = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();

            if (line.match(/^\d+\.\s+(.+)/)) {
                const content = line.replace(/^\d+\.\s+/, '');

                if (!inList) {
                    result.push('<ol>');
                    inList = true;
                }

                result.push(`<li>${content}</li>`);
            } else {
                if (inList) {
                    result.push('</ol>');
                    inList = false;
                }

                if (line) {
                    result.push(line);
                }
            }
        }

        if (inList) {
            result.push('</ol>');
        }

        return result.join('<br>').replace(/<br><ol>/g, '<ol>').replace(/<\/ol><br>/g, '</ol>');
    }

    /**
     * Render a link
     * @param {string} url - URL
     * @param {string} text - Link text (optional)
     * @returns {string} HTML link
     */
    renderLink(url, text = null) {
        const displayText = text || url;
        const safeUrl = this.sanitizeUrl(url);

        return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" data-link-url="${safeUrl}">${displayText}</a>`;
    }

    /**
     * Add click tracking to links
     * @param {HTMLElement} container - Container element
     */
    addLinkTracking(container) {
        const links = container.querySelectorAll('a[data-link-url]');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                const url = link.dataset.linkUrl;

                // Track link click
                this.trackLinkClick(url);

                // Dispatch event
                const event = new CustomEvent('chat:link-clicked', {
                    detail: {
                        url: url,
                        text: link.textContent,
                        messageId: this.data.metadata.message_id
                    }
                });
                document.dispatchEvent(event);

                console.log('Link clicked:', url);
            });
        });
    }

    /**
     * Track link click (analytics)
     * @param {string} url - URL that was clicked
     */
    trackLinkClick(url) {
        // Send analytics event
        if (typeof fetch !== 'undefined') {
            fetch('/analytics/track-user-action/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    action_type: 'chat_link_click',
                    page_path: window.location.pathname,
                    additional_data: {
                        url: url,
                        message_id: this.data.metadata.message_id
                    }
                })
            }).catch(error => {
                console.error('Error tracking link click:', error);
            });
        }
    }

    /**
     * Escape and format plain text
     * @param {string} text - Plain text
     * @returns {string} Formatted HTML
     */
    escapeAndFormat(text) {
        let html = this.escapeHtml(text);

        // Convert line breaks
        html = html.replace(/\n/g, '<br>');

        // Auto-link URLs
        html = html.replace(
            /(https?:\/\/[^\s]+)/g,
            (url) => this.renderLink(url)
        );

        return html;
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Sanitize URL to prevent XSS
     * @param {string} url - URL to sanitize
     * @returns {string} Sanitized URL
     */
    sanitizeUrl(url) {
        // Only allow http, https, and mailto protocols
        const allowedProtocols = ['http:', 'https:', 'mailto:'];

        try {
            const urlObj = new URL(url, window.location.origin);
            if (allowedProtocols.includes(urlObj.protocol)) {
                return urlObj.href;
            }
        } catch (e) {
            // Invalid URL
        }

        return '#';
    }

    /**
     * Format timestamp
     * @param {string} timestamp - ISO timestamp
     * @returns {string} Formatted time
     */
    formatTimestamp(timestamp) {
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
            return `${minutes}min atrás`;
        }

        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h atrás`;
        }

        // Format as time
        return date.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
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
     * Update message content
     * @param {string} content - New content
     */
    updateContent(content) {
        this.data.content = content;

        if (this.element) {
            const bubble = this.element.querySelector('.message-bubble');
            if (bubble) {
                if (this.data.sender_type === 'assistant') {
                    bubble.innerHTML = this.renderMarkdown(content);
                } else {
                    bubble.innerHTML = this.escapeAndFormat(content);
                }

                this.addLinkTracking(bubble);
            }
        }
    }

    /**
     * Get the DOM element
     * @returns {HTMLElement} Message element
     */
    getElement() {
        if (!this.element) {
            this.render();
        }
        return this.element;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Message;
}