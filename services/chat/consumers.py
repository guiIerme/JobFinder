"""
WebSocket Consumer for Chat IA Assistente (Sophie)

This module handles WebSocket connections for real-time chat interactions.
"""

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import logging
from datetime import datetime
from .manager import ChatManager
from .error_handler import ChatErrorHandler
from .security import ChatSecurityValidator
from django.core.cache import cache
from django.conf import settings
import time

logger = logging.getLogger(__name__)

# Initialize ChatManager
chat_manager = ChatManager()


class AnalyticsTracker:
    """
    Helper class for tracking analytics metrics during chat sessions.
    
    Tracks message counts, response times, and other session metrics.
    Requirements: 7.1, 7.2
    """
    
    def __init__(self):
        self.response_times = []
        self.user_message_count = 0
        self.assistant_message_count = 0
        self.topics = []
        self.actions = []
    
    def track_user_message(self):
        """Increment user message counter"""
        self.user_message_count += 1
    
    def track_assistant_message(self, response_time_ms):
        """
        Track assistant message and response time.
        
        Args:
            response_time_ms: Response time in milliseconds
        """
        self.assistant_message_count += 1
        if response_time_ms is not None:
            self.response_times.append(response_time_ms)
    
    def track_topic(self, topic):
        """
        Track a topic discussed in the conversation.
        
        Args:
            topic: Topic identifier or name
        """
        if topic and topic not in self.topics:
            self.topics.append(topic)
    
    def track_action(self, action_type, action_data=None):
        """
        Track a user action.
        
        Args:
            action_type: Type of action (e.g., 'link_clicked', 'service_viewed')
            action_data: Additional data about the action
        """
        action = {
            'type': action_type,
            'timestamp': datetime.now().isoformat()
        }
        if action_data:
            action['data'] = action_data
        self.actions.append(action)
    
    def get_average_response_time(self):
        """
        Calculate average response time.
        
        Returns:
            float: Average response time in milliseconds, or None if no responses
        """
        if not self.response_times:
            return None
        return sum(self.response_times) / len(self.response_times)
    
    def get_total_messages(self):
        """Get total message count"""
        return self.user_message_count + self.assistant_message_count
    
    def to_dict(self):
        """
        Convert tracker data to dictionary for storage.
        
        Returns:
            dict: Analytics data
        """
        return {
            'total_messages': self.get_total_messages(),
            'user_messages': self.user_message_count,
            'assistant_messages': self.assistant_message_count,
            'average_response_time_ms': self.get_average_response_time(),
            'topics_discussed': self.topics,
            'actions_taken': self.actions
        }


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling chat connections and messages.
    
    Responsibilities:
    - Manage WebSocket connection lifecycle
    - Authenticate users
    - Route messages to appropriate handlers
    - Implement rate limiting
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.session = None
        self.user = None
        self.channel_group_name = None
        self.rate_limit_key = None
        self.analytics_tracker = AnalyticsTracker()
    
    async def connect(self):
        """
        Handle new WebSocket connection.
        
        - Authenticate user
        - Create or retrieve chat session
        - Join channel group
        """
        try:
            # Authenticate user
            self.user = self.scope.get('user')
            
            if not self.user or not self.user.is_authenticated:
                logger.warning("Unauthenticated WebSocket connection attempt")
                # Allow anonymous users but mark them as such
                self.user = None
            
            # Accept the WebSocket connection
            await self.accept()
            
            logger.info(
                f"WebSocket connection established",
                extra={
                    'user_id': self.user.id if self.user else None,
                    'channel_name': self.channel_name
                }
            )
            
            # Send welcome message
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Conectado ao chat. Olá! Sou Sophie, sua assistente virtual.',
                'timestamp': datetime.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"Error in connect: {e}", exc_info=True)
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        
        - Clean up session
        - Leave channel group
        - Save analytics data
        """
        try:
            # Save analytics before disconnecting
            if self.session:
                await self.save_analytics()
            
            # Leave channel group if joined
            if self.channel_group_name:
                await self.channel_layer.group_discard(
                    self.channel_group_name,
                    self.channel_name
                )
                logger.info(
                    f"Left channel group: {self.channel_group_name}",
                    extra={'session_id': self.session_id}
                )
            
            logger.info(
                f"WebSocket disconnected",
                extra={
                    'user_id': self.user.id if self.user else None,
                    'session_id': self.session_id,
                    'close_code': close_code,
                    'total_messages': self.analytics_tracker.get_total_messages()
                }
            )
            
        except Exception as e:
            logger.error(f"Error in disconnect: {e}", exc_info=True)
    
    async def receive(self, text_data):
        """
        Handle incoming messages from WebSocket.
        
        - Parse message
        - Route to appropriate handler
        - Apply rate limiting
        """
        try:
            # Parse incoming message
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            logger.info(
                f"Received message",
                extra={
                    'user_id': self.user.id if self.user else None,
                    'session_id': self.session_id,
                    'message_type': message_type
                }
            )
            
            # Route to appropriate handler based on message type
            if message_type == 'message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            elif message_type == 'session_init':
                await self.handle_session_init(data)
            elif message_type == 'session_close':
                await self.handle_session_close(data)
            elif message_type == 'satisfaction_rating':
                await self.handle_satisfaction_rating(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Tipo de mensagem desconhecido',
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato de mensagem inválido',
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error in receive: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Erro ao processar mensagem',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_chat_message(self, data):
        """
        Handle chat message from user.
        
        Args:
            data: Message data containing 'content' and optional metadata
        """
        # Check rate limit first
        is_allowed, retry_after = await self.check_rate_limit()
        if not is_allowed:
            await self.send_rate_limit_error(retry_after)
            return
        
        content = data.get('content', '')
        
        # Validate message content (Requirements: 8.3)
        is_valid, error_message = ChatSecurityValidator.validate_message_content(content)
        if not is_valid:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': error_message,
                'timestamp': datetime.now().isoformat()
            }))
            logger.warning(
                f"Invalid message content",
                extra={
                    'user_id': self.user.id if self.user else None,
                    'error': error_message
                }
            )
            return
        
        # Sanitize message content (Requirements: 8.3)
        if settings.CHAT_CONFIG.get('SANITIZE_INPUT', True):
            content = ChatSecurityValidator.sanitize_message_content(content)
        
        # Ensure session exists
        if not self.session:
            # Auto-initialize session if not already done
            await self.handle_session_init({'context': {}})
        
        # Save user message to database
        try:
            # Track user message in analytics
            self.analytics_tracker.track_user_message()
            
            # Start timing for response
            start_time = time.time()
            
            user_message = await self.save_chat_message(
                self.session,
                content,
                'user',
                {'client_timestamp': data.get('timestamp')}
            )
            
            # Echo message back to confirm receipt
            await self.send(text_data=json.dumps({
                'type': 'message',
                'sender': 'user',
                'content': content,
                'message_id': str(user_message.message_id),
                'timestamp': user_message.created_at.isoformat()
            }))
            
            # Check for frustration and handle escalation if needed
            # Requirements: 6.3, 6.5
            is_frustrated = ChatErrorHandler.detect_frustration(content)
            
            if is_frustrated:
                # Mark session as escalated
                await self.mark_session_escalated(self.session)
                
                # Get escalation response
                escalation_response = await ChatErrorHandler.handle_frustration_escalation(
                    self.session,
                    content
                )
                
                # Calculate response time
                end_time = time.time()
                response_time_ms = int((end_time - start_time) * 1000)
                
                # Save escalation message
                assistant_message = await self.save_chat_message(
                    self.session,
                    escalation_response['message'],
                    'assistant',
                    {
                        'escalated': True,
                        'processing_time_ms': response_time_ms,
                        'actions': escalation_response.get('actions', []),
                        'contact_info': escalation_response.get('contact_info', {})
                    }
                )
                
                # Track assistant message and response time
                self.analytics_tracker.track_assistant_message(response_time_ms)
                self.analytics_tracker.track_action('escalated_to_human', {
                    'reason': 'frustration_detected',
                    'message_preview': content[:50]
                })
                
                # Send escalation response
                await self.send(text_data=json.dumps({
                    'type': 'message',
                    'sender': 'assistant',
                    'content': escalation_response['message'],
                    'message_id': str(assistant_message.message_id),
                    'timestamp': assistant_message.created_at.isoformat(),
                    'escalated': True,
                    'actions': escalation_response.get('actions', []),
                    'contact_info': escalation_response.get('contact_info', {})
                }))
                
                logger.info(
                    f"Escalation message sent",
                    extra={
                        'session_id': self.session_id,
                        'response_time_ms': response_time_ms,
                        'reason': 'frustration_detected'
                    }
                )
                
                return
            
            # Send typing indicator
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'is_typing': True,
                'timestamp': datetime.now().isoformat()
            }))
            
            # Placeholder for AI response (will be implemented in task 5)
            assistant_content = f'Recebi sua mensagem: "{content}". Processamento de IA será implementado em tarefas futuras.'
            
            # Calculate response time
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Save assistant response with processing time
            assistant_message = await self.save_chat_message(
                self.session,
                assistant_content,
                'assistant',
                {'placeholder': True, 'processing_time_ms': response_time_ms}
            )
            
            # Track assistant message and response time in analytics
            self.analytics_tracker.track_assistant_message(response_time_ms)
            
            # Stop typing indicator
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'is_typing': False,
                'timestamp': datetime.now().isoformat()
            }))
            
            # Send assistant response
            await self.send(text_data=json.dumps({
                'type': 'message',
                'sender': 'assistant',
                'content': assistant_content,
                'message_id': str(assistant_message.message_id),
                'timestamp': assistant_message.created_at.isoformat()
            }))
            
            logger.info(
                f"Message processed",
                extra={
                    'session_id': self.session_id,
                    'response_time_ms': response_time_ms,
                    'user_messages': self.analytics_tracker.user_message_count,
                    'assistant_messages': self.analytics_tracker.assistant_message_count
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling chat message: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Erro ao processar mensagem',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_typing_indicator(self, data):
        """
        Handle typing indicator from user.
        
        Args:
            data: Typing indicator data
        """
        is_typing = data.get('is_typing', False)
        
        # Broadcast typing indicator to channel group if exists
        if self.channel_group_name:
            await self.channel_layer.group_send(
                self.channel_group_name,
                {
                    'type': 'typing_indicator',
                    'is_typing': is_typing,
                    'user_id': self.user.id if self.user else None
                }
            )
    
    async def handle_session_init(self, data):
        """
        Handle session initialization request.
        
        Args:
            data: Session initialization data containing optional session_id and context
        """
        try:
            session_id = data.get('session_id')
            context = data.get('context', {})
            
            # Validate session ID if provided (Requirements: 8.3)
            if session_id:
                is_valid, error_message = ChatSecurityValidator.validate_session_id(session_id)
                if not is_valid:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': error_message,
                        'timestamp': datetime.now().isoformat()
                    }))
                    logger.warning(
                        f"Invalid session ID",
                        extra={
                            'user_id': self.user.id if self.user else None,
                            'error': error_message
                        }
                    )
                    return
            
            # Validate context data (Requirements: 8.3)
            is_valid, error_message = ChatSecurityValidator.validate_context_data(context)
            if not is_valid:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': error_message,
                    'timestamp': datetime.now().isoformat()
                }))
                logger.warning(
                    f"Invalid context data",
                    extra={
                        'user_id': self.user.id if self.user else None,
                        'error': error_message
                    }
                )
                return
            
            # Get or create session
            self.session = await self.get_or_create_session(
                self.user,
                session_id,
                context
            )
            
            self.session_id = str(self.session.session_id)
            
            # Update context if provided and session already existed
            if session_id and context:
                await self.update_session_context(self.session, context)
            
            # Create channel group name for this session
            self.channel_group_name = f'chat_{self.session_id}'
            
            # Join channel group
            await self.channel_layer.group_add(
                self.channel_group_name,
                self.channel_name
            )
            
            # Load message history
            history = await self.get_session_history(self.session)
            
            # Send session initialized response
            await self.send(text_data=json.dumps({
                'type': 'session_initialized',
                'session_id': self.session_id,
                'history': [
                    {
                        'sender': msg.sender_type,
                        'content': msg.content,
                        'timestamp': msg.created_at.isoformat(),
                        'metadata': msg.metadata
                    }
                    for msg in history
                ],
                'timestamp': datetime.now().isoformat()
            }))
            
            logger.info(
                f"Session initialized",
                extra={
                    'session_id': self.session_id,
                    'user_id': self.user.id if self.user else None,
                    'history_count': len(history)
                }
            )
            
        except Exception as e:
            logger.error(f"Error initializing session: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Erro ao inicializar sessão',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_session_close(self, data):
        """
        Handle session close request.
        
        Args:
            data: Session close data
        """
        try:
            if self.session_id:
                # Save analytics before closing
                await self.save_analytics()
                
                await self.close_chat_session(self.session_id)
                
                await self.send(text_data=json.dumps({
                    'type': 'session_closed',
                    'session_id': self.session_id,
                    'message': 'Sessão encerrada com sucesso',
                    'timestamp': datetime.now().isoformat()
                }))
                
                logger.info(
                    f"Session closed by user request",
                    extra={
                        'session_id': self.session_id,
                        'total_messages': self.analytics_tracker.get_total_messages()
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Nenhuma sessão ativa para fechar',
                    'timestamp': datetime.now().isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error closing session: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Erro ao fechar sessão',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_satisfaction_rating(self, data):
        """
        Handle satisfaction rating submission from user.
        
        Args:
            data: Rating data containing 'rating' (1-5) and optional 'feedback'
        
        Requirements: 6.4
        """
        try:
            rating = data.get('rating')
            feedback = data.get('feedback', '')
            
            # Validate rating (Requirements: 8.3)
            is_valid, error_message, rating_int = ChatSecurityValidator.validate_rating(rating)
            if not is_valid:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': error_message,
                    'timestamp': datetime.now().isoformat()
                }))
                logger.warning(
                    f"Invalid rating",
                    extra={
                        'user_id': self.user.id if self.user else None,
                        'error': error_message
                    }
                )
                return
            
            # Use validated rating
            rating = rating_int
            
            # Validate feedback if provided (Requirements: 8.3)
            if feedback:
                is_valid, error_message = ChatSecurityValidator.validate_feedback(feedback)
                if not is_valid:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': error_message,
                        'timestamp': datetime.now().isoformat()
                    }))
                    logger.warning(
                        f"Invalid feedback",
                        extra={
                            'user_id': self.user.id if self.user else None,
                            'error': error_message
                        }
                    )
                    return
                
                # Sanitize feedback (Requirements: 8.3)
                if settings.CHAT_CONFIG.get('SANITIZE_INPUT', True):
                    feedback = ChatSecurityValidator.sanitize_feedback(feedback)
            
            # Ensure session exists
            if not self.session:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Nenhuma sessão ativa para avaliar',
                    'timestamp': datetime.now().isoformat()
                }))
                return
            
            # Save rating to session
            await self.save_satisfaction_rating(self.session, rating, feedback)
            
            # Send confirmation
            await self.send(text_data=json.dumps({
                'type': 'satisfaction_rating_saved',
                'rating': rating,
                'message': 'Obrigado pela sua avaliação!',
                'timestamp': datetime.now().isoformat()
            }))
            
            logger.info(
                f"Satisfaction rating saved",
                extra={
                    'session_id': self.session_id,
                    'user_id': self.user.id if self.user else None,
                    'rating': rating,
                    'has_feedback': bool(feedback)
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling satisfaction rating: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Erro ao salvar avaliação',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def send_message(self, event):
        """
        Send message to WebSocket client.
        
        This method is called when a message is sent to the channel group.
        
        Args:
            event: Event data containing message information
        """
        try:
            await self.send(text_data=json.dumps({
                'type': event.get('type', 'message'),
                'sender': event.get('sender', 'assistant'),
                'content': event.get('content', ''),
                'metadata': event.get('metadata', {}),
                'timestamp': event.get('timestamp', datetime.now().isoformat())
            }))
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
    
    async def send_typing_indicator(self, event):
        """
        Send typing indicator to client.
        
        Args:
            event: Event data containing typing indicator information
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'is_typing': event.get('is_typing', False),
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending typing indicator: {e}", exc_info=True)
    
    async def typing_indicator(self, event):
        """
        Handle typing indicator event from channel layer.
        
        Args:
            event: Event data
        """
        await self.send_typing_indicator(event)
    
    # Database access methods (wrapped for async)
    
    @database_sync_to_async
    def get_or_create_session(self, user, session_id=None, context=None):
        """
        Get or create a chat session (async wrapper).
        
        Args:
            user: User object or None
            session_id: Optional existing session ID
            context: Optional context data
        
        Returns:
            ChatSession object
        """
        return chat_manager.get_or_create_session(user, session_id, context)
    
    @database_sync_to_async
    def get_session_history(self, session, limit=50):
        """
        Get message history for a session (async wrapper).
        
        Args:
            session: ChatSession object
            limit: Maximum number of messages
        
        Returns:
            List of ChatMessage objects
        """
        return chat_manager.get_history(session, limit)
    
    @database_sync_to_async
    def save_chat_message(self, session, content, sender_type, metadata=None):
        """
        Save a chat message (async wrapper).
        
        Args:
            session: ChatSession object
            content: Message content
            sender_type: Sender type ('user', 'assistant', 'system')
            metadata: Optional metadata dict
        
        Returns:
            ChatMessage object
        """
        return chat_manager.save_message(session, content, sender_type, metadata)
    
    @database_sync_to_async
    def update_session_context(self, session, context):
        """
        Update session context (async wrapper).
        
        Args:
            session: ChatSession object
            context: Context data to update
        """
        chat_manager.update_context(session, context)
    
    @database_sync_to_async
    def close_chat_session(self, session_id):
        """
        Close a chat session (async wrapper).
        
        Args:
            session_id: Session ID to close
        """
        chat_manager.close_session(session_id)
    
    @database_sync_to_async
    def save_satisfaction_rating(self, session, rating, feedback=None):
        """
        Save satisfaction rating to chat session (async wrapper).
        
        Args:
            session: ChatSession object
            rating: Integer rating from 1-5
            feedback: Optional feedback text
        
        Requirements: 6.4
        """
        session.satisfaction_rating = rating
        
        # Store feedback in context_data if provided
        if feedback:
            if not session.context_data:
                session.context_data = {}
            session.context_data['satisfaction_feedback'] = feedback
        
        session.save(update_fields=['satisfaction_rating', 'context_data'])
        
        logger.info(
            f"Satisfaction rating saved to session",
            extra={
                'session_id': str(session.session_id),
                'rating': rating,
                'has_feedback': bool(feedback)
            }
        )
    
    @database_sync_to_async
    def mark_session_escalated(self, session):
        """
        Mark a session as escalated to human support.
        
        Updates the ChatAnalytics record to indicate escalation.
        
        Args:
            session: ChatSession object
            
        Requirements: 6.3, 6.5
        """
        from services.chat_models import ChatAnalytics
        
        try:
            # Get or create analytics record
            analytics, created = ChatAnalytics.objects.get_or_create(
                session=session,
                defaults={'escalated_to_human': True}
            )
            
            # Update escalation flag if already exists
            if not created and not analytics.escalated_to_human:
                analytics.escalated_to_human = True
                analytics.save(update_fields=['escalated_to_human'])
            
            logger.info(
                f"Session marked as escalated",
                extra={
                    'session_id': str(session.session_id),
                    'user_id': session.user.id if session.user else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error marking session as escalated: {e}", exc_info=True)
    
    @database_sync_to_async
    def save_analytics(self):
        """
        Save or update analytics data for the current session.
        
        Creates or updates a ChatAnalytics record with tracked metrics.
        Requirements: 7.1, 7.2
        """
        from services.chat_models import ChatAnalytics
        
        if not self.session:
            logger.warning("Cannot save analytics: no session")
            return
        
        try:
            analytics_data = self.analytics_tracker.to_dict()
            
            # Check if any escalation actions were tracked
            has_escalation = any(
                action.get('type') == 'escalated_to_human' 
                for action in analytics_data.get('actions_taken', [])
            )
            
            # Get or create analytics record
            analytics, created = ChatAnalytics.objects.get_or_create(
                session=self.session,
                defaults={
                    'total_messages': analytics_data['total_messages'],
                    'user_messages': analytics_data['user_messages'],
                    'assistant_messages': analytics_data['assistant_messages'],
                    'average_response_time_ms': analytics_data['average_response_time_ms'],
                    'topics_discussed': analytics_data['topics_discussed'],
                    'actions_taken': analytics_data['actions_taken'],
                    'escalated_to_human': has_escalation,
                }
            )
            
            # Update if already exists
            if not created:
                analytics.total_messages = analytics_data['total_messages']
                analytics.user_messages = analytics_data['user_messages']
                analytics.assistant_messages = analytics_data['assistant_messages']
                analytics.average_response_time_ms = analytics_data['average_response_time_ms']
                analytics.topics_discussed = analytics_data['topics_discussed']
                analytics.actions_taken = analytics_data['actions_taken']
                
                # Update escalation flag if escalation occurred
                if has_escalation:
                    analytics.escalated_to_human = True
                
                analytics.save()
            
            logger.info(
                f"Analytics saved for session {self.session_id}",
                extra={
                    'session_id': self.session_id,
                    'total_messages': analytics_data['total_messages'],
                    'average_response_time_ms': analytics_data['average_response_time_ms'],
                    'escalated': has_escalation,
                    'is_new': created
                }
            )
            
        except Exception as e:
            logger.error(f"Error saving analytics: {e}", exc_info=True)
    
    # Rate limiting methods
    
    def get_rate_limit_key(self):
        """
        Generate rate limit key for this connection.
        
        Returns:
            str: Cache key for rate limiting
        """
        if self.user and self.user.is_authenticated:
            return f'chat_rate_limit_user_{self.user.id}'
        else:
            # Use channel name for anonymous users (per connection)
            return f'chat_rate_limit_anon_{self.channel_name}'
    
    async def check_rate_limit(self):
        """
        Check if the user has exceeded rate limit.
        
        Returns:
            tuple: (is_allowed: bool, retry_after: int)
        """
        if not self.rate_limit_key:
            self.rate_limit_key = self.get_rate_limit_key()
        
        # Get rate limit configuration
        rate_limit = settings.CHAT_CONFIG.get('RATE_LIMIT_MESSAGES_PER_MINUTE', 10)
        window_seconds = 60
        
        # Get current message count from cache
        current_count = cache.get(self.rate_limit_key, 0)
        
        if current_count >= rate_limit:
            # Rate limit exceeded
            # Try to get TTL, fallback to window_seconds if not supported
            try:
                ttl = cache.ttl(self.rate_limit_key)
                retry_after = ttl if ttl > 0 else window_seconds
            except AttributeError:
                # LocMemCache doesn't support ttl(), use default window
                retry_after = window_seconds
            
            logger.warning(
                f"Rate limit exceeded",
                extra={
                    'user_id': self.user.id if self.user else None,
                    'rate_limit_key': self.rate_limit_key,
                    'current_count': current_count,
                    'limit': rate_limit
                }
            )
            
            return False, retry_after
        
        # Increment counter
        if current_count == 0:
            # First message in window, set with expiry
            cache.set(self.rate_limit_key, 1, window_seconds)
        else:
            # Increment existing counter
            cache.incr(self.rate_limit_key)
        
        return True, 0
    
    async def send_rate_limit_error(self, retry_after):
        """
        Send rate limit error to client.
        
        Args:
            retry_after: Seconds until rate limit resets
        """
        await self.send(text_data=json.dumps({
            'type': 'rate_limit_error',
            'message': f'Você atingiu o limite de mensagens. Por favor, aguarde {retry_after} segundos.',
            'retry_after': retry_after,
            'timestamp': datetime.now().isoformat()
        }))
