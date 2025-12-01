"""
Unit tests for AIProcessor

Tests cache hit/miss scenarios, fallback responses when API fails,
and intent extraction.

Requirements: 2.1, 8.2, 8.5

Run with: python manage.py test services.chat.test_ai_processor
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from django.test import TestCase
from django.conf import settings
import hashlib
import json

from services.chat.ai_processor import AIProcessor


class AIProcessorCacheTests(TestCase):
    """
    Test cache hit/miss scenarios for AIProcessor.
    
    Requirements: 8.2
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key-12345"
        self.processor = AIProcessor(self.api_key)
        
        # Sample test data
        self.test_message = "Quais serviços de limpeza vocês oferecem?"
        self.test_context = {
            'user_type': 'client',
            'current_page': '/services/',
            'user_id': 1
        }
        self.test_history = []
        
        # Expected cached response
        self.cached_response = {
            'content': 'Oferecemos serviços de limpeza residencial, comercial e pós-obra.',
            'intent': 'service_inquiry',
            'cached': True
        }
    
    def _generate_message_hash(self, message):
        """Helper to generate message hash."""
        return hashlib.md5(message.encode('utf-8')).hexdigest()
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_cache_hit_returns_cached_response(self, mock_check_cache):
        """
        Test that when cache hit occurs, cached response is returned.
        
        Validates: Requirements 8.2 - Cache usage for frequent responses
        """
        # Arrange
        message_hash = self._generate_message_hash(self.test_message)
        mock_check_cache.return_value = self.cached_response
        
        # Act
        result = await self.processor.process_message(
            self.test_message,
            self.test_context,
            self.test_history
        )
        
        # Assert
        mock_check_cache.assert_called_once()
        self.assertEqual(result, self.cached_response)
        self.assertTrue(result.get('cached', False))
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    @patch('services.chat.ai_processor.AIProcessor.save_to_cache')
    @patch('services.chat.ai_processor.AIProcessor._generate_ai_response')
    async def test_cache_miss_generates_and_caches_response(
        self, 
        mock_generate_ai,
        mock_save_to_cache, 
        mock_check_cache
    ):
        """
        Test that when cache miss occurs, new response is generated and cached.
        
        Validates: Requirements 8.2 - Cache miss handling
        """
        # Arrange
        mock_check_cache.return_value = None
        new_response = {
            'content': 'Nova resposta gerada',
            'intent': 'service_inquiry',
            'cached': False
        }
        mock_generate_ai.return_value = new_response
        
        # Act
        result = await self.processor.process_message(
            self.test_message,
            self.test_context,
            self.test_history
        )
        
        # Assert
        mock_check_cache.assert_called_once()
        mock_save_to_cache.assert_called_once()
        self.assertFalse(result.get('cached', True))
    
    def test_check_cache_with_valid_hash(self):
        """
        Test cache lookup with valid message hash.
        
        Validates: Requirements 8.2 - Cache retrieval
        """
        # Arrange
        message_hash = self._generate_message_hash(self.test_message)
        
        with patch('django.core.cache.cache.get') as mock_cache_get:
            mock_cache_get.return_value = json.dumps(self.cached_response)
            
            # Act
            result = self.processor.check_cache(message_hash)
            
            # Assert
            mock_cache_get.assert_called_once_with(f'chat_response:{message_hash}')
            self.assertIsNotNone(result)
    
    def test_check_cache_with_invalid_hash_returns_none(self):
        """
        Test cache lookup with non-existent hash returns None.
        
        Validates: Requirements 8.2 - Cache miss handling
        """
        # Arrange
        invalid_hash = "nonexistent_hash_12345"
        
        with patch('django.core.cache.cache.get') as mock_cache_get:
            mock_cache_get.return_value = None
            
            # Act
            result = self.processor.check_cache(invalid_hash)
            
            # Assert
            mock_cache_get.assert_called_once_with(f'chat_response:{invalid_hash}')
            self.assertIsNone(result)
    
    def test_save_to_cache_stores_response(self):
        """
        Test that responses are properly saved to cache.
        
        Validates: Requirements 8.2 - Cache storage
        """
        # Arrange
        message_hash = self._generate_message_hash(self.test_message)
        response = {'content': 'Test response', 'intent': 'general'}
        
        with patch('django.core.cache.cache.set') as mock_cache_set:
            # Act
            self.processor.save_to_cache(message_hash, response)
            
            # Assert
            mock_cache_set.assert_called_once()
            call_args = mock_cache_set.call_args
            self.assertEqual(call_args[0][0], f'chat_response:{message_hash}')
            # Verify TTL is set (should be from CHAT_CONFIG)
            self.assertIsNotNone(call_args[0][2])
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_cache_hit_avoids_api_call(self, mock_check_cache):
        """
        Test that cache hit prevents unnecessary API calls.
        
        Validates: Requirements 8.2 - Reducing API calls through caching
        """
        # Arrange
        mock_check_cache.return_value = self.cached_response
        
        with patch('openai.ChatCompletion.create') as mock_openai:
            # Act
            result = await self.processor.process_message(
                self.test_message,
                self.test_context,
                self.test_history
            )
            
            # Assert
            mock_check_cache.assert_called_once()
            mock_openai.assert_not_called()  # API should not be called
            self.assertTrue(result.get('cached', False))


