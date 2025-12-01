"""
Security utilities for Chat IA Assistente (Sophie)

This module provides security functions for input validation, sanitization,
and security checks for the chat system.

Requirements: 8.3 (Security)
"""

import re
import html
import json
import logging
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ChatSecurityValidator:
    """
    Security validator for chat messages and inputs.
    
    Provides validation and sanitization for user inputs to prevent
    security vulnerabilities like XSS, injection attacks, and abuse.
    
    Requirements: 8.3
    """
    
    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers (onclick, onload, etc.)
        r'<iframe[^>]*>',  # Iframes
        r'<object[^>]*>',  # Object tags
        r'<embed[^>]*>',  # Embed tags
    ]
    
    # Allowed message types
    ALLOWED_MESSAGE_TYPES = ['text', 'system']
    
    # Maximum lengths
    MAX_MESSAGE_LENGTH = 2000
    MIN_MESSAGE_LENGTH = 1
    MAX_FEEDBACK_LENGTH = 1000
    
    @classmethod
    def validate_message_content(cls, content):
        """
        Validate message content for security and format.
        
        Args:
            content: Message content string
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
            
        Requirements: 8.3
        """
        if not content:
            return False, "Mensagem vazia"
        
        # Check if content is a string
        if not isinstance(content, str):
            return False, "Conteúdo da mensagem deve ser texto"
        
        # Strip whitespace for length check
        content_stripped = content.strip()
        
        # Check minimum length
        if len(content_stripped) < cls.MIN_MESSAGE_LENGTH:
            return False, f"Mensagem muito curta. Mínimo: {cls.MIN_MESSAGE_LENGTH} caractere"
        
        # Check maximum length
        max_length = settings.CHAT_CONFIG.get('MAX_MESSAGE_LENGTH', cls.MAX_MESSAGE_LENGTH)
        if len(content) > max_length:
            return False, f"Mensagem muito longa. Máximo: {max_length} caracteres"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(
                    f"Dangerous pattern detected in message",
                    extra={'pattern': pattern, 'content_preview': content[:50]}
                )
                return False, "Conteúdo da mensagem contém padrões não permitidos"
        
        return True, None
    
    @classmethod
    def sanitize_message_content(cls, content):
        """
        Sanitize message content to prevent XSS attacks.
        
        Args:
            content: Message content string
            
        Returns:
            str: Sanitized content
            
        Requirements: 8.3
        """
        if not content:
            return ""
        
        # HTML escape to prevent XSS
        sanitized = html.escape(content)
        
        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    @classmethod
    def validate_message_type(cls, message_type):
        """
        Validate message type.
        
        Args:
            message_type: Type of message
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
            
        Requirements: 8.3
        """
        allowed_types = settings.CHAT_CONFIG.get(
            'ALLOWED_MESSAGE_TYPES',
            cls.ALLOWED_MESSAGE_TYPES
        )
        
        if message_type not in allowed_types:
            return False, f"Tipo de mensagem não permitido: {message_type}"
        
        return True, None
    
    @classmethod
    def validate_session_id(cls, session_id):
        """
        Validate session ID format.
        
        Args:
            session_id: Session ID string
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
            
        Requirements: 8.3
        """
        if not session_id:
            return False, "ID de sessão vazio"
        
        # Check if it's a valid UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, str(session_id), re.IGNORECASE):
            return False, "Formato de ID de sessão inválido"
        
        return True, None
    
    @classmethod
    def validate_rating(cls, rating):
        """
        Validate satisfaction rating value.
        
        Args:
            rating: Rating value
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None, normalized_rating: int or None)
            
        Requirements: 8.3
        """
        if rating is None:
            return False, "Avaliação não fornecida", None
        
        # Check if it's a float (not allowed, must be integer)
        if isinstance(rating, float) and not rating.is_integer():
            return False, "Avaliação deve ser um número inteiro", None
        
        # Try to convert to integer
        try:
            rating_int = int(rating)
        except (ValueError, TypeError):
            return False, "Avaliação deve ser um número", None
        
        # Check range (1-5)
        if rating_int < 1 or rating_int > 5:
            return False, "Avaliação deve ser entre 1 e 5", None
        
        return True, None, rating_int
    
    @classmethod
    def validate_feedback(cls, feedback):
        """
        Validate feedback text.
        
        Args:
            feedback: Feedback text
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
            
        Requirements: 8.3
        """
        if not feedback:
            # Empty feedback is allowed
            return True, None
        
        # Check if feedback is a string
        if not isinstance(feedback, str):
            return False, "Feedback deve ser texto"
        
        # Check maximum length
        if len(feedback) > cls.MAX_FEEDBACK_LENGTH:
            return False, f"Feedback muito longo. Máximo: {cls.MAX_FEEDBACK_LENGTH} caracteres"
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, feedback, re.IGNORECASE):
                logger.warning(
                    f"Dangerous pattern detected in feedback",
                    extra={'pattern': pattern}
                )
                return False, "Feedback contém padrões não permitidos"
        
        return True, None
    
    @classmethod
    def sanitize_feedback(cls, feedback):
        """
        Sanitize feedback text.
        
        Args:
            feedback: Feedback text
            
        Returns:
            str: Sanitized feedback
            
        Requirements: 8.3
        """
        if not feedback:
            return ""
        
        # HTML escape to prevent XSS
        sanitized = html.escape(feedback)
        
        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    @classmethod
    def validate_context_data(cls, context_data):
        """
        Validate context data structure.
        
        Args:
            context_data: Context data dictionary
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
            
        Requirements: 8.3
        """
        if context_data is None:
            # None is allowed, will be converted to empty dict
            return True, None
        
        # Check if it's a dictionary
        if not isinstance(context_data, dict):
            return False, "Dados de contexto devem ser um objeto"
        
        # Check size (prevent DoS via large context)
        max_context_size = settings.CHAT_CONFIG.get('MAX_CONTEXT_SIZE_BYTES', 10000)
        try:
            context_json = json.dumps(context_data)
            if len(context_json) > max_context_size:
                return False, f"Dados de contexto muito grandes. Máximo: {max_context_size} bytes"
        except (TypeError, ValueError) as e:
            return False, f"Dados de contexto inválidos: {str(e)}"
        
        # Validate context keys (prevent injection via keys)
        for key in context_data.keys():
            if not isinstance(key, str):
                return False, "Chaves de contexto devem ser strings"
            
            # Check for dangerous characters in keys
            if not re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
                return False, f"Chave de contexto inválida: {key}"
        
        return True, None
    
    @classmethod
    def validate_json_message(cls, text_data):
        """
        Validate JSON message format.
        
        Args:
            text_data: Raw text data from WebSocket
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None, parsed_data: dict or None)
            
        Requirements: 8.3
        """
        if not text_data:
            return False, "Mensagem vazia", None
        
        # Check if it's a string
        if not isinstance(text_data, str):
            return False, "Mensagem deve ser texto", None
        
        # Try to parse JSON
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {str(e)}", None
        
        # Check if it's a dictionary
        if not isinstance(data, dict):
            return False, "Mensagem deve ser um objeto JSON", None
        
        # Validate required fields
        if 'type' not in data:
            return False, "Campo 'type' obrigatório", None
        
        return True, None, data
    
    @classmethod
    def validate_websocket_frame_size(cls, data, max_size=None):
        """
        Validate WebSocket frame size.
        
        Args:
            data: Data to validate (string or bytes)
            max_size: Maximum size in bytes (optional)
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
            
        Requirements: 8.3
        """
        if max_size is None:
            ws_security = getattr(settings, 'WEBSOCKET_SECURITY', {})
            max_size = ws_security.get('MAX_FRAME_SIZE', 65536)
        
        # Calculate size in bytes
        if isinstance(data, str):
            size = len(data.encode('utf-8'))
        elif isinstance(data, bytes):
            size = len(data)
        else:
            return False, "Tipo de dados inválido"
        
        if size > max_size:
            return False, f"Frame muito grande. Máximo: {max_size} bytes"
        
        return True, None
    
    @classmethod
    def sanitize_context_data(cls, context_data):
        """
        Sanitize context data to prevent injection attacks.
        
        Args:
            context_data: Context data dictionary
            
        Returns:
            dict: Sanitized context data
            
        Requirements: 8.3
        """
        if not context_data or not isinstance(context_data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in context_data.items():
            # Sanitize key
            if isinstance(key, str) and re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
                # Sanitize value based on type
                if isinstance(value, str):
                    sanitized[key] = html.escape(value)
                elif isinstance(value, (int, float, bool)):
                    sanitized[key] = value
                elif isinstance(value, (list, dict)):
                    # Recursively sanitize nested structures
                    try:
                        sanitized[key] = cls._sanitize_nested(value)
                    except Exception as e:
                        logger.warning(f"Error sanitizing nested value: {e}")
                        continue
        
        return sanitized
    
    @classmethod
    def _sanitize_nested(cls, value, depth=0, max_depth=5):
        """
        Recursively sanitize nested data structures.
        
        Args:
            value: Value to sanitize
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            Sanitized value
        """
        # Prevent deep recursion
        if depth >= max_depth:
            return None
        
        if isinstance(value, str):
            return html.escape(value)
        elif isinstance(value, (int, float, bool)):
            return value
        elif isinstance(value, list):
            return [cls._sanitize_nested(item, depth + 1, max_depth) for item in value]
        elif isinstance(value, dict):
            return {
                k: cls._sanitize_nested(v, depth + 1, max_depth)
                for k, v in value.items()
                if isinstance(k, str)
            }
        else:
            return None
    
    @classmethod
    def check_origin(cls, origin, allowed_origins):
        """
        Check if the origin is allowed for WebSocket connections.
        
        Args:
            origin: Origin header from WebSocket request
            allowed_origins: List of allowed origins
            
        Returns:
            bool: True if origin is allowed, False otherwise
            
        Requirements: 8.3
        """
        if not origin:
            logger.warning("WebSocket connection attempt without origin header")
            return False
        
        # Check if origin is in allowed list
        if origin in allowed_origins:
            return True
        
        # Check for wildcard patterns
        for allowed in allowed_origins:
            if allowed == '*':
                # Allow all origins (not recommended for production)
                logger.warning("Wildcard origin allowed - not recommended for production")
                return True
            
            # Check for pattern matching (e.g., *.example.com)
            if allowed.startswith('*.'):
                domain = allowed[2:]
                # Extract domain from origin (remove protocol and port)
                # Example: http://sub.example.com:8000 -> sub.example.com
                origin_domain = origin.split('://')[1] if '://' in origin else origin
                origin_domain = origin_domain.split(':')[0]  # Remove port if present
                
                # Check if origin domain ends with the allowed domain
                # and has a subdomain (not just the domain itself)
                if origin_domain.endswith('.' + domain) or origin_domain.endswith(domain):
                    # Ensure it's actually a subdomain, not just the domain
                    if origin_domain != domain and origin_domain.endswith('.' + domain):
                        return True
        
        logger.warning(
            f"WebSocket connection from unauthorized origin",
            extra={'origin': origin, 'allowed_origins': allowed_origins}
        )
        return False


class ConnectionTracker:
    """
    Track active WebSocket connections for rate limiting.
    
    Requirements: 8.3
    """
    
    @staticmethod
    def get_user_connection_key(user_id):
        """Get cache key for user connection count"""
        return f'ws_connections_user_{user_id}'
    
    @staticmethod
    def get_ip_connection_key(ip_address):
        """Get cache key for IP connection count"""
        return f'ws_connections_ip_{ip_address}'
    
    @staticmethod
    def increment_connection(user_id=None, ip_address=None):
        """
        Increment connection count for user or IP.
        
        Args:
            user_id: User ID (optional)
            ip_address: IP address (optional)
            
        Returns:
            tuple: (user_count, ip_count)
        """
        user_count = 0
        ip_count = 0
        
        if user_id:
            key = ConnectionTracker.get_user_connection_key(user_id)
            user_count = cache.get(key, 0) + 1
            cache.set(key, user_count, timeout=3600)  # 1 hour
        
        if ip_address:
            key = ConnectionTracker.get_ip_connection_key(ip_address)
            ip_count = cache.get(key, 0) + 1
            cache.set(key, ip_count, timeout=3600)  # 1 hour
        
        return user_count, ip_count
    
    @staticmethod
    def decrement_connection(user_id=None, ip_address=None):
        """
        Decrement connection count for user or IP.
        
        Args:
            user_id: User ID (optional)
            ip_address: IP address (optional)
        """
        if user_id:
            key = ConnectionTracker.get_user_connection_key(user_id)
            count = cache.get(key, 0)
            if count > 0:
                cache.set(key, count - 1, timeout=3600)
        
        if ip_address:
            key = ConnectionTracker.get_ip_connection_key(ip_address)
            count = cache.get(key, 0)
            if count > 0:
                cache.set(key, count - 1, timeout=3600)
    
    @staticmethod
    def check_connection_limit(user_id=None, ip_address=None):
        """
        Check if connection limits are exceeded.
        
        Args:
            user_id: User ID (optional)
            ip_address: IP address (optional)
            
        Returns:
            tuple: (is_allowed: bool, reason: str or None)
        """
        ws_security = getattr(settings, 'WEBSOCKET_SECURITY', {})
        max_per_user = ws_security.get('MAX_CONNECTIONS_PER_USER', 5)
        max_per_ip = ws_security.get('MAX_CONNECTIONS_PER_IP', 10)
        
        if user_id:
            key = ConnectionTracker.get_user_connection_key(user_id)
            count = cache.get(key, 0)
            if count >= max_per_user:
                return False, f'Maximum connections per user exceeded ({max_per_user})'
        
        if ip_address:
            key = ConnectionTracker.get_ip_connection_key(ip_address)
            count = cache.get(key, 0)
            if count >= max_per_ip:
                return False, f'Maximum connections per IP exceeded ({max_per_ip})'
        
        return True, None


class WebSocketSecurityMiddleware:
    """
    Security middleware for WebSocket connections.
    
    Provides origin checking, connection validation, and rate limiting
    for WebSocket connections.
    
    Requirements: 8.3
    """
    
    def __init__(self, app):
        self.app = app
    
    def get_client_ip(self, scope):
        """
        Extract client IP address from scope.
        
        Args:
            scope: ASGI scope
            
        Returns:
            str: Client IP address
        """
        # Check for X-Forwarded-For header (proxy/load balancer)
        for header_name, header_value in scope.get('headers', []):
            if header_name == b'x-forwarded-for':
                # Get first IP in the chain
                ip = header_value.decode('utf-8').split(',')[0].strip()
                return ip
        
        # Fall back to client address from scope
        client = scope.get('client')
        if client:
            return client[0]
        
        return None
    
    async def __call__(self, scope, receive, send):
        """
        Process WebSocket connection with security checks.
        
        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        # Only apply to WebSocket connections
        if scope['type'] != 'websocket':
            return await self.app(scope, receive, send)
        
        ws_security = getattr(settings, 'WEBSOCKET_SECURITY', {})
        
        # Get origin from headers
        origin = None
        for header_name, header_value in scope.get('headers', []):
            if header_name == b'origin':
                origin = header_value.decode('utf-8')
                break
        
        # Get allowed origins from settings
        allowed_origins = getattr(settings, 'ALLOWED_WEBSOCKET_ORIGINS', [])
        
        # Check origin (Requirements: 8.3 - Configure CORS)
        if ws_security.get('ENFORCE_ORIGIN_CHECK', True):
            if not ChatSecurityValidator.check_origin(origin, allowed_origins):
                # Reject connection
                if ws_security.get('LOG_REJECTED_CONNECTIONS', True):
                    logger.warning(
                        f"Rejected WebSocket connection from unauthorized origin",
                        extra={'origin': origin, 'path': scope.get('path')}
                    )
                
                # Send close frame
                await send({
                    'type': 'websocket.close',
                    'code': 4003,  # Custom code for unauthorized origin
                })
                return
        
        # Get client IP and user
        client_ip = self.get_client_ip(scope)
        user = scope.get('user')
        user_id = user.id if user and hasattr(user, 'id') and user.is_authenticated else None
        
        # Check connection limits (Requirements: 8.3)
        if ws_security.get('TRACK_CONNECTIONS', True):
            is_allowed, reason = ConnectionTracker.check_connection_limit(
                user_id=user_id,
                ip_address=client_ip
            )
            
            if not is_allowed:
                if ws_security.get('LOG_REJECTED_CONNECTIONS', True):
                    logger.warning(
                        f"Rejected WebSocket connection: {reason}",
                        extra={
                            'user_id': user_id,
                            'ip_address': client_ip,
                            'path': scope.get('path')
                        }
                    )
                
                # Send close frame
                await send({
                    'type': 'websocket.close',
                    'code': 4008,  # Custom code for connection limit exceeded
                })
                return
            
            # Increment connection count
            ConnectionTracker.increment_connection(
                user_id=user_id,
                ip_address=client_ip
            )
        
        # Origin and limits are valid, proceed with connection
        if ws_security.get('LOG_SECURITY_EVENTS', True):
            logger.info(
                f"WebSocket connection accepted",
                extra={
                    'origin': origin,
                    'path': scope.get('path'),
                    'user_id': user_id,
                    'ip_address': client_ip
                }
            )
        
        # Wrap receive to enforce message size limits
        original_receive = receive
        
        async def receive_with_size_check():
            """Wrap receive to check message size"""
            message = await original_receive()
            
            # Check frame size (Requirements: 8.3 - Set message size limits)
            if ws_security.get('ENFORCE_MESSAGE_SIZE', True):
                if message.get('type') == 'websocket.receive':
                    text = message.get('text', '')
                    bytes_data = message.get('bytes', b'')
                    
                    max_frame_size = ws_security.get('MAX_FRAME_SIZE', 65536)
                    
                    # Check text message size
                    if text and len(text.encode('utf-8')) > max_frame_size:
                        logger.warning(
                            f"Message frame size exceeded",
                            extra={
                                'user_id': user_id,
                                'size': len(text.encode('utf-8')),
                                'max_size': max_frame_size
                            }
                        )
                        # Return disconnect message
                        return {
                            'type': 'websocket.disconnect',
                            'code': 4009,  # Custom code for message too large
                        }
                    
                    # Check binary message size
                    if bytes_data and len(bytes_data) > max_frame_size:
                        logger.warning(
                            f"Binary frame size exceeded",
                            extra={
                                'user_id': user_id,
                                'size': len(bytes_data),
                                'max_size': max_frame_size
                            }
                        )
                        return {
                            'type': 'websocket.disconnect',
                            'code': 4009,
                        }
            
            return message
        
        try:
            # Call the application with wrapped receive
            return await self.app(scope, receive_with_size_check, send)
        finally:
            # Decrement connection count on disconnect
            if ws_security.get('TRACK_CONNECTIONS', True):
                ConnectionTracker.decrement_connection(
                    user_id=user_id,
                    ip_address=client_ip
                )
