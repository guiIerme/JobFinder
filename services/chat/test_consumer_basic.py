"""
Basic tests for ChatConsumer WebSocket functionality.

This test file verifies the core WebSocket consumer implementation
for task 3: Build WebSocket consumer and connection handling.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from services.chat.consumers import ChatConsumer
from services.chat_models import ChatSession, ChatMessage
from channels.db import database_sync_to_async
import json


class ChatConsumerBasicTests(TestCase):
    """
    Test suite for ChatConsumer basic functionality.
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
    
    async def test_websocket_connection(self):
        """Test WebSocket connection establishment."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        
        # Set user in scope
        communicator.scope['user'] = self.user
        
        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected, "WebSocket should connect successfully")
        
        # Receive welcome message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')
        self.assertIn('Sophie', response['message'])
        
        # Disconnect
        await communicator.disconnect()
    
    async def test_session_initialization(self):
        """Test session initialization."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator.scope['user'] = self.user
        
        await communicator.connect()
        await communicator.receive_json_from()  # Welcome message
        
        # Send session init
        await communicator.send_json_to({
            'type': 'session_init',
            'context': {'page': 'home'}
        })
        
        # Receive session initialized response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'session_initialized')
        self.assertIn('session_id', response)
        self.assertIn('history', response)
        
        # Verify session was created in database
        session_id = response['session_id']
        session = ChatSession.objects.filter(session_id=session_id).first()
        self.assertIsNotNone(session)
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
        
        await communicator.disconnect()
    
    async def test_message_handling(self):
        """Test basic message sending and receiving."""
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
        response = await communicator.receive_json_from()
        session_id = response['session_id']
        
        # Send a message
        test_message = "Olá, preciso de ajuda"
        await communicator.send_json_to({
            'type': 'message',
            'content': test_message
        })
        
        # Receive echo of user message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'message')
        self.assertEqual(response['sender'], 'user')
        self.assertEqual(response['content'], test_message)
        
        # Receive typing indicator
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'typing_indicator')
        self.assertTrue(response['is_typing'])
        
        # Receive stop typing indicator
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'typing_indicator')
        self.assertFalse(response['is_typing'])
        
        # Receive assistant response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'message')
        self.assertEqual(response['sender'], 'assistant')
        
        # Verify messages were saved to database
        session = ChatSession.objects.get(session_id=session_id)
        messages = ChatMessage.objects.filter(session=session)
        self.assertEqual(messages.count(), 2)  # User message + assistant response
        
        await communicator.disconnect()
    
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        from django.conf import settings
        
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
        await communicator.receive_json_from()
        
        # Get rate limit
        rate_limit = settings.CHAT_CONFIG.get('RATE_LIMIT_MESSAGES_PER_MINUTE', 10)
        
        # Send messages up to rate limit
        for i in range(rate_limit):
            await communicator.send_json_to({
                'type': 'message',
                'content': f'Message {i}'
            })
            # Consume all responses
            await communicator.receive_json_from()  # User echo
            await communicator.receive_json_from()  # Typing on
            await communicator.receive_json_from()  # Typing off
            await communicator.receive_json_from()  # Assistant response
        
        # Next message should be rate limited
        await communicator.send_json_to({
            'type': 'message',
            'content': 'This should be rate limited'
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'rate_limit_error')
        self.assertIn('retry_after', response)
        
        await communicator.disconnect()
    
    async def test_empty_message_validation(self):
        """Test validation of empty messages."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator.scope['user'] = self.user
        
        await communicator.connect()
        await communicator.receive_json_from()  # Welcome message
        
        # Send empty message
        await communicator.send_json_to({
            'type': 'message',
            'content': '   '  # Only whitespace
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('vazia', response['message'].lower())
        
        await communicator.disconnect()
    
    async def test_message_length_validation(self):
        """Test validation of message length."""
        from django.conf import settings
        
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
        await communicator.receive_json_from()
        
        # Send message that's too long
        max_length = settings.CHAT_CONFIG.get('MAX_MESSAGE_LENGTH', 2000)
        long_message = 'a' * (max_length + 1)
        
        await communicator.send_json_to({
            'type': 'message',
            'content': long_message
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('longa', response['message'].lower())
        
        await communicator.disconnect()
    
    async def test_session_close(self):
        """Test session closing."""
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
        response = await communicator.receive_json_from()
        session_id = response['session_id']
        
        # Close session
        await communicator.send_json_to({
            'type': 'session_close'
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'session_closed')
        
        # Verify session is closed in database
        session = ChatSession.objects.get(session_id=session_id)
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.closed_at)
        
        await communicator.disconnect()
    
    async def test_satisfaction_rating_valid(self):
        """Test submitting a valid satisfaction rating."""
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
        response = await communicator.receive_json_from()
        session_id = response['session_id']
        
        # Submit satisfaction rating
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'rating': 5,
            'feedback': 'Excelente atendimento!'
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'satisfaction_rating_saved')
        self.assertEqual(response['rating'], 5)
        self.assertIn('Obrigado', response['message'])
        
        # Verify rating was saved to database
        @database_sync_to_async
        def get_session():
            return ChatSession.objects.get(session_id=session_id)
        
        session = await get_session()
        self.assertEqual(session.satisfaction_rating, 5)
        self.assertEqual(session.context_data.get('satisfaction_feedback'), 'Excelente atendimento!')
        
        await communicator.disconnect()
    
    async def test_satisfaction_rating_without_feedback(self):
        """Test submitting a satisfaction rating without feedback."""
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
        response = await communicator.receive_json_from()
        session_id = response['session_id']
        
        # Submit satisfaction rating without feedback
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'rating': 4
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'satisfaction_rating_saved')
        self.assertEqual(response['rating'], 4)
        
        # Verify rating was saved to database
        @database_sync_to_async
        def get_session():
            return ChatSession.objects.get(session_id=session_id)
        
        session = await get_session()
        self.assertEqual(session.satisfaction_rating, 4)
        
        await communicator.disconnect()
    
    async def test_satisfaction_rating_invalid_range(self):
        """Test submitting an invalid satisfaction rating (out of range)."""
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
        await communicator.receive_json_from()
        
        # Submit invalid rating (too high)
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'rating': 6
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('inválida', response['message'].lower())
        
        # Submit invalid rating (too low)
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'rating': 0
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('inválida', response['message'].lower())
        
        await communicator.disconnect()
    
    async def test_satisfaction_rating_missing(self):
        """Test submitting satisfaction rating without rating value."""
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
        await communicator.receive_json_from()
        
        # Submit without rating
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'feedback': 'Some feedback'
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('não fornecida', response['message'].lower())
        
        await communicator.disconnect()
    
    async def test_satisfaction_rating_no_session(self):
        """Test submitting satisfaction rating without an active session."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/chat/'
        )
        communicator.scope['user'] = self.user
        
        await communicator.connect()
        await communicator.receive_json_from()  # Welcome message
        
        # Try to submit rating without initializing session
        await communicator.send_json_to({
            'type': 'satisfaction_rating',
            'rating': 5
        })
        
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('sessão', response['message'].lower())
        
        await communicator.disconnect()