class AIProcessorFallbackTests(TestCase):
    """
    Test fallback responses when OpenAI API fails.
    
    Requirements: 8.5
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key-12345"
        self.processor = AIProcessor(self.api_key)
        
        self.test_message = "Como solicitar um serviço?"
        self.test_context = {'user_type': 'client'}
        self.test_history = []
    
    @patch('openai.ChatCompletion.create')
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_api_failure_returns_fallback_response(
        self, 
        mock_check_cache, 
        mock_openai
    ):
        """
        Test that API failure triggers fallback response.
        
        Validates: Requirements 8.5 - Fallback for API unavailability
        """
        # Arrange
        mock_check_cache.return_value = None
        mock_openai.side_effect = Exception("API connection failed")
        
        # Act
        result = await self.processor.process_message(
            self.test_message,
            self.test_context,
            self.test_history
        )
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('fallback', result.get('type', '').lower())
        self.assertIn('content', result)
    
    @patch('openai.ChatCompletion.create')
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_timeout_error_returns_fallback(
        self, 
        mock_check_cache, 
        mock_openai
    ):
        """
        Test that timeout errors trigger fallback response.
        
        Validates: Requirements 8.5 - Handling timeout scenarios
        """
        # Arrange
        mock_check_cache.return_value = None
        mock_openai.side_effect = TimeoutError("Request timed out")
        
        # Act
        result = await self.processor.process_message(
            self.test_message,
            self.test_context,
            self.test_history
        )
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('content', result)
    
    @patch('openai.ChatCompletion.create')
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_rate_limit_error_returns_fallback(
        self, 
        mock_check_cache, 
        mock_openai
    ):
        """
        Test that rate limit errors trigger fallback response.
        
        Validates: Requirements 8.5 - Handling rate limit scenarios
        """
        # Arrange
        mock_check_cache.return_value = None
        mock_openai.side_effect = Exception("Rate limit exceeded")
        
        # Act
        result = await self.processor.process_message(
            self.test_message,
            self.test_context,
            self.test_history
        )
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('content', result)
    
    def test_fallback_response_contains_helpful_actions(self):
        """
        Test that fallback responses include helpful action buttons.
        
        Validates: Requirements 6.2 - Alternative options when AI cannot help
        """
        # Arrange
        intent = 'service_inquiry'
        
        # Act
        fallback = self.processor._get_fallback_response(intent)
        
        # Assert
        self.assertIn('content', fallback)
        self.assertIn('actions', fallback)
        self.assertIsInstance(fallback['actions'], list)
        self.assertGreater(len(fallback['actions']), 0)
    
    def test_fallback_response_varies_by_intent(self):
        """
        Test that fallback responses are customized based on intent.
        
        Validates: Requirements 2.1 - Context-aware responses
        """
        # Arrange
        intents = ['service_inquiry', 'navigation_help', 'provider_questions']
        
        # Act & Assert
        responses = [self.processor._get_fallback_response(intent) for intent in intents]
        
        # Verify responses are different
        contents = [r['content'] for r in responses]
        self.assertEqual(len(set(contents)), len(intents))
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_fallback_response_not_cached(self, mock_check_cache):
        """
        Test that fallback responses are not cached.
        
        Validates: Requirements 8.2 - Only cache successful AI responses
        """
        # Arrange
        mock_check_cache.return_value = None
        
        with patch('openai.ChatCompletion.create') as mock_openai:
            mock_openai.side_effect = Exception("API failed")
            
            with patch.object(
                self.processor, 
                'save_to_cache'
            ) as mock_save_cache:
                # Act
                result = await self.processor.process_message(
                    self.test_message,
                    self.test_context,
                    self.test_history
                )
                
                # Assert
                mock_save_cache.assert_not_called()


class AIProcessorIntentExtractionTests(TestCase):
    """
    Test intent extraction from user messages.
    
    Requirements: 2.1
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key-12345"
        self.processor = AIProcessor(self.api_key)
    
    def test_extract_service_inquiry_intent(self):
        """
        Test extraction of service inquiry intent.
        
        Validates: Requirements 2.1 - Understanding service questions
        """
        # Arrange
        messages = [
            "Quais serviços de limpeza vocês oferecem?",
            "Quanto custa um encanador?",
            "Preciso de um eletricista urgente",
            "Vocês fazem pintura residencial?",
            "Qual o preço do serviço de jardinagem?"
        ]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertEqual(
                intent, 
                'service_inquiry',
                f"Failed to extract service_inquiry from: {message}"
            )
    
    def test_extract_navigation_help_intent(self):
        """
        Test extraction of navigation help intent.
        
        Validates: Requirements 3.1 - Providing navigation assistance
        """
        # Arrange
        messages = [
            "Como faço para solicitar um serviço?",
            "Onde vejo meus pedidos?",
            "Como atualizo meu perfil?",
            "Onde fica a página inicial?",
            "Como faço login?"
        ]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertEqual(
                intent, 
                'navigation_help',
                f"Failed to extract navigation_help from: {message}"
            )
    
    def test_extract_provider_questions_intent(self):
        """
        Test extraction of provider-specific questions intent.
        
        Validates: Requirements 4.1 - Identifying provider users
        """
        # Arrange
        messages = [
            "Como aceito uma solicitação?",
            "Onde vejo meus pagamentos?",
            "Como atualizo minha disponibilidade?",
            "Como gerencio minhas solicitações?",
            "Onde configuro meu perfil profissional?"
        ]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertEqual(
                intent, 
                'provider_questions',
                f"Failed to extract provider_questions from: {message}"
            )
    
    def test_extract_general_intent(self):
        """
        Test extraction of general conversation intent.
        
        Validates: Requirements 2.1 - Handling general queries
        """
        # Arrange
        messages = [
            "Olá",
            "Oi, tudo bem?",
            "Obrigado",
            "Tchau",
            "Pode me ajudar?"
        ]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertEqual(
                intent, 
                'general',
                f"Failed to extract general from: {message}"
            )
    
    def test_extract_complaint_intent(self):
        """
        Test extraction of complaint/problem intent.
        
        Validates: Requirements 6.3 - Detecting user frustration
        """
        # Arrange
        messages = [
            "Não está funcionando",
            "Isso não funciona",
            "Estou com problema",
            "Não consigo fazer nada",
            "Isso é péssimo"
        ]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertIn(
                intent, 
                ['complaint', 'general'],
                f"Failed to extract complaint from: {message}"
            )
    
    def test_extract_intent_case_insensitive(self):
        """
        Test that intent extraction is case-insensitive.
        
        Validates: Requirements 2.3 - Natural language understanding
        """
        # Arrange
        messages = [
            "QUAIS SERVIÇOS VOCÊS OFERECEM?",
            "quais serviços vocês oferecem?",
            "Quais Serviços Vocês Oferecem?"
        ]
        
        # Act & Assert
        intents = [self.processor.extract_intent(msg) for msg in messages]
        
        # All should extract the same intent
        self.assertEqual(len(set(intents)), 1)
        self.assertEqual(intents[0], 'service_inquiry')
    
    def test_extract_intent_with_typos(self):
        """
        Test intent extraction handles common typos gracefully.
        
        Validates: Requirements 2.3 - Robust natural language processing
        """
        # Arrange
        messages = [
            "Quais servicos voces oferecem?",  # Missing accents
            "Quanto custa um encanador",  # Missing question mark
            "preciso de eletricista",  # Missing article
        ]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertEqual(intent, 'service_inquiry')
    
    def test_extract_intent_from_empty_message(self):
        """
        Test intent extraction from empty message returns general.
        
        Validates: Requirements 2.1 - Handling edge cases
        """
        # Arrange
        messages = ["", "   ", "\n", "\t"]
        
        # Act & Assert
        for message in messages:
            intent = self.processor.extract_intent(message)
            self.assertEqual(intent, 'general')
    
    def test_extract_intent_with_multiple_intents(self):
        """
        Test that messages with multiple intents return primary intent.
        
        Validates: Requirements 2.1 - Intent prioritization
        """
        # Arrange
        message = "Quais serviços vocês oferecem e como faço para solicitar?"
        
        # Act
        intent = self.processor.extract_intent(message)
        
        # Assert - Should prioritize navigation_help (more specific phrase "como faço")
        # over service_inquiry (general keyword "serviços")
        self.assertEqual(intent, 'navigation_help')
    
    def test_extract_intent_with_context_keywords(self):
        """
        Test intent extraction uses context keywords effectively.
        
        Validates: Requirements 2.1 - Keyword-based intent detection
        """
        # Test service-related keywords
        service_keywords = ['serviço', 'preço', 'custo', 'valor', 'profissional']
        for keyword in service_keywords:
            message = f"Preciso saber sobre {keyword}"
            intent = self.processor.extract_intent(message)
            self.assertEqual(intent, 'service_inquiry')
        
        # Test navigation-related keywords
        nav_keywords = ['como', 'onde', 'página', 'acessar', 'encontrar']
        for keyword in nav_keywords:
            message = f"{keyword} faço isso?"
            intent = self.processor.extract_intent(message)
            self.assertEqual(intent, 'navigation_help')


