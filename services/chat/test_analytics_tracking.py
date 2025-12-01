"""
Tests for analytics tracking in ChatConsumer.

Tests the analytics tracking functionality implemented in task 11.1.
Requirements: 7.1, 7.2
"""

from django.test import TestCase
from django.contrib.auth.models import User
from services.chat.consumers import AnalyticsTracker
from services.chat_models import ChatSession, ChatMessage, ChatAnalytics
import json


class AnalyticsTrackerTests(TestCase):
    """Test the AnalyticsTracker helper class"""
    
    def setUp(self):
        self.tracker = AnalyticsTracker()
    
    def test_track_user_message(self):
        """Test tracking user messages"""
        self.assertEqual(self.tracker.user_message_count, 0)
        self.tracker.track_user_message()
        self.assertEqual(self.tracker.user_message_count, 1)
        self.tracker.track_user_message()
        self.assertEqual(self.tracker.user_message_count, 2)
    
    def test_track_assistant_message(self):
        """Test tracking assistant messages with response times"""
        self.assertEqual(self.tracker.assistant_message_count, 0)
        self.assertEqual(len(self.tracker.response_times), 0)
        
        self.tracker.track_assistant_message(100)
        self.assertEqual(self.tracker.assistant_message_count, 1)
        self.assertEqual(len(self.tracker.response_times), 1)
        self.assertEqual(self.tracker.response_times[0], 100)
        
        self.tracker.track_assistant_message(200)
        self.assertEqual(self.tracker.assistant_message_count, 2)
        self.assertEqual(len(self.tracker.response_times), 2)
    
    def test_track_assistant_message_with_none_response_time(self):
        """Test tracking assistant message with None response time"""
        self.tracker.track_assistant_message(None)
        self.assertEqual(self.tracker.assistant_message_count, 1)
        self.assertEqual(len(self.tracker.response_times), 0)
    
    def test_get_average_response_time(self):
        """Test calculating average response time"""
        # No responses yet
        self.assertIsNone(self.tracker.get_average_response_time())
        
        # Add some response times
        self.tracker.track_assistant_message(100)
        self.assertEqual(self.tracker.get_average_response_time(), 100.0)
        
        self.tracker.track_assistant_message(200)
        self.assertEqual(self.tracker.get_average_response_time(), 150.0)
        
        self.tracker.track_assistant_message(300)
        self.assertEqual(self.tracker.get_average_response_time(), 200.0)
    
    def test_get_total_messages(self):
        """Test getting total message count"""
        self.assertEqual(self.tracker.get_total_messages(), 0)
        
        self.tracker.track_user_message()
        self.assertEqual(self.tracker.get_total_messages(), 1)
        
        self.tracker.track_assistant_message(100)
        self.assertEqual(self.tracker.get_total_messages(), 2)
        
        self.tracker.track_user_message()
        self.tracker.track_assistant_message(200)
        self.assertEqual(self.tracker.get_total_messages(), 4)
    
    def test_track_topic(self):
        """Test tracking topics discussed"""
        self.assertEqual(len(self.tracker.topics), 0)
        
        self.tracker.track_topic('service_inquiry')
        self.assertEqual(len(self.tracker.topics), 1)
        self.assertIn('service_inquiry', self.tracker.topics)
        
        # Duplicate topics should not be added
        self.tracker.track_topic('service_inquiry')
        self.assertEqual(len(self.tracker.topics), 1)
        
        self.tracker.track_topic('navigation_help')
        self.assertEqual(len(self.tracker.topics), 2)
    
    def test_track_action(self):
        """Test tracking user actions"""
        self.assertEqual(len(self.tracker.actions), 0)
        
        self.tracker.track_action('link_clicked', {'url': '/services/'})
        self.assertEqual(len(self.tracker.actions), 1)
        self.assertEqual(self.tracker.actions[0]['type'], 'link_clicked')
        self.assertEqual(self.tracker.actions[0]['data']['url'], '/services/')
        
        self.tracker.track_action('service_viewed')
        self.assertEqual(len(self.tracker.actions), 2)
    
    def test_to_dict(self):
        """Test converting tracker data to dictionary"""
        self.tracker.track_user_message()
        self.tracker.track_user_message()
        self.tracker.track_assistant_message(100)
        self.tracker.track_assistant_message(200)
        self.tracker.track_topic('service_inquiry')
        self.tracker.track_action('link_clicked')
        
        data = self.tracker.to_dict()
        
        self.assertEqual(data['total_messages'], 4)
        self.assertEqual(data['user_messages'], 2)
        self.assertEqual(data['assistant_messages'], 2)
        self.assertEqual(data['average_response_time_ms'], 150.0)
        self.assertEqual(len(data['topics_discussed']), 1)
        self.assertEqual(len(data['actions_taken']), 1)


