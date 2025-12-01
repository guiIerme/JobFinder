# Chat Analytics System

This document describes the analytics and reporting features for the Sophie chat assistant.

## Overview

The chat analytics system tracks and reports on chat session performance, user engagement, and conversation metrics. It provides both real-time dashboards and exportable reports for analysis.

**Requirements Implemented:** 7.1, 7.2, 7.4, 7.5

## Features

### 1. Analytics Tracking (Requirement 7.1)

Analytics are automatically tracked during chat sessions via the `AnalyticsTracker` class in `consumers.py`:

- **Message counts**: User messages, assistant messages, total messages
- **Response times**: Processing time for each AI response
- **Topics discussed**: Topics identified during conversation
- **Actions taken**: User actions like link clicks, service views
- **Engagement metrics**: Calculated engagement scores

Data is saved to the `ChatAnalytics` model when sessions are closed or disconnected.

### 2. Admin Dashboard (Requirement 7.2)

Access the analytics dashboard at: `/admin/chat-analytics/`

**Features:**
- Real-time active session count
- Average response time metrics
- Satisfaction ratings
- Resolution rate statistics
- Top topics discussed
- User type distribution
- Recent session details with engagement scores

**Time Filters:**
- Last 24 hours
- Last 7 days (default)
- Last 30 days
- Last 90 days

**Auto-refresh:** Active session count updates every 30 seconds

### 3. Data Export (Requirement 7.4)

Export chat data to CSV format for external analysis:

#### Export Sessions
```
GET /admin/chat-analytics/export/sessions/
```

**Query Parameters:**
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `user_type`: Filter by user type (client, provider, anonymous)
- `is_active`: Filter by status (true/false)

**Exported Fields:**
- Session ID, User, User Type, Status
- Created/Updated/Closed timestamps
- Message counts (total, user, assistant)
- Average response time
- Satisfaction rating
- Resolution status
- Topics discussed
- Engagement score

#### Export Messages
```
GET /admin/chat-analytics/export/messages/
```

**Query Parameters:**
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `session_id`: Filter by specific session
- `sender_type`: Filter by sender (user, assistant, system)

**Exported Fields:**
- Message ID, Session ID, User
- Sender type, Content
- Created timestamp
- Processing time
- Cached response indicator
- Metadata

#### Export Analytics
```
GET /admin/chat-analytics/export/analytics/
```

**Query Parameters:**
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `user_type`: Filter by user type
- `resolved`: Filter by resolution status (true/false)

**Exported Fields:**
- Analytics ID, Session ID, User
- Message counts and response times
- Resolution and escalation status
- Topics and actions
- Engagement score
- Session duration

### 4. Weekly Reports (Requirement 7.5)

Generate comprehensive weekly reports using the Django management command:

```bash
python manage.py generate_chat_weekly_report [options]
```

**Options:**
- `--days N`: Number of days to include (default: 7)
- `--format {text,json}`: Output format (default: text)
- `--output FILE`: Save to file instead of console

**Report Contents:**
- Session statistics (total, active, closed)
- Message statistics (total, by sender type, average per session)
- Performance metrics (response time, resolution rate, engagement)
- User satisfaction (average rating, rating count)
- Top topics discussed (most frequent topics)
- Common issues (topics from unresolved sessions)
- User type distribution
- Peak usage hours

**Examples:**

Generate text report for last 7 days:
```bash
python manage.py generate_chat_weekly_report
```

Generate JSON report for last 30 days:
```bash
python manage.py generate_chat_weekly_report --days 30 --format json
```

Save report to file:
```bash
python manage.py generate_chat_weekly_report --output weekly_report.txt
```

Save JSON report:
```bash
python manage.py generate_chat_weekly_report --format json --output report.json
```

## Scheduled Reports

To automatically generate weekly reports, add a cron job or scheduled task:

**Linux/Mac (crontab):**
```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/project && python manage.py generate_chat_weekly_report --output /path/to/reports/weekly_$(date +\%Y\%m\%d).txt
```

**Windows (Task Scheduler):**
Create a scheduled task that runs:
```cmd
python manage.py generate_chat_weekly_report --output C:\reports\weekly_report.txt
```

## API Endpoints

### Real-time Analytics API
```
GET /admin/chat-analytics/api/
```

Returns JSON with current metrics:
```json
{
  "active_sessions": 5,
  "avg_response_time": 1234.56,
  "avg_satisfaction": 4.2,
  "timestamp": "2025-11-26T17:20:15.015621+00:00"
}
```

## Database Models

### ChatAnalytics
Stores analytics data for each chat session:
- `analytics_id`: UUID primary key
- `session`: OneToOne relationship to ChatSession
- `total_messages`: Total message count
- `user_messages`: User message count
- `assistant_messages`: Assistant message count
- `average_response_time_ms`: Average AI response time
- `resolved`: Whether issue was resolved
- `escalated_to_human`: Whether escalated to human support
- `topics_discussed`: JSON array of topics
- `actions_taken`: JSON array of user actions
- `created_at`: Timestamp

**Computed Properties:**
- `engagement_score`: Calculated engagement metric (0-100)

## Permissions

All analytics endpoints require staff member permissions (`@staff_member_required`).

## Performance Considerations

- Analytics data is saved asynchronously during session disconnect
- Dashboard queries use database indexes for efficiency
- Export operations stream data to avoid memory issues with large datasets
- Real-time API endpoint uses lightweight queries for fast response

## Future Enhancements

Potential improvements for future versions:
- Email delivery of weekly reports
- Custom report templates
- Advanced filtering and segmentation
- Trend analysis and predictions
- Integration with external analytics platforms
- Real-time alerting for anomalies