class AIProcessorIntegrationTests(TestCase):
    """
    Integration tests for AIProcessor combining multiple features.
    
    Requirements: 2.1, 8.2, 8.5
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key-12345"
        self.processor = AIProcessor(self.api_key)
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    @patch('openai.ChatCompletion.create')
    async def test_full_processing_flow_with_cache_miss(
        self, 
        mock_openai, 
        mock_check_cache
    ):
        """
        Test complete message processing flow with cache miss.
        
        Validates: Requirements 2.1, 8.2 - Full processing pipeline
        """
        # Arrange
        mock_check_cache.return_value = None
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'Oferecemos diversos serviços de limpeza.'
                }
            }]
        }
        
        message = "Quais serviços de limpeza vocês oferecem?"
        context = {'user_type': 'client'}
        history = []
        
        with patch.object(self.processor, 'save_to_cache'):
            # Act
            result = await self.processor.process_message(message, context, history)
            
            # Assert
            self.assertIsNotNone(result)
            self.assertIn('content', result)
            mock_check_cache.assert_called_once()
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    async def test_full_processing_flow_with_cache_hit(self, mock_check_cache):
        """
        Test complete message processing flow with cache hit.
        
        Validates: Requirements 8.2 - Cache optimization
        """
        # Arrange
        cached_response = {
            'content': 'Cached response',
            'intent': 'service_inquiry',
            'cached': True
        }
        mock_check_cache.return_value = cached_response
        
        message = "Quais serviços vocês oferecem?"
        context = {'user_type': 'client'}
        history = []
        
        # Act
        result = await self.processor.process_message(message, context, history)
        
        # Assert
        self.assertEqual(result, cached_response)
        self.assertTrue(result['cached'])
    
    @patch('services.chat.ai_processor.AIProcessor.check_cache')
    @patch('openai.ChatCompletion.create')
    async def test_full_processing_flow_with_api_failure(
        self, 
        mock_openai, 
        mock_check_cache
    ):
        """
        Test complete message processing flow with API failure and fallback.
        
        Validates: Requirements 8.5 - Fallback handling
        """
        # Arrange
        mock_check_cache.return_value = None
        mock_openai.side_effect = Exception("API unavailable")
        
        message = "Como solicitar um serviço?"
        context = {'user_type': 'client'}
        history = []
        
        # Act
        result = await self.processor.process_message(message, context, history)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIn('content', result)
        # Fallback should not be cached
        mock_check_cache.assert_called_once()


if __name__ == '__main__':
    unittest.main()
