/**
 * WebSocket Client for Real-time Notifications
 * 
 * Handles WebSocket connection, heartbeat, auto-reconnection, and notification handling.
 * 
 * Requirements: 8.2, 8.3, 8.5
 */

class NotificationWebSocket {
    constructor(options = {}) {
        this.url = options.url || this.getWebSocketURL();
        this.heartbeatInterval = options.heartbeatInterval || 30000; // 30 seconds
        this.reconnectDelay = options.reconnectDelay || 3000; // 3 seconds
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        this.reconnectAttempts = 0;
        this.socket = null;
        this.heartbeatTimer = null;
        this.reconnectTimer = null;
        this.isIntentionallyClosed = false;

        // Callbacks
        this.onNotification = options.onNotification || this.defaultNotificationHandler;
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onError = options.onError || ((error) => console.error('WebSocket error:', error));
    }

    /**
     * Get the WebSocket URL based on current page protocol and host
     */
    getWebSocketURL() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//st}/ws/notifications/`;
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return;
        }

        this.isIntentionallyClosed = false;

        try {
            console.log('Connecting to WebSocket:', this.url);
            this.socket = new WebSocket(this.url);

            this.socket.onopen = (event) => this.handleOpen(event);
            this.socket.onmessage = (event) => this.handleMessage(event);
            this.socket.onclose = (event) => this.handleClose(event);
            this.socket.onerror = (event) => this.handleError(event);
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket connection open
     */
    handleOpen(event) {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.onConnect(event);
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);

            switch (data.type) {
                case 'connection_established':
                    console.log('Connection established:', data.message);
                    break;

                case 'notification':
                    this.onNotification(data.notification);
                    break;

                case 'pong':
                    // Heartbeat response received
                    console.log('Heartbeat pong received');
                    break;

                case 'unread_count':
                    this.updateUnreadCount(data.count);
                    break;

                case 'mark_read_response':
                    console.log('Mark read response:', data);
                    break;

                case 'error':
                    console.error('WebSocket error message:', data.message);
                    break;

                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket connection close
     */
    handleClose(event) {
        console.log('WebSocket closed:', event.code, event.reason);
        this.stopHeartbeat();
        this.onDisconnect(event);

        // Attempt to reconnect unless intentionally closed
        if (!this.isIntentionallyClosed) {
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket errors
     */
    handleError(event) {
        console.error('WebSocket error:', event);
        this.onError(event);
    }

    /**
     * Start sending heartbeat messages every 30 seconds
     * Requirement: 8.5 - Send heartbeat every 30 seconds
     */
    startHeartbeat() {
        this.stopHeartbeat(); // Clear any existing timer

        this.heartbeatTimer = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.send({
                    type: 'ping',
                    timestamp: new Date().toISOString()
                });
            }
        }, this.heartbeatInterval);
    }

    /**
     * Stop sending heartbeat messages
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Schedule a reconnection attempt
     * Requirement: 8.3 - Automatic reconnection
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.min(this.reconnectAttempts, 5); // Exponential backoff

        console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);

        this.reconnectTimer = setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.connect();
        }, delay);
    }

    /**
     * Send a message to the WebSocket server
     */
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.error('WebSocket is not connected');
        }
    }

    /**
     * Mark a notification as read
     */
    markAsRead(notificationId) {
        this.send({
            type: 'mark_read',
            notification_id: notificationId
        });
    }

    /**
     * Request unread notification count
     */
    getUnreadCount() {
        this.send({
            type: 'get_unread_count'
        });
    }

    /**
     * Close the WebSocket connection
     */
    close() {
        this.isIntentionallyClosed = true;
        this.stopHeartbeat();

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    /**
     * Default notification handler
     */
    defaultNotificationHandler(notification) {
        console.log('New notification:', notification);

        // Show browser notification if permitted
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/static/favicon.ico',
                tag: `notification-${notification.id}`
            });
        }

        // Update UI
        this.updateNotificationUI(notification);
    }

    /**
     * Update notification UI
     */
    updateNotificationUI(notification) {
        // Update notification badge
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
            badge.style.display = 'inline-block';
        }

        // Add notification to dropdown if it exists
        const notificationList = document.querySelector('.notification-list');
        if (notificationList) {
            const notificationHTML = this.createNotificationHTML(notification);
            notificationList.insertAdjacentHTML('afterbegin', notificationHTML);
        }

        // Show toast notification
        this.showToast(notification);
    }

    /**
     * Create HTML for a notification item
     */
    createNotificationHTML(notification) {
        const timeAgo = this.getTimeAgo(new Date(notification.created_at));
        return `
            <div class="notification-item" data-notification-id="${notification.id}">
                <div class="notification-content">
                    <h4>${notification.title}</h4>
                    <p>${notification.message}</p>
                    <span class="notification-time">${timeAgo}</span>
                </div>
            </div>
        `;
    }

    /**
     * Show a toast notification
     */
    showToast(notification) {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = `
            <strong>${notification.title}</strong>
            <p>${notification.message}</p>
        `;

        document.body.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    /**
     * Update unread count in UI
     */
    updateUnreadCount(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    /**
     * Get time ago string
     */
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);

        if (seconds < 60) return 'agora mesmo';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} minutos atrás`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)} horas atrás`;
        return `${Math.floor(seconds / 86400)} dias atrás`;
    }

    /**
     * Request browser notification permission
     */
    static requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                console.log('Notification permission:', permission);
            });
        }
    }
}

// Auto-initialize WebSocket connection when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated (you can customize this check)
    const isAuthenticated = document.body.dataset.authenticated === 'true';

    if (isAuthenticated) {
        // Request notification permission
        NotificationWebSocket.requestNotificationPermission();

        // Initialize WebSocket connection
        window.notificationWS = new NotificationWebSocket({
            onNotification: (notification) => {
                console.log('Received notification:', notification);
                // Custom notification handler can be added here
            },
            onConnect: () => {
                console.log('Connected to notification service');
                // Request initial unread count
                if (window.notificationWS) {
                    window.notificationWS.getUnreadCount();
                }
            },
            onDisconnect: () => {
                console.log('Disconnected from notification service');
            }
        });

        window.notificationWS.connect();
    }
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (window.notificationWS) {
        window.notificationWS.close();
    }
});
$ {