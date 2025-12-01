"""
Chat Manager - Business Logic for Chat Sessions

This module handles chat session management, message persistence,
and context management.
"""

from services.chat_models import ChatSession, ChatMessage
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
import logging
import uuid

logger = logging.getLogger(__name__)


class ChatManager:
    """
    Manages chat sessions and message persistence.
    
    Responsibilities:
    - Create and retrieve chat sessions
    - Save and retrieve messages
    - Manage session context
    - Clean up old sessions
    """
    
    def create_session(self, user, context=None):
        """
        Create a new chat session.
        
        Args:
            user: User object or None for anonymous
            context: Initial context data (navigation, user type, etc.)
        
        Returns:
            ChatSession object
        """
        try:
            if context is None:
                context = {}
            
            # Determine user type
            if user and user.is_authenticated:
                # Check if user is a provider or client based on profile
                # For now, default to 'client' - will be enhanced later
                user_type = 'client'
            else:
                user_type = 'anonymous'
            
            session = ChatSession.objects.create(
                user=user if user and user.is_authenticated else None,
                anonymous_id=str(uuid.uuid4()) if not user or not user.is_authenticated else None,
                context_data=context,
                user_type=user_type,
                is_active=True
            )
            
            logger.info(
                f"Created new chat session",
                extra={
                    'session_id': str(session.session_id),
                    'user_id': user.id if user and user.is_authenticated else None,
                    'user_type': user_type
                }
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {e}", exc_info=True)
            raise
    
    def get_session(self, session_id):
        """
        Retrieve an existing chat session.
        
        Args:
            session_id: UUID of the session
        
        Returns:
            ChatSession object or None
        """
        try:
            # Try to get from cache first
            cache_key = f'chat_session_{session_id}'
            session = cache.get(cache_key)
            
            if session is None:
                # Get from database
                session = ChatSession.objects.filter(
                    session_id=session_id,
                    is_active=True
                ).first()
                
                if session:
                    # Cache for 5 minutes
                    cache.set(cache_key, session, 300)
            
            return session
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}", exc_info=True)
            return None
    
    def get_or_create_session(self, user, session_id=None, context=None):
        """
        Get existing session or create new one.
        
        Args:
            user: User object or None for anonymous
            session_id: Optional existing session ID
            context: Initial context data
        
        Returns:
            ChatSession object
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                # Update last activity
                session.updated_at = timezone.now()
                session.save(update_fields=['updated_at'])
                return session
        
        # Create new session
        return self.create_session(user, context)
    
    def save_message(self, session, content, sender_type, metadata=None):
        """
        Save a message to the database.
        
        Args:
            session: ChatSession object
            content: Message content
            sender_type: Sender type ('user', 'assistant', 'system')
            metadata: Optional metadata dict
        
        Returns:
            ChatMessage object
        """
        try:
            if metadata is None:
                metadata = {}
            
            message = ChatMessage.objects.create(
                session=session,
                sender_type=sender_type,
                content=content,
                metadata=metadata
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save(update_fields=['updated_at'])
            
            # Invalidate session cache
            cache_key = f'chat_session_{session.session_id}'
            cache.delete(cache_key)
            
            logger.info(
                f"Saved message",
                extra={
                    'session_id': str(session.session_id),
                    'sender_type': sender_type,
                    'message_id': str(message.message_id)
                }
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Error saving message: {e}", exc_info=True)
            raise
    
    def get_history(self, session, limit=50):
        """
        Retrieve message history for a session.
        
        Args:
            session: ChatSession object
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of ChatMessage objects
        """
        try:
            messages = ChatMessage.objects.filter(
                session=session
            ).order_by('-created_at')[:limit]
            
            # Return in chronological order
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error retrieving history: {e}", exc_info=True)
            return []
    
    def update_context(self, session, context):
        """
        Update session context data.
        
        Args:
            session: ChatSession object
            context: Context data to update (will be merged with existing)
        """
        try:
            # Merge with existing context
            session.context_data.update(context)
            session.save(update_fields=['context_data', 'updated_at'])
            
            # Invalidate cache
            cache_key = f'chat_session_{session.session_id}'
            cache.delete(cache_key)
            
            logger.info(
                f"Updated session context",
                extra={'session_id': str(session.session_id)}
            )
            
        except Exception as e:
            logger.error(f"Error updating context: {e}", exc_info=True)
            raise
    
    def close_session(self, session_id):
        """
        Close a chat session.
        
        Args:
            session_id: UUID of the session
        """
        try:
            session = self.get_session(session_id)
            if session:
                session.is_active = False
                session.closed_at = timezone.now()
                session.save(update_fields=['is_active', 'closed_at', 'updated_at'])
                
                # Invalidate cache
                cache_key = f'chat_session_{session_id}'
                cache.delete(cache_key)
                
                logger.info(
                    f"Closed session",
                    extra={'session_id': str(session_id)}
                )
                
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}", exc_info=True)
            raise
    
    def get_active_sessions(self, user):
        """
        Get all active sessions for a user.
        
        Args:
            user: User object
        
        Returns:
            QuerySet of ChatSession objects
        """
        try:
            return ChatSession.objects.filter(
                user=user,
                is_active=True
            ).order_by('-updated_at')
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}", exc_info=True)
            return ChatSession.objects.none()
    
    def cleanup_old_sessions(self):
        """
        Clean up sessions older than 24 hours.
        
        Closes sessions that haven't been updated in the last 24 hours.
        This method should be called periodically (e.g., via a cron job or
        Django management command).
        
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            from datetime import timedelta
            
            # Calculate cutoff time (24 hours ago)
            cutoff_time = timezone.now() - timedelta(hours=24)
            
            # Find active sessions older than 24 hours
            old_sessions = ChatSession.objects.filter(
                is_active=True,
                updated_at__lt=cutoff_time
            )
            
            count = old_sessions.count()
            
            if count > 0:
                # Close all old sessions
                old_sessions.update(
                    is_active=False,
                    closed_at=timezone.now()
                )
                
                # Clear cache for closed sessions
                for session in old_sessions:
                    cache_key = f'chat_session_{session.session_id}'
                    cache.delete(cache_key)
                
                logger.info(
                    f"Cleaned up {count} old chat sessions",
                    extra={'count': count, 'cutoff_time': cutoff_time}
                )
            
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}", exc_info=True)
            return 0
