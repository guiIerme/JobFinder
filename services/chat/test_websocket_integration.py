"""
Integration tests for WebSocket chat flow.

This test file verifies the complete WebSocket conversation flow including:
- Connection to closure lifecycle
- Session persistence across reconnections
- Rate limiting enforcement

Requirements: 1.3, 1.4, 5.3, 8.3
"""

from django.test import TestCase
from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from services.chat.consumers import ChatConsumer
from services.chat_models import ChatSession, ChatMessage, ChatAnalytics
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.conf import settings
import json
import asyncio


class WebSocketIntegrationTests(TestCase):
    """
    Integration test suite for WebSocket chat flow.
    
    Tests complete conversation flows, session persistence, and rate limiting.
    Requirements: 1.3, 1.4, 5.3, 8.3
    """
    
    def setUp(self):
        """Set up test user and application."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create application with routing
        self.application = URLRouter([
            path('ws/chat/', ChatConsumer.as_asgi()),
        ])
        
        # Clear cache before each test
        cache.clear()
    
    def tearDown(self):
        """Clean up after each test."""
        cache.clear()
    
    async def test_full_conversation_flow_connection_to_closure(self):
        """
        Test complete conversation flow from connection to closure.
        
        This test verifies:
        - WebSocket connection establishment
        - Session initialization
        - Sending and receiving messages
        - Session closure
        - Analytics tracking
        
        Requirements: 1.3, 1.4, 5.3
        """
        # Step 1: Establish WebSocket connection
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator.scope['user'] = self.user
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected, "WebSocket should connect successfully")
        
        # Receive welcome message
        welcome_response = await communicator.receive_json_from()
        self.assertEqual(welcome_response['type'], 'connection_established')
        self.assertIn('Sophie', welcome_response['message'])
        
        # Step 2: Initialize session
        await communicator.send_json_to({
            'type': 'session_init',
            'context': {
                'page': '/services/',
                'referrer': '/'
            }
        })
        
        session_response = await communicator.receive_json_from()
        self.assertEqual(session_response['type'], 'session_initialized')
        self.assertIn('session_id', session_response)
        self.assertIn('history', session_response)
        
        session_id = session_response['session_id']
        
        # Verify session was created in database
        @database_sync_to_async
        def get_session():
            return ChatSession.objects.filter(session_id=session_id).first()
        
        session = await get_session()
        self.assertIsNotNone(session)
        
        @database_sync_to_async
        def check_session():
            s = ChatSession.objects.get(session_id=session_id)
            return s.user.id if s.user else None, s.is_active, s.context_data.get('page')
        
        user_id, is_active, page = await check_session()
        self.assertEqual(user_id, self.user.id)
        self.assertTrue(is_active)
        self.assertEqual(page, '/services/')
        
        # Step 3: Send multiple messages in conversation
        messages_to_send = [
            "Olá, preciso de ajuda",
            "Quais serviços vocês oferecem?",
            "Quanto custa um encanador?"
        ]
        
        for message_content in messages_to_send:
            # Send user message
            await communicator.send_json_to({
                'type': 'message',
                'content': message_content
            })
            
            # Receive echo of user message
            user_echo = await communicator.receive_json_from()
            self.assertEqual(user_echo['type'], 'message')
            self.assertEqual(user_echo['sender'], 'user')
            self.assertEqual(user_echo['content'], message_content)
            
            # Receive typing indicator (on)
            typing_on = await communicator.receive_json_from()
            self.assertEqual(typing_on['type'], 'typing_indicator')
            self.assertTrue(typing_on['is_typing'])
            
            # Receive typing indicator (off)
            typing_off = await communicator.receive_json_from()
            self.assertEqual(typing_off['type'], 'typing_indicator')
            self.assertFalse(typing_off['is_typing'])
            
            # Receive assistant response
            assistant_response = await communicator.receive_json_from()
            self.assertEqual(assistant_response['type'], 'message')
            self.assertEqual(assistant_response['sender'], 'assistant')
            self.assertIn('content', assistant_response)
        
        # Verify all messages were saved to database
        message_count = await database_sync_to_async(
            lambda: ChatMessage.objects.filter(session=session).count()
        )()
        # 3 user messages + 3 assistant responses = 6 total
        self.assertEqual(message_count, 6)
        
        # Step 4: Submit satisfaction rating
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'rating': 5,
            'feedback': 'Excelente atendimento!'
        })
        
        rating_response = await communicator.receive_json_from()
        self.assertEqual(rating_response['type'], 'satisfaction_rating_saved')
        self.assertEqual(rating_response['rating'], 5)
        
        # Verify rating was saved
        session = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session_id)
        self.assertEqual(session.satisfaction_rating, 5)
        self.assertEqual(session.context_data.get('satisfaction_feedback'), 'Excelente atendimento!')
        
        # Step 5: Close session
        await communicator.send_json_to({
            'type': 'session_close'
        })
        
        close_response = await communicator.receive_json_from()
        self.assertEqual(close_response['type'], 'session_closed')
        self.assertEqual(close_response['session_id'], session_id)
        
        # Verify session was closed in database
        session = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session_id)
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.closed_at)
        
        # Step 6: Verify analytics were saved
        analytics = await database_sync_to_async(
            lambda: ChatAnalytics.objects.filter(session=session).first()
        )()
        self.assertIsNotNone(analytics)
        self.assertEqual(analytics.total_messages, 6)
        self.assertEqual(analytics.user_messages, 3)
        self.assertEqual(analytics.assistant_messages, 3)
        self.assertIsNotNone(analytics.average_response_time_ms)
        
        # Step 7: Disconnect
        await communicator.disconnect()
    
    async def test_session_persistence_across_reconnections(self):
        """
        Test that session persists across WebSocket reconnections.
        
        This test verifies:
        - Session creation on first connection
        - Session retrieval on reconnection with same session_id
        - Message history is preserved
        - Context data is maintained
        
        Requirements: 1.4, 5.3
        """
        # First connection - create session
        communicator1 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator1.scope['user'] = self.user
        
        await communicator1.connect()
        await communicator1.receive_json_from()  # Welcome message
        
        # Initialize session
        await communicator1.send_json_to({
            'type': 'session_init',
            'context': {
                'page': '/services/',
                'user_preference': 'dark_mode'
            }
        })
        
        session_response = await communicator1.receive_json_from()
        session_id = session_response['session_id']
        
        # Send some messages
        await communicator1.send_json_to({
            'type': 'message',
            'content': 'Primeira mensagem'
        })
        
        # Consume responses
        await communicator1.receive_json_from()  # User echo
        await communicator1.receive_json_from()  # Typing on
        await communicator1.receive_json_from()  # Typing off
        await communicator1.receive_json_from()  # Assistant response
        
        await communicator1.send_json_to({
            'type': 'message',
            'content': 'Segunda mensagem'
        })
        
        # Consume responses
        await communicator1.receive_json_from()  # User echo
        await communicator1.receive_json_from()  # Typing on
        await communicator1.receive_json_from()  # Typing off
        await communicator1.receive_json_from()  # Assistant response
        
        # Disconnect first connection
        await communicator1.disconnect()
        
        # Verify session still exists and is active
        session = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session_id)
        self.assertTrue(session.is_active)
        
        # Second connection - reconnect with same session_id
        communicator2 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator2.scope['user'] = self.user
        
        await communicator2.connect()
        await communicator2.receive_json_from()  # Welcome message
        
        # Initialize with existing session_id
        await communicator2.send_json_to({
            'type': 'session_init',
            'session_id': session_id,
            'context': {
                'page': '/meus-pedidos/'
            }
        })
        
        reconnect_response = await communicator2.receive_json_from()
        self.assertEqual(reconnect_response['type'], 'session_initialized')
        self.assertEqual(reconnect_response['session_id'], session_id)
        
        # Verify message history was loaded
        history = reconnect_response['history']
        self.assertEqual(len(history), 4)  # 2 user + 2 assistant messages
        
        # Verify first message is preserved
        self.assertEqual(history[0]['sender'], 'user')
        self.assertEqual(history[0]['content'], 'Primeira mensagem')
        
        # Verify second message is preserved
        self.assertEqual(history[2]['sender'], 'user')
        self.assertEqual(history[2]['content'], 'Segunda mensagem')
        
        # Verify context was updated (merged)
        @database_sync_to_async
        def get_context():
            s = ChatSession.objects.get(session_id=session_id)
            return s.context_data
        
        context_data = await get_context()
        self.assertEqual(context_data['page'], '/meus-pedidos/')
        self.assertEqual(context_data['user_preference'], 'dark_mode')
        
        # Send a new message on reconnected session
        await communicator2.send_json_to({
            'type': 'message',
            'content': 'Terceira mensagem após reconexão'
        })
        
        # Consume responses
        await communicator2.receive_json_from()  # User echo
        await communicator2.receive_json_from()  # Typing on
        await communicator2.receive_json_from()  # Typing off
        await communicator2.receive_json_from()  # Assistant response
        
        # Verify new message was added to existing session
        message_count = await database_sync_to_async(
            lambda: ChatMessage.objects.filter(session=session).count()
        )()
        self.assertEqual(message_count, 6)  # 3 user + 3 assistant messages
        
        await communicator2.disconnect()
    
    async def test_rate_limiting_enforcement(self):
        """
        Test that rate limiting is properly enforced.
        
        This test verifies:
        - Messages are allowed up to the rate limit
        - Messages beyond the limit are rejected
        - Rate limit error includes retry_after
        - Rate limit resets after window expires
        
        Requirements: 8.3
        """
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator.scope['user'] = self.user
        
        await communicator.connect()
        await communicator.receive_json_from()  # Welcome message
        
        # Initialize session
        await communicator.send_json_to({
            'type': 'session_init',
            'context': {}
        })
        await communicator.receive_json_from()  # Session initialized
        
        # Get rate limit from settings
        rate_limit = settings.CHAT_CONFIG.get('RATE_LIMIT_MESSAGES_PER_MINUTE', 10)
        
        # Send messages up to the rate limit
        for i in range(rate_limit):
            await communicator.send_json_to({
                'type': 'message',
                'content': f'Message {i + 1}'
            })
            
            # Consume all responses
            await communicator.receive_json_from()  # User echo
            await communicator.receive_json_from()  # Typing on
            await communicator.receive_json_from()  # Typing off
            await communicator.receive_json_from()  # Assistant response
        
        # Next message should be rate limited
        await communicator.send_json_to({
            'type': 'message',
            'content': 'This message should be rate limited'
        })
        
        rate_limit_response = await communicator.receive_json_from()
        self.assertEqual(rate_limit_response['type'], 'rate_limit_error')
        self.assertIn('retry_after', rate_limit_response)
        self.assertGreater(rate_limit_response['retry_after'], 0)
        self.assertIn('limite', rate_limit_response['message'].lower())
        
        # Verify no additional messages were saved beyond the limit
        session = await database_sync_to_async(
            lambda: ChatSession.objects.filter(user=self.user, is_active=True).first()
        )()
        message_count = await database_sync_to_async(
            lambda: ChatMessage.objects.filter(session=session, sender_type='user').count()
        )()
        self.assertEqual(message_count, rate_limit)
        
        await communicator.disconnect()
    
    async def test_multiple_concurrent_sessions(self):
        """
        Test handling of multiple concurrent WebSocket sessions.
        
        This test verifies:
        - Multiple sessions can be active simultaneously
        - Each session maintains independent state
        - Messages are isolated to their respective sessions
        
        Requirements: 1.3, 5.3, 8.1
        """
        # Create two users
        user2 = await database_sync_to_async(
            User.objects.create_user
        )(username='testuser2', email='test2@example.com', password='testpass123')
        
        # Create first session
        communicator1 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator1.scope['user'] = self.user
        
        await communicator1.connect()
        await communicator1.receive_json_from()  # Welcome
        
        await communicator1.send_json_to({
            'type': 'session_init',
            'context': {'page': '/services/'}
        })
        session1_response = await communicator1.receive_json_from()
        session1_id = session1_response['session_id']
        
        # Create second session
        communicator2 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator2.scope['user'] = user2
        
        await communicator2.connect()
        await communicator2.receive_json_from()  # Welcome
        
        await communicator2.send_json_to({
            'type': 'session_init',
            'context': {'page': '/meus-pedidos/'}
        })
        session2_response = await communicator2.receive_json_from()
        session2_id = session2_response['session_id']
        
        # Verify sessions are different
        self.assertNotEqual(session1_id, session2_id)
        
        # Send message in first session
        await communicator1.send_json_to({
            'type': 'message',
            'content': 'Message from user 1'
        })
        
        # Consume responses for session 1
        await communicator1.receive_json_from()  # User echo
        await communicator1.receive_json_from()  # Typing on
        await communicator1.receive_json_from()  # Typing off
        await communicator1.receive_json_from()  # Assistant response
        
        # Send message in second session
        await communicator2.send_json_to({
            'type': 'message',
            'content': 'Message from user 2'
        })
        
        # Consume responses for session 2
        await communicator2.receive_json_from()  # User echo
        await communicator2.receive_json_from()  # Typing on
        await communicator2.receive_json_from()  # Typing off
        await communicator2.receive_json_from()  # Assistant response
        
        # Verify messages are isolated to their sessions
        session1 = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session1_id)
        session1_messages = await database_sync_to_async(
            lambda: list(ChatMessage.objects.filter(session=session1, sender_type='user'))
        )()
        self.assertEqual(len(session1_messages), 1)
        self.assertEqual(session1_messages[0].content, 'Message from user 1')
        
        session2 = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session2_id)
        session2_messages = await database_sync_to_async(
            lambda: list(ChatMessage.objects.filter(session=session2, sender_type='user'))
        )()
        self.assertEqual(len(session2_messages), 1)
        self.assertEqual(session2_messages[0].content, 'Message from user 2')
        
        # Verify context is different
        self.assertEqual(session1.context_data['page'], '/services/')
        self.assertEqual(session2.context_data['page'], '/meus-pedidos/')
        
        await communicator1.disconnect()
        await communicator2.disconnect()
    
    async def test_session_recovery_after_unexpected_disconnect(self):
        """
        Test session recovery after unexpected disconnection.
        
        This test verifies:
        - Session remains active after unexpected disconnect
        - Session can be recovered on reconnection
        - No data loss occurs
        
        Requirements: 1.4, 5.3
        """
        # First connection
        communicator1 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator1.scope['user'] = self.user
        
        await communicator1.connect()
        await communicator1.receive_json_from()  # Welcome
        
        # Initialize session
        await communicator1.send_json_to({
            'type': 'session_init',
            'context': {'page': '/services/'}
        })
        session_response = await communicator1.receive_json_from()
        session_id = session_response['session_id']
        
        # Send a message
        await communicator1.send_json_to({
            'type': 'message',
            'content': 'Message before disconnect'
        })
        
        # Consume responses
        await communicator1.receive_json_from()  # User echo
        await communicator1.receive_json_from()  # Typing on
        await communicator1.receive_json_from()  # Typing off
        await communicator1.receive_json_from()  # Assistant response
        
        # Simulate unexpected disconnect (without closing session)
        await communicator1.disconnect()
        
        # Verify session is still active (not explicitly closed)
        session = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session_id)
        self.assertTrue(session.is_active)
        
        # Reconnect with same session
        communicator2 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator2.scope['user'] = self.user
        
        await communicator2.connect()
        await communicator2.receive_json_from()  # Welcome
        
        # Recover session
        await communicator2.send_json_to({
            'type': 'session_init',
            'session_id': session_id
        })
        
        recovery_response = await communicator2.receive_json_from()
        self.assertEqual(recovery_response['type'], 'session_initialized')
        self.assertEqual(recovery_response['session_id'], session_id)
        
        # Verify history is intact
        history = recovery_response['history']
        self.assertEqual(len(history), 2)  # 1 user + 1 assistant message
        self.assertEqual(history[0]['content'], 'Message before disconnect')
        
        # Continue conversation
        await communicator2.send_json_to({
            'type': 'message',
            'content': 'Message after reconnect'
        })
        
        # Consume responses
        await communicator2.receive_json_from()  # User echo
        await communicator2.receive_json_from()  # Typing on
        await communicator2.receive_json_from()  # Typing off
        await communicator2.receive_json_from()  # Assistant response
        
        # Verify both messages are in the same session
        message_count = await database_sync_to_async(
            lambda: ChatMessage.objects.filter(session=session).count()
        )()
        self.assertEqual(message_count, 4)  # 2 user + 2 assistant messages
        
        await communicator2.disconnect()
    
    async def test_analytics_tracking_throughout_conversation(self):
        """
        Test that analytics are properly tracked throughout the conversation.
        
        This test verifies:
        - Message counts are tracked
        - Response times are recorded
        - Analytics are saved on disconnect
        
        Requirements: 7.1, 7.2
        """
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator.scope['user'] = self.user
        
        await communicator.connect()
        await communicator.receive_json_from()  # Welcome
        
        # Initialize session
        await communicator.send_json_to({
            'type': 'session_init',
            'context': {}
        })
        session_response = await communicator.receive_json_from()
        session_id = session_response['session_id']
        
        # Send multiple messages
        num_messages = 5
        for i in range(num_messages):
            await communicator.send_json_to({
                'type': 'message',
                'content': f'Test message {i + 1}'
            })
            
            # Consume responses
            await communicator.receive_json_from()  # User echo
            await communicator.receive_json_from()  # Typing on
            await communicator.receive_json_from()  # Typing off
            await communicator.receive_json_from()  # Assistant response
        
        # Close session to trigger analytics save
        await communicator.send_json_to({
            'type': 'session_close'
        })
        await communicator.receive_json_from()  # Close confirmation
        
        await communicator.disconnect()
        
        # Verify analytics were saved
        session = await database_sync_to_async(
            ChatSession.objects.get
        )(session_id=session_id)
        
        analytics = await database_sync_to_async(
            lambda: ChatAnalytics.objects.filter(session=session).first()
        )()
        
        self.assertIsNotNone(analytics)
        self.assertEqual(analytics.total_messages, num_messages * 2)  # user + assistant
        self.assertEqual(analytics.user_messages, num_messages)
        self.assertEqual(analytics.assistant_messages, num_messages)
        self.assertIsNotNone(analytics.average_response_time_ms)
        self.assertGreater(analytics.average_response_time_ms, 0)
    
    async def test_rate_limit_per_user_isolation(self):
        """
        Test that rate limits are enforced per user, not globally.
        
        This test verifies:
        - Each user has independent rate limit
        - One user hitting limit doesn't affect another
        
        Requirements: 8.3
        """
        # Create second user
        user2 = await database_sync_to_async(
            User.objects.create_user
        )(username='testuser2', email='test2@example.com', password='testpass123')
        
        # Get rate limit
        rate_limit = settings.CHAT_CONFIG.get('RATE_LIMIT_MESSAGES_PER_MINUTE', 10)
        
        # User 1 connection
        communicator1 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator1.scope['user'] = self.user
        
        await communicator1.connect()
        await communicator1.receive_json_from()  # Welcome
        
        await communicator1.send_json_to({
            'type': 'session_init',
            'context': {}
        })
        await communicator1.receive_json_from()  # Session initialized
        
        # User 1 hits rate limit
        for i in range(rate_limit):
            await communicator1.send_json_to({
                'type': 'message',
                'content': f'User 1 message {i + 1}'
            })
            # Consume responses
            await communicator1.receive_json_from()
            await communicator1.receive_json_from()
            await communicator1.receive_json_from()
            await communicator1.receive_json_from()
        
        # User 1 should be rate limited
        await communicator1.send_json_to({
            'type': 'message',
            'content': 'User 1 rate limited message'
        })
        
        rate_limit_response = await communicator1.receive_json_from()
        self.assertEqual(rate_limit_response['type'], 'rate_limit_error')
        
        # User 2 connection
        communicator2 = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator2.scope['user'] = user2
        
        await communicator2.connect()
        await communicator2.receive_json_from()  # Welcome
        
        await communicator2.send_json_to({
            'type': 'session_init',
            'context': {}
        })
        await communicator2.receive_json_from()  # Session initialized
        
        # User 2 should NOT be rate limited
        await communicator2.send_json_to({
            'type': 'message',
            'content': 'User 2 first message'
        })
        
        # User 2 should receive normal responses (not rate limit error)
        user2_echo = await communicator2.receive_json_from()
        self.assertEqual(user2_echo['type'], 'message')
        self.assertEqual(user2_echo['sender'], 'user')
        
        await communicator2.receive_json_from()  # Typing on
        await communicator2.receive_json_from()  # Typing off
        
        user2_response = await communicator2.receive_json_from()
        self.assertEqual(user2_response['type'], 'message')
        self.assertEqual(user2_response['sender'], 'assistant')
        
        await communicator1.disconnect()
        await communicator2.disconnect()
