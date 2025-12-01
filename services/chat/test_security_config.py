"""
Security Configuration Tests for Chat IA Assistente

Tests to validate security configurations including CORS, message size limits,
and input validation rules.

Requirements: 8.3 (Security)
"""

import json
from django.test import TestCase, override_settings
from django.conf import settings
from services.chat.security import (
    ChatSecurityValidator,
    ConnectionTracker,
    WebSocketSecurityMiddleware
)


class SecurityConfigurationTests(TestCase):
    """
    Test suite for security configuration validation.
    
    Requirements: 8.3
    """
    
    def test_cors_configuration_exists(self):
        """Test that CORS configuration is properly set"""
        # Check that ALLOWED_WEBSOCKET_ORIGINS is configured
        self.assertTrue(hasattr(settings, 'ALLOWED_WEBSOCKET_ORIGINS'))
        self.assertIsInstance(settings.ALLOWED_WEBSOCKET_ORIGINS, list)
        self.assertGreater(len(settings.ALLOWED_WEBSOCKET_ORIGINS), 0)
        
        # Check that WEBSOCKET_CORS_ALLOWED_HEADERS is configured
        self.assertTrue(hasattr(settings, 'WEBSOCKET_CORS_ALLOWED_HEADERS'))
        self.assertIsInstance(settings.WEBSOCKET_CORS_ALLOWED_HEADERS, list)
        
        # Verify essential headers are included
        required_headers = ['origin', 'authorization', 'content-type']
        for header in required_headers:
            self.assertIn(
                header,
                settings.WEBSOCKET_CORS_ALLOWED_HEADERS,
                f"Required header '{header}' not in WEBSOCKET_CORS_ALLOWED_HEADERS"
            )
    
    def test_message_size_limits_configured(self):
        """Test that message size limits are properly configured"""
        # Check WEBSOCKET_SECURITY configuration
        self.assertTrue(hasattr(settings, 'WEBSOCKET_SECURITY'))
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify message size limits
        self.assertIn('MAX_MESSAGE_SIZE', ws_security)
        self.assertIn('MAX_FRAME_SIZE', ws_security)
        self.assertIn('ENFORCE_MESSAGE_SIZE', ws_security)
        
        # Verify reasonable limits
        self.assertGreater(ws_security['MAX_MESSAGE_SIZE'], 0)
        self.assertLessEqual(ws_security['MAX_MESSAGE_SIZE'], 10000)  # Not too large
        
        self.assertGreater(ws_security['MAX_FRAME_SIZE'], 0)
        self.assertLessEqual(ws_security['MAX_FRAME_SIZE'], 1048576)  # Max 1MB
        
        # Verify enforcement is enabled
        self.assertTrue(ws_security['ENFORCE_MESSAGE_SIZE'])
    
    def test_input_validation_rules_configured(self):
        """Test that input validation rules are properly configured"""
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify validation flags
        validation_flags = [
            'VALIDATE_JSON',
            'VALIDATE_MESSAGE_TYPE',
            'VALIDATE_CONTENT',
            'BLOCK_DANGEROUS_PATTERNS',
            'SANITIZE_INPUT',
        ]
        
        for flag in validation_flags:
            self.assertIn(flag, ws_security, f"Validation flag '{flag}' not configured")
            self.assertTrue(
                ws_security[flag],
                f"Validation flag '{flag}' should be enabled"
            )
    
    def test_connection_limits_configured(self):
        """Test that connection limits are properly configured"""
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify connection limit settings
        self.assertIn('MAX_CONNECTIONS_PER_USER', ws_security)
        self.assertIn('MAX_CONNECTIONS_PER_IP', ws_security)
        self.assertIn('TRACK_CONNECTIONS', ws_security)
        
        # Verify reasonable limits
        self.assertGreater(ws_security['MAX_CONNECTIONS_PER_USER'], 0)
        self.assertLessEqual(ws_security['MAX_CONNECTIONS_PER_USER'], 20)
        
        self.assertGreater(ws_security['MAX_CONNECTIONS_PER_IP'], 0)
        self.assertLessEqual(ws_security['MAX_CONNECTIONS_PER_IP'], 50)
        
        # Verify tracking is enabled
        self.assertTrue(ws_security['TRACK_CONNECTIONS'])
    
    def test_rate_limiting_configured(self):
        """Test that rate limiting is properly configured"""
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify rate limiting settings
        self.assertIn('ENABLE_RATE_LIMITING', ws_security)
        self.assertIn('RATE_LIMIT_MESSAGES_PER_MINUTE', ws_security)
        self.assertIn('RATE_LIMIT_WINDOW_SECONDS', ws_security)
        
        # Verify rate limiting is enabled
        self.assertTrue(ws_security['ENABLE_RATE_LIMITING'])
        
        # Verify reasonable limits
        self.assertGreater(ws_security['RATE_LIMIT_MESSAGES_PER_MINUTE'], 0)
        self.assertLessEqual(ws_security['RATE_LIMIT_MESSAGES_PER_MINUTE'], 100)
    
    def test_timeout_settings_configured(self):
        """Test that timeout settings are properly configured"""
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify timeout settings
        timeout_settings = [
            'CONNECTION_TIMEOUT',
            'PING_INTERVAL',
            'PING_TIMEOUT',
            'IDLE_TIMEOUT',
        ]
        
        for setting in timeout_settings:
            self.assertIn(setting, ws_security, f"Timeout setting '{setting}' not configured")
            self.assertGreater(
                ws_security[setting],
                0,
                f"Timeout setting '{setting}' must be positive"
            )
    
    def test_logging_configured(self):
        """Test that security logging is properly configured"""
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify logging flags
        logging_flags = [
            'LOG_SECURITY_EVENTS',
            'LOG_REJECTED_CONNECTIONS',
            'LOG_VALIDATION_FAILURES',
        ]
        
        for flag in logging_flags:
            self.assertIn(flag, ws_security, f"Logging flag '{flag}' not configured")
            # Logging should be enabled for security monitoring
            self.assertTrue(
                ws_security[flag],
                f"Logging flag '{flag}' should be enabled for security"
            )
    
    def test_origin_validation_configured(self):
        """Test that origin validation is properly configured"""
        ws_security = settings.WEBSOCKET_SECURITY
        
        # Verify origin validation settings
        self.assertIn('ENFORCE_ORIGIN_CHECK', ws_security)
        self.assertIn('ALLOW_WILDCARD_ORIGIN', ws_security)
        self.assertIn('ALLOWED_ORIGINS', ws_security)
        
        # Verify origin checking is enforced
        self.assertTrue(ws_security['ENFORCE_ORIGIN_CHECK'])
        
        # Verify wildcard is disabled (security best practice)
        # Note: May be True in development, but should be False in production
        if not settings.DEBUG:
            self.assertFalse(
                ws_security['ALLOW_WILDCARD_ORIGIN'],
                "Wildcard origin should be disabled in production"
            )
    
    def test_chat_config_security_settings(self):
        """Test that CHAT_CONFIG has security settings"""
        chat_config = settings.CHAT_CONFIG
        
        # Verify security-related settings in CHAT_CONFIG
        security_settings = [
            'MAX_MESSAGE_LENGTH',
            'SANITIZE_INPUT',
            'VALIDATE_SESSION',
            'VALIDATE_ORIGIN',
            'BLOCK_DANGEROUS_PATTERNS',
            'HTML_ESCAPE_MESSAGES',
        ]
        
        for setting in security_settings:
            self.assertIn(
                setting,
                chat_config,
                f"Security setting '{setting}' not in CHAT_CONFIG"
            )
        
        # Verify security features are enabled
        self.assertTrue(chat_config['SANITIZE_INPUT'])
        self.assertTrue(chat_config['VALIDATE_SESSION'])
        self.assertTrue(chat_config['BLOCK_DANGEROUS_PATTERNS'])
        self.assertTrue(chat_config['HTML_ESCAPE_MESSAGES'])