class ChatAnalyticsIntegrationTests(TestCase):
    """Integration tests for analytics tracking in chat sessions"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_analytics_record_creation(self):
        """Test that ChatAnalytics record is created for a session"""
        # Create a chat session
        session = ChatSession.objects.create(
            user=self.user,
            user_type='client'
        )
        
        # Create analytics record
        analytics = ChatAnalytics.objects.create(
            session=session,
            total_messages=5,
            user_messages=3,
            assistant_messages=2,
            average_response_time_ms=150.5
        )
        
        # Verify record was created
        self.assertIsNotNone(analytics.analytics_id)
        self.assertEqual(analytics.session, session)
        self.assertEqual(analytics.total_messages, 5)
        self.assertEqual(analytics.user_messages, 3)
        self.assertEqual(analytics.assistant_messages, 2)
        self.assertEqual(analytics.average_response_time_ms, 150.5)
    
    def test_analytics_update(self):
        """Test updating analytics record"""
        session = ChatSession.objects.create(
            user=self.user,
            user_type='client'
        )
        
        analytics = ChatAnalytics.objects.create(
            session=session,
            total_messages=2,
            user_messages=1,
            assistant_messages=1
        )
        
        # Update analytics
        analytics.total_messages = 4
        analytics.user_messages = 2
        analytics.assistant_messages = 2
        analytics.average_response_time_ms = 200.0
        analytics.save()
        
        # Verify update
        updated_analytics = ChatAnalytics.objects.get(session=session)
        self.assertEqual(updated_analytics.total_messages, 4)
        self.assertEqual(updated_analytics.user_messages, 2)
        self.assertEqual(updated_analytics.assistant_messages, 2)
        self.assertEqual(updated_analytics.average_response_time_ms, 200.0)
    
    def test_analytics_topics_and_actions(self):
        """Test storing topics and actions in analytics"""
        session = ChatSession.objects.create(
            user=self.user,
            user_type='client'
        )
        
        topics = ['service_inquiry', 'navigation_help']
        actions = [
            {'type': 'link_clicked', 'data': {'url': '/services/'}},
            {'type': 'service_viewed', 'data': {'service_id': 1}}
        ]
        
        analytics = ChatAnalytics.objects.create(
            session=session,
            total_messages=4,
            user_messages=2,
            assistant_messages=2,
            topics_discussed=topics,
            actions_taken=actions
        )
        
        # Verify JSON fields
        self.assertEqual(len(analytics.topics_discussed), 2)
        self.assertIn('service_inquiry', analytics.topics_discussed)
        self.assertEqual(len(analytics.actions_taken), 2)
        self.assertEqual(analytics.actions_taken[0]['type'], 'link_clicked')
    
    def test_engagement_score_calculation(self):
        """Test engagement score property calculation"""
        session = ChatSession.objects.create(
            user=self.user,
            user_type='client'
        )
        
        # Test with no messages
        analytics = ChatAnalytics.objects.create(
            session=session,
            total_messages=0
        )
        self.assertEqual(analytics.engagement_score, 0)
        
        # Test with messages
        analytics.total_messages = 5
        analytics.save()
        self.assertEqual(analytics.engagement_score, 50)
        
        # Test with resolved conversation
        analytics.resolved = True
        analytics.save()
        self.assertEqual(analytics.engagement_score, 70)
        
        # Test with escalation (should reduce score)
        analytics.escalated_to_human = True
        analytics.save()
        self.assertEqual(analytics.engagement_score, 60)
    
    def test_one_to_one_relationship(self):
        """Test that each session can only have one analytics record"""
        session = ChatSession.objects.create(
            user=self.user,
            user_type='client'
        )
        
        # Create first analytics record
        analytics1 = ChatAnalytics.objects.create(
            session=session,
            total_messages=2
        )
        
        # Attempting to create another should fail or replace
        with self.assertRaises(Exception):
            ChatAnalytics.objects.create(
                session=session,
                total_messages=4
            )
