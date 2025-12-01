"""
Structured Logging Configuration for Chat System

This module provides structured logging utilities for the chat system,
enabling better monitoring, debugging, and analytics.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs for better parsing and analysis.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON string with structured log data
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'event'):
            log_data['event'] = record.event
        if hasattr(record, 'processing_time_ms'):
            log_data['processing_time_ms'] = record.processing_time_ms
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        if hasattr(record, 'error_message'):
            log_data['error_message'] = record.error_message
        if hasattr(record, 'intent'):
            log_data['intent'] = record.intent
        if hasattr(record, 'cached'):
            log_data['cached'] = record.cached
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ChatLogger:
    """
    Structured logger for chat operations.
    
    This class provides convenience methods for logging chat-related events
    with structured data for better analysis and monitoring.
    """
    
    def __init__(self, name: str = 'services.chat'):
        """
        Initialize the chat logger.
        
        Args:
            name: Logger name (default: 'services.chat')
        """
        self.logger = logging.getLogger(name)
    
    def log_message_processed(
        self,
        session_id: str,
        user_id: Optional[int],
        processing_time_ms: float,
        intent: Optional[str] = None,
        cached: bool = False
    ) -> None:
        """
        Log a processed message event.
        
        Args:
            session_id: The chat session ID
            user_id: The user ID (None for anonymous)
            processing_time_ms: Time taken to process the message
            intent: Detected intent of the message
            cached: Whether the response was cached
            
        Requirements: 7.1
        """
        self.logger.info(
            "Message processed",
            extra={
                'event': 'message_processed',
                'session_id': session_id,
                'user_id': user_id,
                'processing_time_ms': processing_time_ms,
                'intent': intent,
                'cached': cached
            }
        )
    
    def log_session_created(
        self,
        session_id: str,
        user_id: Optional[int],
        user_type: str
    ) -> None:
        """
        Log a session creation event.
        
        Args:
            session_id: The new chat session ID
            user_id: The user ID (None for anonymous)
            user_type: Type of user (client/provider/anonymous)
            
        Requirements: 7.1
        """
        self.logger.info(
            "Session created",
            extra={
                'event': 'session_created',
                'session_id': session_id,
                'user_id': user_id,
                'user_type': user_type
            }
        )
    
    def log_session_closed(
        self,
        session_id: str,
        user_id: Optional[int],
        total_messages: int,
        duration_seconds: float
    ) -> None:
        """
        Log a session closure event.
        
        Args:
            session_id: The chat session ID
            user_id: The user ID (None for anonymous)
            total_messages: Total messages in the session
            duration_seconds: Session duration in seconds
            
        Requirements: 7.1
        """
        self.logger.info(
            "Session closed",
            extra={
                'event': 'session_closed',
                'session_id': session_id,
                'user_id': user_id,
                'total_messages': total_messages,
                'duration_seconds': duration_seconds
            }
        )
    
    def log_ai_api_call(
        self,
        session_id: str,
        processing_time_ms: float,
        cached: bool,
        success: bool
    ) -> None:
        """
        Log an AI API call event.
        
        Args:
            session_id: The chat session ID
            processing_time_ms: Time taken for the API call
            cached: Whether the response was cached
            success: Whether the call was successful
            
        Requirements: 7.1
        """
        level = logging.INFO if success else logging.ERROR
        self.logger.log(
            level,
            "AI API call",
            extra={
                'event': 'ai_api_call',
                'session_id': session_id,
                'processing_time_ms': processing_time_ms,
                'cached': cached,
                'success': success
            }
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        operation: Optional[str] = None
    ) -> None:
        """
        Log an error event.
        
        Args:
            error_type: Type of error
            error_message: Error message
            session_id: The chat session ID (if applicable)
            user_id: The user ID (if applicable)
            operation: The operation that failed (if applicable)
            
        Requirements: 7.1
        """
        self.logger.error(
            f"Error: {error_type}",
            extra={
                'event': 'error',
                'error_type': error_type,
                'error_message': error_message,
                'session_id': session_id,
                'user_id': user_id,
                'operation': operation
            }
        )
    
    def log_rate_limit(
        self,
        user_id: Optional[int],
        session_id: Optional[str] = None
    ) -> None:
        """
        Log a rate limit event.
        
        Args:
            user_id: The user ID that hit the rate limit
            session_id: The chat session ID (if applicable)
            
        Requirements: 7.1
        """
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                'event': 'rate_limit_exceeded',
                'user_id': user_id,
                'session_id': session_id
            }
        )
    
    def log_cache_hit(
        self,
        session_id: str,
        message_hash: str
    ) -> None:
        """
        Log a cache hit event.
        
        Args:
            session_id: The chat session ID
            message_hash: Hash of the cached message
            
        Requirements: 7.1
        """
        self.logger.info(
            "Cache hit",
            extra={
                'event': 'cache_hit',
                'session_id': session_id,
                'message_hash': message_hash
            }
        )
    
    def log_cache_miss(
        self,
        session_id: str,
        message_hash: str
    ) -> None:
        """
        Log a cache miss event.
        
        Args:
            session_id: The chat session ID
            message_hash: Hash of the message
            
        Requirements: 7.1
        """
        self.logger.info(
            "Cache miss",
            extra={
                'event': 'cache_miss',
                'session_id': session_id,
                'message_hash': message_hash
            }
        )
    
    def log_websocket_connection(
        self,
        user_id: Optional[int],
        session_id: Optional[str] = None,
        connected: bool = True
    ) -> None:
        """
        Log a WebSocket connection event.
        
        Args:
            user_id: The user ID
            session_id: The chat session ID (if applicable)
            connected: Whether connecting (True) or disconnecting (False)
            
        Requirements: 7.1
        """
        event = 'websocket_connected' if connected else 'websocket_disconnected'
        self.logger.info(
            f"WebSocket {'connected' if connected else 'disconnected'}",
            extra={
                'event': event,
                'user_id': user_id,
                'session_id': session_id
            }
        )


def configure_chat_logging() -> None:
    """
    Configure structured logging for the chat system.
    
    This function sets up a dedicated logger for chat operations with
    structured JSON formatting for better analysis and monitoring.
    
    Requirements: 7.1
    """
    # Get or create chat logger
    chat_logger = logging.getLogger('services.chat')
    chat_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    chat_logger.handlers.clear()
    
    # Create console handler with structured formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    
    # Create file handler with structured formatter
    file_handler = logging.FileHandler('chat.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(StructuredFormatter())
    
    # Add handlers to logger
    chat_logger.addHandler(console_handler)
    chat_logger.addHandler(file_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    chat_logger.propagate = False