class MessageSizeLimitTests(TestCase):
    """
    Test suite for message size limit enforcement.
    
    Requirements: 8.3 - Set message size limits
    """
    
    def test_message_content_size_limit(self):
        """Test that message content size is enforced"""
        max_size = settings.CHAT_CONFIG.get('MAX_MESSAGE_LENGTH', 2000)
        
        # Valid message (within limit)
        valid_message = 'A' * (max_size - 1)
        is_valid, error = ChatSecurityValidator.validate_message_content(valid_message)
        self.assertTrue(is_valid, f"Valid message rejected: {error}")
        
        # Invalid message (exceeds limit)
        invalid_message = 'A' * (max_size + 1)
        is_valid, error = ChatSecurityValidator.validate_message_content(invalid_message)
        self.assertFalse(is_valid, "Oversized message not rejected")
        self.assertIn('muito longa', error.lower())
    
    def test_websocket_frame_size_limit(self):
        """Test that WebSocket frame size is validated"""
        max_frame_size = settings.WEBSOCKET_SECURITY.get('MAX_FRAME_SIZE', 65536)
        
        # Valid frame (within limit)
        valid_data = 'A' * (max_frame_size - 100)  # Leave room for JSON overhead
        is_valid, error = ChatSecurityValidator.validate_websocket_frame_size(valid_data)
        self.assertTrue(is_valid, f"Valid frame rejected: {error}")
        
        # Invalid frame (exceeds limit)
        invalid_data = 'A' * (max_frame_size + 1)
        is_valid, error = ChatSecurityValidator.validate_websocket_frame_size(invalid_data)
        self.assertFalse(is_valid, "Oversized frame not rejected")
        self.assertIn('muito grande', error.lower())
    
    def test_feedback_size_limit(self):
        """Test that feedback text size is enforced"""
        max_feedback = settings.WEBSOCKET_SECURITY.get('MAX_FEEDBACK_LENGTH', 1000)
        
        # Valid feedback (within limit)
        valid_feedback = 'A' * (max_feedback - 1)
        is_valid, error = ChatSecurityValidator.validate_feedback(valid_feedback)
        self.assertTrue(is_valid, f"Valid feedback rejected: {error}")
        
        # Invalid feedback (exceeds limit)
        invalid_feedback = 'A' * (max_feedback + 1)
        is_valid, error = ChatSecurityValidator.validate_feedback(invalid_feedback)
        self.assertFalse(is_valid, "Oversized feedback not rejected")
        self.assertIn('muito longo', error.lower())
    
    def test_context_data_size_limit(self):
        """Test that context data size is enforced"""
        max_context_size = settings.CHAT_CONFIG.get('MAX_CONTEXT_SIZE_BYTES', 10000)
        
        # Valid context (within limit)
        valid_context = {'key': 'A' * 100}
        is_valid, error = ChatSecurityValidator.validate_context_data(valid_context)
        self.assertTrue(is_valid, f"Valid context rejected: {error}")
        
        # Invalid context (exceeds limit)
        # Create a large context that exceeds the limit
        large_value = 'A' * (max_context_size + 1000)
        invalid_context = {'key': large_value}
        is_valid, error = ChatSecurityValidator.validate_context_data(invalid_context)
        self.assertFalse(is_valid, "Oversized context not rejected")
        self.assertIn('muito grandes', error.lower())


