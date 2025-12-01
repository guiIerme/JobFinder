"""
Unit tests for Chat Security

Tests the security validation and sanitization functions.

Requirements: 8.3 (Security)
"""

import unittest
from django.test import TestCase, override_settings
from services.chat.security import ChatSecurityValidator


class ChatSecurityValidatorTests(TestCase):
    """
    Test suite for ChatSecurityValidator.
    
    Tests input validation, sanitization, and security checks.
    """
    
    def test_validate_message_content_valid(self):
        """Test validation of valid message content"""
        content = "Olá, preciso de ajuda com um serviço"
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_message_content_empty(self):
        """Test validation rejects empty messages"""
        content = ""
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("vazia", error.lower())
    
    def test_validate_message_content_whitespace_only(self):
        """Test validation rejects whitespace-only messages"""
        content = "   \n\t  "
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_message_content_too_long(self):
        """Test validation rejects oversized messages"""
        content = "A" * 3000  # Exceeds default 2000 char limit
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("longa", error.lower())
    
    def test_validate_message_content_xss_script_tag(self):
        """Test validation blocks script tags (XSS)"""
        content = "<script>alert('XSS')</script>"
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("não permitidos", error.lower())
    
    def test_validate_message_content_xss_javascript_protocol(self):
        """Test validation blocks javascript: protocol"""
        content = "Click here: javascript:alert('XSS')"
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_message_content_xss_event_handler(self):
        """Test validation blocks event handlers"""
        content = '<img src="x" onerror="alert(\'XSS\')">'
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_message_content_xss_iframe(self):
        """Test validation blocks iframe tags"""
        content = '<iframe src="https://malicious.com"></iframe>'
        is_valid, error = ChatSecurityValidator.validate_message_content(content)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_sanitize_message_content(self):
        """Test message content sanitization"""
        content = "<b>Hello</b> & goodbye"
        sanitized = ChatSecurityValidator.sanitize_message_content(content)
        
        # Should HTML escape
        self.assertIn("&lt;b&gt;", sanitized)
        self.assertIn("&amp;", sanitized)
        self.assertNotIn("<b>", sanitized)
    
    def test_sanitize_message_content_whitespace(self):
        """Test sanitization trims whitespace"""
        content = "  Hello World  \n"
        sanitized = ChatSecurityValidator.sanitize_message_content(content)
        
        self.assertEqual(sanitized, "Hello World")
    
    def test_validate_message_type_valid(self):
        """Test validation of valid message types"""
        is_valid, error = ChatSecurityValidator.validate_message_type('text')
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        is_valid, error = ChatSecurityValidator.validate_message_type('system')
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_message_type_invalid(self):
        """Test validation rejects invalid message types"""
        is_valid, error = ChatSecurityValidator.validate_message_type('malicious')
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("não permitido", error.lower())
    
    def test_validate_session_id_valid(self):
        """Test validation of valid UUID session IDs"""
        session_id = "550e8400-e29b-41d4-a716-446655440000"
        is_valid, error = ChatSecurityValidator.validate_session_id(session_id)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_session_id_invalid_format(self):
        """Test validation rejects invalid UUID format"""
        session_id = "not-a-valid-uuid"
        is_valid, error = ChatSecurityValidator.validate_session_id(session_id)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("inválido", error.lower())
    
    def test_validate_session_id_empty(self):
        """Test validation rejects empty session ID"""
        session_id = ""
        is_valid, error = ChatSecurityValidator.validate_session_id(session_id)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_rating_valid(self):
        """Test validation of valid ratings"""
        for rating in [1, 2, 3, 4, 5]:
            is_valid, error, normalized = ChatSecurityValidator.validate_rating(rating)
            self.assertTrue(is_valid, f"Rating {rating} should be valid")
            self.assertIsNone(error)
            self.assertEqual(normalized, rating)
    
    def test_validate_rating_string_number(self):
        """Test validation accepts string numbers"""
        is_valid, error, normalized = ChatSecurityValidator.validate_rating("3")
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(normalized, 3)
    
    def test_validate_rating_out_of_range(self):
        """Test validation rejects out-of-range ratings"""
        for rating in [0, 6, 10, -1]:
            is_valid, error, normalized = ChatSecurityValidator.validate_rating(rating)
            self.assertFalse(is_valid, f"Rating {rating} should be invalid")
            self.assertIsNotNone(error)
            self.assertIsNone(normalized)
    
    def test_validate_rating_invalid_type(self):
        """Test validation rejects non-numeric ratings"""
        is_valid, error, normalized = ChatSecurityValidator.validate_rating("abc")
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIsNone(normalized)
    
    def test_validate_rating_none(self):
        """Test validation rejects None rating"""
        is_valid, error, normalized = ChatSecurityValidator.validate_rating(None)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIsNone(normalized)
    
    def test_validate_feedback_valid(self):
        """Test validation of valid feedback"""
        feedback = "O atendimento foi excelente!"
        is_valid, error = ChatSecurityValidator.validate_feedback(feedback)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_feedback_empty(self):
        """Test validation allows empty feedback"""
        feedback = ""
        is_valid, error = ChatSecurityValidator.validate_feedback(feedback)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_feedback_too_long(self):
        """Test validation rejects oversized feedback"""
        feedback = "A" * 1500  # Exceeds 1000 char limit
        is_valid, error = ChatSecurityValidator.validate_feedback(feedback)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("longo", error.lower())
    
    def test_validate_feedback_xss(self):
        """Test validation blocks XSS in feedback"""
        feedback = "<script>alert('XSS')</script>"
        is_valid, error = ChatSecurityValidator.validate_feedback(feedback)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_sanitize_feedback(self):
        """Test feedback sanitization"""
        feedback = "<b>Great service!</b> & fast"
        sanitized = ChatSecurityValidator.sanitize_feedback(feedback)
        
        # Should HTML escape
        self.assertIn("&lt;b&gt;", sanitized)
        self.assertIn("&amp;", sanitized)
        self.assertNotIn("<b>", sanitized)
    
    def test_validate_context_data_valid(self):
        """Test validation of valid context data"""
        context = {
            'page': 'home',
            'referrer': 'google',
            'user_type': 'client'
        }
        is_valid, error = ChatSecurityValidator.validate_context_data(context)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_context_data_none(self):
        """Test validation allows None context"""
        is_valid, error = ChatSecurityValidator.validate_context_data(None)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_context_data_empty_dict(self):
        """Test validation allows empty dict"""
        is_valid, error = ChatSecurityValidator.validate_context_data({})
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_context_data_invalid_type(self):
        """Test validation rejects non-dict context"""
        is_valid, error = ChatSecurityValidator.validate_context_data("not a dict")
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("objeto", error.lower())
    
    def test_validate_context_data_too_large(self):
        """Test validation rejects oversized context"""
        # Create a large context (>10KB)
        context = {'data': 'A' * 15000}
        is_valid, error = ChatSecurityValidator.validate_context_data(context)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        self.assertIn("grandes", error.lower())
    
    def test_check_origin_valid(self):
        """Test origin checking with valid origin"""
        origin = "http://localhost:8000"
        allowed = ["http://localhost:8000", "http://localhost:3000"]
        
        is_allowed = ChatSecurityValidator.check_origin(origin, allowed)
        self.assertTrue(is_allowed)
    
    def test_check_origin_invalid(self):
        """Test origin checking rejects unauthorized origin"""
        origin = "https://malicious.com"
        allowed = ["http://localhost:8000", "http://localhost:3000"]
        
        is_allowed = ChatSecurityValidator.check_origin(origin, allowed)
        self.assertFalse(is_allowed)
    
    def test_check_origin_no_origin(self):
        """Test origin checking rejects missing origin"""
        origin = None
        allowed = ["http://localhost:8000"]
        
        is_allowed = ChatSecurityValidator.check_origin(origin, allowed)
        self.assertFalse(is_allowed)
    
    def test_check_origin_wildcard(self):
        """Test origin checking with wildcard"""
        origin = "https://anything.com"
        allowed = ["*"]
        
        is_allowed = ChatSecurityValidator.check_origin(origin, allowed)
        self.assertTrue(is_allowed)
    
    def test_check_origin_subdomain_pattern(self):
        """Test origin checking with subdomain pattern"""
        origin = "https://api.example.com"
        allowed = ["*.example.com"]
        
        is_allowed = ChatSecurityValidator.check_origin(origin, allowed)
        self.assertTrue(is_allowed)


if __name__ == '__main__':
    unittest.main()
