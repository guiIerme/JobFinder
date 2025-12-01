"""
Setup verification tests for Chat IA Assistente

Run with: python manage.py test services.chat.tests_setup
"""

from django.test import TestCase
from django.conf import settings


class ChatSetupTests(TestCase):
    """Test that chat infrastructure is properly configured."""
    
    def test_chat_config_exists(self):
        """Verify CHAT_CONFIG is defined in settings."""
        self.assertTrue(hasattr(settings, 'CHAT_CONFIG'))
        self.assertIsInstance(settings.CHAT_CONFIG, dict)
    
    def test_chat_config_keys(self):
        """Verify all required config keys are present."""
        required_keys = [
            'OPENAI_API_KEY',
            'OPENAI_MODEL',
            'MAX_HISTORY_MESSAGES',
            'SESSION_TIMEOUT_HOURS',
            'RATE_LIMIT_MESSAGES_PER_MINUTE',
            'CACHE_TTL_SECONDS',
            'MAX_CONCURRENT_SESSIONS',
            'RESPONSE_TIMEOUT_SECONDS',
            'ENABLE_ANALYTICS',
            'FALLBACK_RESPONSES',
            'MAX_MESSAGE_LENGTH',
        ]
        
        for key in required_keys:
            self.assertIn(key, settings.CHAT_CONFIG, f"Missing config key: {key}")
    
    def test_channel_layers_configured(self):
        """Verify CHANNEL_LAYERS is configured."""
        self.assertTrue(hasattr(settings, 'CHANNEL_LAYERS'))
        self.assertIn('default', settings.CHANNEL_LAYERS)
    
    def test_asgi_application_configured(self):
        """Verify ASGI application is configured."""
        self.assertTrue(hasattr(settings, 'ASGI_APPLICATION'))
        self.assertEqual(settings.ASGI_APPLICATION, 'home_services.asgi.application')
    
    def test_chat_models_importable(self):
        """Verify chat models can be imported."""
        try:
            from services.chat.models import (
                ChatSession,
                ChatMessage,
                KnowledgeBaseEntry,
                ChatAnalytics
            )
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import chat models: {e}")
    
    def test_chat_consumer_importable(self):
        """Verify chat consumer can be imported."""
        try:
            from services.chat.consumers import ChatConsumer
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import ChatConsumer: {e}")
    
    def test_chat_manager_importable(self):
        """Verify chat manager can be imported."""
        try:
            from services.chat.manager import ChatManager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import ChatManager: {e}")
    
    def test_ai_processor_importable(self):
        """Verify AI processor can be imported."""
        try:
            from services.chat.ai_processor import AIProcessor
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import AIProcessor: {e}")
    
    def test_context_manager_importable(self):
        """Verify context manager can be imported."""
        try:
            from services.chat.context_manager import ContextManager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import ContextManager: {e}")
    
    def test_knowledge_base_importable(self):
        """Verify knowledge base can be imported."""
        try:
            from services.chat.knowledge_base import KnowledgeBase
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import KnowledgeBase: {e}")
    
    def test_error_handler_importable(self):
        """Verify error handler can be imported."""
        try:
            from services.chat.error_handler import ChatErrorHandler
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import ChatErrorHandler: {e}")