class InputValidationTests(TestCase):
    """
    Test suite for input validation rules.
    
    Requirements: 8.3 - Add input validation rules
    """
    
    def test_dangerous_pattern_detection(self):
        """Test that dangerous patterns are detected and blocked"""
        dangerous_inputs = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src=x onerror=alert("xss")>',
            '<iframe src="malicious.com"></iframe>',
            '<object data="malicious.swf"></object>',
            '<embed src="malicious.swf">',
        ]
        
        for dangerous_input in dangerous_inputs:
            is_valid, error = ChatSecurityValidator.validate_message_content(dangerous_input)
            self.assertFalse(
                is_valid,
                f"Dangerous pattern not detected: {dangerous_input}"
            )
            self.assertIn('não permitidos', error.lower())
    
    def test_input_sanitization(self):
        """Test that inputs are properly sanitized"""
        test_cases = [
            ('<script>alert("xss")</script>', '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'),
            ('<b>Bold</b>', '&lt;b&gt;Bold&lt;/b&gt;'),
            ('Normal text', 'Normal text'),
            ('Text with & ampersand', 'Text with &amp; ampersand'),
        ]
        
        for input_text, expected_output in test_cases:
            sanitized = ChatSecurityValidator.sanitize_message_content(input_text)
            self.assertEqual(
                sanitized,
                expected_output,
                f"Sanitization failed for: {input_text}"
            )
    
    def test_session_id_validation(self):
        """Test that session IDs are validated"""
        # Valid UUID
        valid_uuid = '550e8400-e29b-41d4-a716-446655440000'
        is_valid, error = ChatSecurityValidator.validate_session_id(valid_uuid)
        self.assertTrue(is_valid, f"Valid UUID rejected: {error}")
        
        # Invalid formats
        invalid_ids = [
            'not-a-uuid',
            '12345',
            'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',  # Not hex
            '',
            None,
        ]
        
        for invalid_id in invalid_ids:
            is_valid, error = ChatSecurityValidator.validate_session_id(invalid_id)
            self.assertFalse(
                is_valid,
                f"Invalid session ID not rejected: {invalid_id}"
            )
    
    def test_rating_validation(self):
        """Test that ratings are validated"""
        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            is_valid, error, normalized = ChatSecurityValidator.validate_rating(rating)
            self.assertTrue(is_valid, f"Valid rating rejected: {rating}")
            self.assertEqual(normalized, rating)
        
        # Invalid ratings
        invalid_ratings = [0, 6, -1, 'not a number', None, 3.5]
        
        for rating in invalid_ratings:
            is_valid, error, normalized = ChatSecurityValidator.validate_rating(rating)
            self.assertFalse(
                is_valid,
                f"Invalid rating not rejected: {rating}"
            )
    
    def test_json_message_validation(self):
        """Test that JSON messages are validated"""
        # Valid JSON message
        valid_json = json.dumps({'type': 'message', 'content': 'Hello'})
        is_valid, error, data = ChatSecurityValidator.validate_json_message(valid_json)
        self.assertTrue(is_valid, f"Valid JSON rejected: {error}")
        self.assertIsInstance(data, dict)
        self.assertIn('type', data)
        
        # Invalid JSON
        invalid_json = 'not json'
        is_valid, error, data = ChatSecurityValidator.validate_json_message(invalid_json)
        self.assertFalse(is_valid, "Invalid JSON not rejected")
        
        # Valid JSON but not an object
        invalid_structure = json.dumps(['array', 'not', 'object'])
        is_valid, error, data = ChatSecurityValidator.validate_json_message(invalid_structure)
        self.assertFalse(is_valid, "Non-object JSON not rejected")
        
        # Missing required field
        missing_type = json.dumps({'content': 'Hello'})
        is_valid, error, data = ChatSecurityValidator.validate_json_message(missing_type)
        self.assertFalse(is_valid, "JSON without 'type' field not rejected")
    
    def test_context_data_validation(self):
        """Test that context data is validated"""
        # Valid context
        valid_context = {
            'page': 'home',
            'user_type': 'client',
            'referrer': 'google',
        }
        is_valid, error = ChatSecurityValidator.validate_context_data(valid_context)
        self.assertTrue(is_valid, f"Valid context rejected: {error}")
        
        # Invalid context (not a dict)
        invalid_context = "not a dict"
        is_valid, error = ChatSecurityValidator.validate_context_data(invalid_context)
        self.assertFalse(is_valid, "Non-dict context not rejected")
        
        # Invalid context (invalid key)
        invalid_key_context = {'invalid key!': 'value'}
        is_valid, error = ChatSecurityValidator.validate_context_data(invalid_key_context)
        self.assertFalse(is_valid, "Context with invalid key not rejected")


