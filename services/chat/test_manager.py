"""
Unit tests for ChatManager service class.

Tests session CRUD operations, message persistence, and context management.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from services.chat.manager import ChatManager
from services.chat_models import ChatSession, ChatMessage


class ChatManagerTests(TestCase):
    """Test suite for ChatManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = ChatManager()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_session_authenticated_user(self):
        """Test session creation for authenticated user"""
        context = {'page': '/services/', 'referrer': '/'}
        session = self.manager.create_session(self.user, context)
        
        self.assertIsNotNone(session)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.user_type, 'client')
        self.assertTrue(session.is_active)
        self.assertEqual(session.context_data, context)
        self.assertIsNone(session.anonymous_id)
    
    def test_create_session_anonymous_user(self):
        """Test session creation for anonymous user"""
        session = self.manager.create_session(None)
        
        self.assertIsNotNone(session)
        self.assertIsNone(session.user)
        self.assertEqual(session.user_type, 'anonymous')
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.anonymous_id)
    
    def test_get_session(self):
        """Test session retrieval"""
        # Create a session
        session = self.manager.create_session(self.user)
        session_id = session.session_id
        
        # Retrieve the session
        retrieved_session = self.manager.get_session(session_id)
        
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session_id)
        self.assertEqual(retrieved_session.user, self.user)
    
    def test_get_session_with_caching(self):
        """Test that session retrieval uses caching"""
        # Create a session
        session = self.manager.create_session(self.user)
        session_id = session.session_id
        
        # First retrieval (from database)
        session1 = self.manager.get_session(session_id)
        
        # Second retrieval (should be from cache)
        session2 = self.manager.get_session(session_id)
        
        self.assertEqual(session1.session_id, session2.session_id)
    
    def test_close_session(self):
        """Test session closure"""
        # Create a session
        session = self.manager.create_session(self.user)
        session_id = session.session_id
        
        # Close the session
        self.manager.close_session(session_id)
        
        # Verify session is closed
        closed_session = ChatSession.objects.get(session_id=session_id)
        self.assertFalse(closed_session.is_active)
        self.assertIsNotNone(closed_session.closed_at)
    
    def test_save_message(self):
        """Test message persistence"""
        # Create a session
        session = self.manager.create_session(self.user)
        
        # Save a user message
        message = self.manager.save_message(
            session=session,
            content='Hello, I need help',
            sender_type='user',
            metadata={'intent': 'greeting'}
        )
        
        self.assertIsNotNone(message)
        self.assertEqual(message.session, session)
        self.assertEqual(message.sender_type, 'user')
        self.assertEqual(message.content, 'Hello, I need help')
        self.assertEqual(message.metadata['intent'], 'greeting')
    
    def test_get_history(self):
        """Test message history retrieval"""
        # Create a session
        session = self.manager.create_session(self.user)
        
        # Save multiple messages
        self.manager.save_message(session, 'Message 1', 'user')
        self.manager.save_message(session, 'Response 1', 'assistant')
        self.manager.save_message(session, 'Message 2', 'user')
        
        # Get history
        history = self.manager.get_history(session)
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].content, 'Message 1')
        self.assertEqual(history[1].content, 'Response 1')
        self.assertEqual(history[2].content, 'Message 2')
    
    def test_get_history_with_limit(self):
        """Test message history retrieval with pagination"""
        # Create a session
        session = self.manager.create_session(self.user)
        
        # Save multiple messages
        for i in range(10):
            self.manager.save_message(session, f'Message {i}', 'user')
        
        # Get history with limit
        history = self.manager.get_history(session, limit=5)
        
        self.assertEqual(len(history), 5)
    
    def test_update_context(self):
        """Test context update"""
        # Create a session with initial context
        initial_context = {'page': '/services/'}
        session = self.manager.create_session(self.user, initial_context)
        
        # Update context
        new_context = {'page': '/meus-pedidos/', 'action': 'view_orders'}
        self.manager.update_context(session, new_context)
        
        # Verify context was updated
        updated_session = ChatSession.objects.get(session_id=session.session_id)
        self.assertEqual(updated_session.context_data['page'], '/meus-pedidos/')
        self.assertEqual(updated_session.context_data['action'], 'view_orders')
    
    def test_cleanup_old_sessions(self):
        """Test cleanup of sessions older than 24 hours"""
        # Create an old session (25 hours ago)
        old_session = self.manager.create_session(self.user)
        old_time = timezone.now() - timedelta(hours=25)
        ChatSession.objects.filter(session_id=old_session.session_id).update(
            updated_at=old_time
        )
        
        # Create a recent session
        recent_session = self.manager.create_session(self.user)
        
        # Run cleanup
        cleaned_count = self.manager.cleanup_old_sessions()
        
        # Verify old session was closed
        old_session_updated = ChatSession.objects.get(session_id=old_session.session_id)
        self.assertFalse(old_session_updated.is_active)
        self.assertIsNotNone(old_session_updated.closed_at)
        
        # Verify recent session is still active
        recent_session_updated = ChatSession.objects.get(session_id=recent_session.session_id)
        self.assertTrue(recent_session_updated.is_active)
        
        # Verify count
        self.assertEqual(cleaned_count, 1)
    
    def test_get_active_sessions(self):
        """Test retrieval of active sessions for a user"""
        # Create multiple sessions
        session1 = self.manager.create_session(self.user)
        session2 = self.manager.create_session(self.user)
        
        # Close one session
        self.manager.close_session(session1.session_id)
        
        # Get active sessions
        active_sessions = self.manager.get_active_sessions(self.user)
        
        # Verify only active session is returned
        self.assertEqual(active_sessions.count(), 1)
        self.assertEqual(active_sessions.first().session_id, session2.session_id)
    
    def test_get_or_create_session_creates_new(self):
        """Test get_or_create_session creates new session when no session_id provided"""
        context = {'page': '/services/'}
        session = self.manager.get_or_create_session(self.user, context=context)
        
        self.assertIsNotNone(session)
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.context_data, context)
    
    def test_get_or_create_session_retrieves_existing(self):
        """Test get_or_create_session retrieves existing session when session_id provided"""
        # Create initial session
        initial_session = self.manager.create_session(self.user)
        session_id = initial_session.session_id
        
        # Get or create with existing session_id
        retrieved_session = self.manager.get_or_create_session(
            self.user, 
            session_id=session_id
        )
        
        self.assertEqual(retrieved_session.session_id, session_id)
    
    def test_get_session_returns_none_for_invalid_id(self):
        """Test get_session returns None for non-existent session"""
        import uuid
        fake_id = uuid.uuid4()
        session = self.manager.get_session(fake_id)
        
        self.assertIsNone(session)
    
    def test_get_session_returns_none_for_inactive_session(self):
        """Test get_session returns None for inactive sessions"""
        # Create and close a session
        session = self.manager.create_session(self.user)
        session_id = session.session_id
        self.manager.close_session(session_id)
        
        # Try to retrieve the closed session
        retrieved_session = self.manager.get_session(session_id)
        
        self.assertIsNone(retrieved_session)
    
    def test_save_message_updates_session_timestamp(self):
        """Test that saving a message updates the session's updated_at timestamp"""
        # Create a session
        session = self.manager.create_session(self.user)
        original_updated_at = session.updated_at
        
        # Wait a moment and save a message
        import time
        time.sleep(0.1)
        
        self.manager.save_message(session, 'Test message', 'user')
        
        # Refresh session from database
        session.refresh_from_db()
        
        # Verify timestamp was updated
        self.assertGreater(session.updated_at, original_updated_at)
    
    def test_cleanup_old_sessions_no_sessions_to_clean(self):
        """Test cleanup when there are no old sessions"""
        # Create only recent sessions
        self.manager.create_session(self.user)
        
        # Run cleanup
        cleaned_count = self.manager.cleanup_old_sessions()
        
        # Verify no sessions were cleaned
        self.assertEqual(cleaned_count, 0)
    
    def test_update_context_merges_with_existing(self):
        """Test that update_context merges with existing context data"""
        # Create session with initial context
        initial_context = {'page': '/services/', 'user_preference': 'dark_mode'}
        session = self.manager.create_session(self.user, initial_context)
        
        # Update with new context
        new_context = {'page': '/meus-pedidos/'}
        self.manager.update_context(session, new_context)
        
        # Verify context was merged (not replaced)
        updated_session = ChatSession.objects.get(session_id=session.session_id)
        self.assertEqual(updated_session.context_data['page'], '/meus-pedidos/')
        self.assertEqual(updated_session.context_data['user_preference'], 'dark_mode')
    
    def test_get_history_returns_empty_list_for_new_session(self):
        """Test get_history returns empty list for session with no messages"""
        # Create a new session with no messages
        session = self.manager.create_session(self.user)
        
        # Get history
        history = self.manager.get_history(session)
        
        # Verify empty list is returned
        self.assertEqual(len(history), 0)
        self.assertIsInstance(history, list)
    
    def test_multiple_message_types(self):
        """Test saving and retrieving different message types"""
        # Create a session
        session = self.manager.create_session(self.user)
        
        # Save different message types
        user_msg = self.manager.save_message(session, 'User question', 'user')
        assistant_msg = self.manager.save_message(session, 'Assistant response', 'assistant')
        system_msg = self.manager.save_message(session, 'System notification', 'system')
        
        # Verify all message types were saved correctly
        self.assertEqual(user_msg.sender_type, 'user')
        self.assertEqual(assistant_msg.sender_type, 'assistant')
        self.assertEqual(system_msg.sender_type, 'system')
        
        # Verify history contains all messages
        history = self.manager.get_history(session)
        self.assertEqual(len(history), 3)
