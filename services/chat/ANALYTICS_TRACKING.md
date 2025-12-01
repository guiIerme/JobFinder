# Chat Analytics Tracking Implementation

## Overview

This document describes the analytics tracking implementation for the Chat IA Assistente (Sophie) system, completed as part of task 11.1.

## Requirements

- **Requirement 7.1**: Track all chat sessions including questions, responses, and actions taken
- **Requirement 7.2**: Provide admin dashboard with usage and satisfaction metrics

## Implementation

### AnalyticsTracker Class

A helper class that tracks metrics during an active WebSocket session:

**Tracked Metrics:**
- User message count
- Assistant message count
- Response times (in milliseconds)
- Topics discussed
- User actions (links clicked, services viewed, etc.)

**Key Methods:**
- `track_user_message()`: Increment user message counter
- `track_assistant_message(response_time_ms)`: Track assistant message and response time
- `track_topic(topic)`: Record a topic discussed
- `track_action(action_type, action_data)`: Record a user action
- `get_average_response_time()`: Calculate average response time
- `get_total_messages()`: Get total message count
- `to_dict()`: Convert tracker data to dictionary for storage

### ChatConsumer Integration

The `ChatConsumer` class has been enhanced with analytics tracking:

**Initialization:**
- Each WebSocket connection creates an `AnalyticsTracker` instance

**Message Handling:**
- User messages are tracked when received
- Response times are measured from message receipt to response generation
- Assistant messages are tracked with their response times

**Session Lifecycle:**
- Analytics are saved when the session is closed (user request)
- Analytics are saved when the WebSocket disconnects
- Analytics records are created or updated in the database

**Database Integration:**
- `save_analytics()` method creates or updates `ChatAnalytics` records
- Uses `get_or_create` to handle both new and existing sessions
- Stores all tracked metrics in the database

### ChatAnalytics Model

The `ChatAnalytics` model stores the following fields:

- `analytics_id`: Unique identifier (UUID)
- `session`: One-to-one relationship with ChatSession
- `total_messages`: Total number of messages
- `user_messages`: Number of user messages
- `assistant_messages`: Number of assistant messages
- `average_response_time_ms`: Average response time in milliseconds
- `resolved`: Whether the issue was resolved
- `escalated_to_human`: Whether escalated to human support
- `topics_discussed`: JSON array of topics
- `actions_taken`: JSON array of actions
- `created_at`: Timestamp of creation

**Computed Properties:**
- `engagement_score`: Calculated based on message count and resolution status

## Usage Example

```python
# In ChatConsumer
async def handle_chat_message(self, data):
    # Track user message
    self.analytics_tracker.track_user_message()
    
    # Measure response time
    start_time = time.time()
    
    # Process message...
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Track assistant message
    self.analytics_tracker.track_assistant_message(response_time_ms)
    
    # Track topics and actions as needed
    self.analytics_tracker.track_topic('service_inquiry')
    self.analytics_tracker.track_action('link_clicked', {'url': '/services/'})
```

## Testing

Comprehensive tests have been implemented in `test_analytics_tracking.py`:

**AnalyticsTrackerTests:**
- Test message tracking
- Test response time calculation
- Test topic and action tracking
- Test data conversion

**ChatAnalyticsIntegrationTests:**
- Test analytics record creation
- Test analytics updates
- Test JSON field storage
- Test engagement score calculation
- Test one-to-one relationship constraint

All tests pass successfully.

## Future Enhancements

The following features can be added in future tasks:

1. **Topic Detection**: Automatically detect topics from message content using AI
2. **Action Tracking**: Track more user actions (service views, navigation, etc.)
3. **Real-time Metrics**: Display live analytics in admin dashboard
4. **Satisfaction Ratings**: Integrate with satisfaction rating collection (task 12)
5. **Escalation Detection**: Automatically detect when to escalate to human support
6. **Performance Monitoring**: Alert on slow response times or high error rates

## Performance Considerations

- Analytics tracking is lightweight and non-blocking
- Database writes are batched (only on session close/disconnect)
- In-memory tracking during active session minimizes database load
- Async database operations prevent blocking WebSocket communication

## Logging

Analytics operations are logged with the following information:
- Session ID
- Message counts
- Response times
- Whether analytics record was created or updated

Example log entry:
```
INFO: Analytics saved for session abc-123
  session_id: abc-123
  total_messages: 8
  average_response_time_ms: 156.3
  created: False
```

## Related Files

- `services/chat/consumers.py`: Main implementation
- `services/chat_models.py`: ChatAnalytics model definition
- `services/chat/test_analytics_tracking.py`: Test suite
- `.kiro/specs/chat-ia-assistente/design.md`: Design specification
- `.kiro/specs/chat-ia-assistente/requirements.md`: Requirements specification