class CORSConfigurationTests(TestCase):
    """
    Test suite for CORS configuration.
    
    Requirements: 8.3 - Configure CORS for WebSocket connections
    """
    
    def test_origin_checking(self):
        """Test that origin checking works correctly"""
        allowed_origins = [
            'http://localhost:8000',
            'http://localhost:3000',
        ]
        
        # Valid origins
        for origin in allowed_origins:
            is_allowed = ChatSecurityValidator.check_origin(origin, allowed_origins)
            self.assertTrue(
                is_allowed,
                f"Allowed origin rejected: {origin}"
            )
        
        # Invalid origins
        invalid_origins = [
            'http://malicious-site.com',
            'http://evil.com',
            'https://phishing.com',
        ]
        
        for origin in invalid_origins:
            is_allowed = ChatSecurityValidator.check_origin(origin, allowed_origins)
            self.assertFalse(
                is_allowed,
                f"Unauthorized origin accepted: {origin}"
            )
    
    def test_wildcard_origin(self):
        """Test wildcard origin handling"""
        allowed_origins = ['*']
        
        # Any origin should be allowed with wildcard
        test_origins = [
            'http://localhost:8000',
            'http://malicious-site.com',
            'https://any-domain.com',
        ]
        
        for origin in test_origins:
            is_allowed = ChatSecurityValidator.check_origin(origin, allowed_origins)
            self.assertTrue(
                is_allowed,
                f"Origin rejected with wildcard: {origin}"
            )
    
    def test_pattern_matching(self):
        """Test pattern matching for origins"""
        allowed_origins = ['*.example.com']
        
        # Should match
        matching_origins = [
            'http://sub.example.com',
            'https://api.example.com',
            'http://www.example.com',
        ]
        
        for origin in matching_origins:
            is_allowed = ChatSecurityValidator.check_origin(origin, allowed_origins)
            self.assertTrue(
                is_allowed,
                f"Matching origin rejected: {origin}"
            )
        
        # Should not match
        non_matching_origins = [
            'http://example.com',  # No subdomain
            'http://example.org',  # Different TLD
            'http://notexample.com',  # Different domain
        ]
        
        for origin in non_matching_origins:
            is_allowed = ChatSecurityValidator.check_origin(origin, allowed_origins)
            self.assertFalse(
                is_allowed,
                f"Non-matching origin accepted: {origin}"
            )


