"""
Error Handler - Chat Error Handling and Fallbacks

This module handles errors in the chat system and provides
fallback responses when needed.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ChatErrorHandler:
    """
    Handles errors in the chat system and provides fallback responses.
    
    This class provides static methods for handling different types of errors
    that can occur in the chat system, including AI processing errors, rate
    limiting, and session errors.
    """
    
    @staticmethod
    async def handle_ai_error(error: Exception, session: Any) -> Dict[str, Any]:
        """
        Handle AI processing errors with fallback responses.
        
        When the AI service fails, this method logs the error and returns
        a user-friendly fallback response with helpful action buttons.
        
        Args:
            error: The exception that occurred during AI processing
            session: The ChatSession object where the error occurred
            
        Returns:
            Dict containing fallback response with type, message, and actions
            
        Requirements: 6.1, 6.2, 8.5
        """
        logger.error(
            f"AI Error in session {session.session_id}: {error}",
            extra={
                'session_id': str(session.session_id),
                'user_id': session.user.id if session.user else None,
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        )
        
        return {
            'type': 'fallback',
            'message': 'Desculpe, estou com dificuldades no momento. Posso ajudá-lo com:\n'
                      '- Ver serviços disponíveis\n'
                      '- Acessar meus pedidos\n'
                      '- Falar com suporte humano',
            'actions': [
                {'label': 'Ver Serviços', 'url': '/services/'},
                {'label': 'Meus Pedidos', 'url': '/meus-pedidos/'},
                {'label': 'Contato', 'url': '/contact/'}
            ],
            'error_code': 'AI_PROCESSING_ERROR'
        }
    
    @staticmethod
    async def handle_rate_limit(user: Optional[Any]) -> Dict[str, Any]:
        """
        Handle rate limit exceeded errors.
        
        When a user exceeds the rate limit, this method returns a response
        informing them to wait before sending more messages.
        
        Args:
            user: The User object that exceeded the rate limit (can be None for anonymous)
            
        Returns:
            Dict containing rate limit response with type, message, and retry_after
            
        Requirements: 8.3
        """
        user_id = user.id if user else 'anonymous'
        logger.warning(
            f"Rate limit exceeded for user {user_id}",
            extra={
                'user_id': user_id,
                'event': 'rate_limit_exceeded'
            }
        )
        
        return {
            'type': 'rate_limit',
            'message': 'Você atingiu o limite de mensagens. Por favor, aguarde alguns minutos.',
            'retry_after': 60,
            'error_code': 'RATE_LIMIT_EXCEEDED'
        }
    
    @staticmethod
    async def handle_session_error(error: Exception) -> Dict[str, Any]:
        """
        Handle session-related errors.
        
        When a session error occurs (e.g., session not found, expired, or corrupted),
        this method logs the error and returns a response to create a new session.
        
        Args:
            error: The exception that occurred related to the session
            
        Returns:
            Dict containing session error response with type, message, and action
            
        Requirements: 6.1
        """
        logger.error(
            f"Session Error: {error}",
            extra={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'event': 'session_error'
            }
        )
        
        return {
            'type': 'session_error',
            'message': 'Ocorreu um erro com sua sessão. Vamos iniciar uma nova conversa.',
            'action': 'create_new_session',
            'error_code': 'SESSION_ERROR'
        }
    
    @staticmethod
    async def handle_connection_error(error: Exception) -> Dict[str, Any]:
        """
        Handle WebSocket connection errors.
        
        Args:
            error: The connection exception that occurred
            
        Returns:
            Dict containing connection error response
        """
        logger.error(
            f"Connection Error: {error}",
            extra={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'event': 'connection_error'
            }
        )
        
        return {
            'type': 'connection_error',
            'message': 'Não foi possível conectar ao chat. Tentando reconectar...',
            'action': 'reconnect',
            'error_code': 'CONNECTION_ERROR'
        }
    
    @staticmethod
    async def handle_validation_error(error: Exception, field: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle input validation errors.
        
        Args:
            error: The validation exception that occurred
            field: Optional field name that failed validation
            
        Returns:
            Dict containing validation error response
        """
        logger.warning(
            f"Validation Error: {error}",
            extra={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'field': field,
                'event': 'validation_error'
            }
        )
        
        return {
            'type': 'validation_error',
            'message': 'Mensagem inválida. Por favor, tente novamente.',
            'field': field,
            'error_code': 'VALIDATION_ERROR'
        }
    
    @staticmethod
    async def handle_timeout_error(operation: str) -> Dict[str, Any]:
        """
        Handle timeout errors.
        
        Args:
            operation: The operation that timed out
            
        Returns:
            Dict containing timeout error response
        """
        logger.error(
            f"Timeout Error: {operation}",
            extra={
                'operation': operation,
                'event': 'timeout_error'
            }
        )
        
        return {
            'type': 'timeout_error',
            'message': 'A operação demorou muito tempo. Por favor, tente novamente.',
            'operation': operation,
            'error_code': 'TIMEOUT_ERROR'
        }
    
    @staticmethod
    def detect_frustration(message: str) -> bool:
        """
        Detect frustration keywords in user messages.
        
        Analyzes the message content for keywords and phrases that indicate
        user frustration, confusion, or dissatisfaction.
        
        Args:
            message: The user's message text
            
        Returns:
            bool: True if frustration is detected, False otherwise
            
        Requirements: 6.3, 6.5
        """
        # Convert to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Frustration keywords and phrases in Portuguese
        frustration_keywords = [
            # Direct frustration expressions
            'frustrado', 'frustrante', 'irritado', 'irritante',
            'chateado', 'decepcionado', 'decepção',
            
            # Negative feedback
            'não funciona', 'não está funcionando', 'não consegui',
            'não consigo', 'não entendi', 'não entendo',
            'não resolve', 'não resolveu', 'não ajuda', 'não ajudou',
            
            # Complaints
            'péssimo', 'horrível', 'terrível', 'ruim',
            'pior', 'problema', 'erro', 'bug',
            
            # Giving up expressions
            'desisto', 'desistir', 'cansei', 'cansado',
            'já tentei', 'tentei várias vezes', 'não adianta',
            
            # Requesting human help
            'falar com alguém', 'falar com pessoa', 'falar com uma pessoa',
            'atendente', 'humano', 'pessoa real', 'suporte humano',
            'gerente', 'supervisor',
            
            # Confusion and difficulty
            'confuso', 'complicado', 'difícil', 'impossível',
            'não faz sentido', 'não sei', 'perdido',
            
            # Repetition indicators
            'de novo', 'novamente', 'outra vez', 'já disse',
            'já falei', 'repetindo',
            
            # Time-related frustration
            'demora', 'demorado', 'lento', 'esperando',
            'quanto tempo', 'há horas', 'há dias',
            
            # Strong negative emotions
            'ódio', 'raiva', 'furioso', 'insuportável',
            'absurdo', 'ridículo', 'inaceitável'
        ]
        
        # Check for frustration keywords
        for keyword in frustration_keywords:
            if keyword in message_lower:
                logger.info(
                    f"Frustration detected: keyword '{keyword}' found in message",
                    extra={
                        'keyword': keyword,
                        'message_preview': message[:50],
                        'event': 'frustration_detected'
                    }
                )
                return True
        
        # Check for excessive punctuation (!!!, ???)
        if '!!!' in message or '???' in message:
            logger.info(
                "Frustration detected: excessive punctuation",
                extra={
                    'message_preview': message[:50],
                    'event': 'frustration_detected'
                }
            )
            return True
        
        # Check for all caps (at least 5 consecutive uppercase words)
        words = message.split()
        caps_count = sum(1 for word in words if word.isupper() and len(word) > 2)
        if caps_count >= 5:
            logger.info(
                "Frustration detected: excessive caps",
                extra={
                    'caps_count': caps_count,
                    'message_preview': message[:50],
                    'event': 'frustration_detected'
                }
            )
            return True
        
        return False
    
    @staticmethod
    async def handle_frustration_escalation(session: Any, message: str) -> Dict[str, Any]:
        """
        Handle escalation to human support when frustration is detected.
        
        Provides contact information and options for human support when
        the user shows signs of frustration or explicitly requests human help.
        
        Args:
            session: The ChatSession object
            message: The user's message that triggered escalation
            
        Returns:
            Dict containing escalation response with contact information
            
        Requirements: 6.3, 6.5
        """
        logger.info(
            f"Escalating to human support for session {session.session_id}",
            extra={
                'session_id': str(session.session_id),
                'user_id': session.user.id if session.user else None,
                'message_preview': message[:50],
                'event': 'escalation_to_human'
            }
        )
        
        # Mark session as escalated in analytics (will be saved later)
        # This is handled by the consumer when it saves analytics
        
        return {
            'type': 'escalation',
            'message': (
                'Entendo sua frustração e quero ajudar. '
                'Vou conectá-lo com nossa equipe de suporte humano.\n\n'
                '📞 **Opções de Contato:**\n\n'
                '• **Chat ao Vivo**: Disponível de segunda a sexta, 9h-18h\n'
                '• **Email**: suporte@jobfinder.com\n'
                '• **Telefone**: (11) 1234-5678\n'
                '• **WhatsApp**: (11) 98765-4321\n\n'
                'Nossa equipe responderá o mais rápido possível!'
            ),
            'actions': [
                {'label': 'Enviar Email', 'url': '/contact/', 'type': 'contact_form'},
                {'label': 'Ver FAQ', 'url': '/faq/', 'type': 'help'},
                {'label': 'Central de Ajuda', 'url': '/help-support/', 'type': 'help'}
            ],
            'escalated': True,
            'contact_info': {
                'email': 'suporte@jobfinder.com',
                'phone': '(11) 1234-5678',
                'whatsapp': '(11) 98765-4321',
                'hours': 'Segunda a Sexta, 9h-18h'
            }
        }
