"""
Tests for frustration detection and escalation to human support.

Requirements: 6.3, 6.5
"""

from django.test import TestCase
from services.chat.error_handler import ChatErrorHandler
import asyncio


class TestFrustrationDetection(TestCase):
    """Test suite for frustration detection functionality."""
    
    def test_detect_frustration_with_direct_keywords(self):
        """Test detection of direct frustration keywords."""
        # Test various frustration expressions
        frustrated_messages = [
            "Estou muito frustrado com isso",
            "Isso é irritante",
            "Estou chateado com o serviço",
            "Que decepção",
        ]
        
        for message in frustrated_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_negative_feedback(self):
        """Test detection of negative feedback phrases."""
        negative_messages = [
            "Não funciona",
            "Não está funcionando",
            "Não consegui fazer isso",
            "Não entendo nada",
            "Não resolve meu problema",
        ]
        
        for message in negative_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_complaints(self):
        """Test detection of complaint keywords."""
        complaint_messages = [
            "Isso é péssimo",
            "Serviço horrível",
            "Que terrível",
            "Muito ruim",
            "O pior sistema",
        ]
        
        for message in complaint_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_giving_up(self):
        """Test detection of giving up expressions."""
        giving_up_messages = [
            "Desisto",
            "Vou desistir",
            "Já cansei disso",
            "Já tentei várias vezes",
            "Não adianta mais",
        ]
        
        for message in giving_up_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_human_request(self):
        """Test detection of requests for human support."""
        human_request_messages = [
            "Quero falar com alguém",
            "Preciso falar com uma pessoa",
            "Cadê o atendente?",
            "Quero falar com um humano",
            "Preciso de suporte humano",
            "Quero falar com o gerente",
        ]
        
        for message in human_request_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_confusion(self):
        """Test detection of confusion indicators."""
        confused_messages = [
            "Estou confuso",
            "Isso é muito complicado",
            "Muito difícil",
            "Isso é impossível",
            "Não faz sentido",
            "Estou perdido",
        ]
        
        for message in confused_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_repetition(self):
        """Test detection of repetition indicators."""
        repetition_messages = [
            "De novo isso",
            "Novamente o mesmo problema",
            "Outra vez",
            "Já disse isso",
            "Já falei sobre isso",
            "Estou repetindo",
        ]
        
        for message in repetition_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_time_complaints(self):
        """Test detection of time-related frustration."""
        time_messages = [
            "Isso demora muito",
            "Muito demorado",
            "Muito lento",
            "Estou esperando há horas",
            "Quanto tempo vai demorar?",
        ]
        
        for message in time_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_strong_emotions(self):
        """Test detection of strong negative emotions."""
        emotional_messages = [
            "Estou com raiva",
            "Que ódio",
            "Estou furioso",
            "Isso é insuportável",
            "Que absurdo",
            "Isso é ridículo",
            "Inaceitável",
        ]
        
        for message in emotional_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_excessive_punctuation(self):
        """Test detection of excessive punctuation."""
        punctuation_messages = [
            "Por que não funciona!!!",
            "O que está acontecendo???",
            "Isso é sério!!!???",
        ]
        
        for message in punctuation_messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Failed to detect frustration in: {message}"
    
    def test_detect_frustration_with_caps(self):
        """Test detection of excessive caps."""
        caps_message = "POR QUE ISSO NÃO FUNCIONA NUNCA"
        assert ChatErrorHandler.detect_frustration(caps_message) is True
    
    def test_no_frustration_in_normal_messages(self):
        """Test that normal messages don't trigger frustration detection."""
        normal_messages = [
            "Olá, como posso solicitar um serviço?",
            "Gostaria de saber mais sobre limpeza",
            "Quanto custa um encanador?",
            "Obrigado pela ajuda",
            "Entendi, vou fazer isso",
            "Perfeito, muito obrigado!",
        ]
        
        for message in normal_messages:
            assert ChatErrorHandler.detect_frustration(message) is False, \
                f"False positive frustration detection in: {message}"
    
    def test_case_insensitive_detection(self):
        """Test that detection is case-insensitive."""
        messages = [
            "FRUSTRADO",
            "Frustrado",
            "frustrado",
            "FrUsTrAdO",
        ]
        
        for message in messages:
            assert ChatErrorHandler.detect_frustration(message) is True, \
                f"Case sensitivity issue with: {message}"
    
    def test_handle_frustration_escalation_response(self):
        """Test that escalation response contains required information."""
        # Mock session object
        class MockUser:
            id = 123
        
        class MockSession:
            session_id = "test-session-123"
            user = MockUser()
        
        session = MockSession()
        message = "Estou frustrado, quero falar com alguém"
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            ChatErrorHandler.handle_frustration_escalation(session, message)
        )
        loop.close()
        
        # Verify response structure
        self.assertEqual(response['type'], 'escalation')
        self.assertIn('message', response)
        self.assertIn('actions', response)
        self.assertIn('contact_info', response)
        self.assertTrue(response['escalated'])
        
        # Verify contact information is present
        contact_info = response['contact_info']
        self.assertIn('email', contact_info)
        self.assertIn('phone', contact_info)
        self.assertIn('whatsapp', contact_info)
        self.assertIn('hours', contact_info)
        
        # Verify actions are present
        self.assertGreater(len(response['actions']), 0)
        for action in response['actions']:
            self.assertIn('label', action)
            self.assertIn('url', action)
    
    def test_escalation_message_content(self):
        """Test that escalation message is helpful and informative."""
        class MockSession:
            session_id = "test-session-456"
            user = None
        
        session = MockSession()
        message = "Não aguento mais isso"
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            ChatErrorHandler.handle_frustration_escalation(session, message)
        )
        loop.close()
        
        message_content = response['message']
        
        # Check that message contains key information
        self.assertTrue(
            'suporte' in message_content.lower() or 
            'email' in message_content.lower() or 
            '@' in message_content
        )
        self.assertTrue(
            'telefone' in message_content.lower() or 
            'phone' in message_content.lower()
        )
        
        # Check that message is empathetic
        self.assertTrue(
            any(word in message_content.lower() for word in ['entendo', 'ajudar', 'equipe'])
        )