class ConnectionLimitTests(TestCase):
    """
    Test suite for connection limit enforcement.
    
    Requirements: 8.3
    """
    
    def setUp(self):
        """Clear cache before each test"""
        from django.core.cache import cache
        cache.clear()
    
    def test_connection_tracking(self):
        """Test that connections are tracked correctly"""
        user_id = 123
        ip_address = '192.168.1.1'
        
        # Increment connection
        user_count, ip_count = ConnectionTracker.increment_connection(
            user_id=user_id,
            ip_address=ip_address
        )
        
        self.assertEqual(user_count, 1)
        self.assertEqual(ip_count, 1)
        
        # Increment again
        user_count, ip_count = ConnectionTracker.increment_connection(
            user_id=user_id,
            ip_address=ip_address
        )
        
        self.assertEqual(user_count, 2)
        self.assertEqual(ip_count, 2)
        
        # Decrement
        ConnectionTracker.decrement_connection(
            user_id=user_id,
            ip_address=ip_address
        )
        
        # Check limit (should be within limit now)
        is_allowed, reason = ConnectionTracker.check_connection_limit(
            user_id=user_id,
            ip_address=ip_address
        )
        self.assertTrue(is_allowed)
    
    @override_settings(WEBSOCKET_SECURITY={'MAX_CONNECTIONS_PER_USER': 2, 'MAX_CONNECTIONS_PER_IP': 3})
    def test_connection_limit_enforcement(self):
        """Test that connection limits are enforced"""
        user_id = 456
        
        # Add connections up to limit
        for i in range(2):
            ConnectionTracker.increment_connection(user_id=user_id)
        
        # Check limit (should be at limit)
        is_allowed, reason = ConnectionTracker.check_connection_limit(user_id=user_id)
        self.assertFalse(is_allowed, "Connection limit not enforced")
        self.assertIn('exceeded', reason.lower())


# Run tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['services.chat.test_security_config'])
