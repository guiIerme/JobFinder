"""
Tests for KnowledgeBase service class

Tests the search, service info retrieval, FAQ, and navigation help methods.
"""

from django.test import TestCase
from services.chat.knowledge_base import KnowledgeBase
from services.chat_models import KnowledgeBaseEntry
from services.models import Service
from datetime import timedelta


class KnowledgeBaseTests(TestCase):
    """Test suite for KnowledgeBase class"""
    
    def setUp(self):
        """Set up test data"""
        self.kb = KnowledgeBase()
        
        # Create test service
        self.service = Service.objects.create(
            name='Test Cleaning Service',
            description='Professional cleaning service',
            category='cleaning',
            base_price=100.00,
            estimated_duration=timedelta(hours=2),
            is_active=True
        )
        
        # Create test knowledge base entries
        self.service_entry = KnowledgeBaseEntry.objects.create(
            title='Cleaning Services Info',
            content='We offer professional cleaning services',
            category='service',
            keywords=['cleaning', 'limpeza', 'service'],
            is_active=True
        )
        self.service_entry.related_services.add(self.service)
        
        self.faq_entry = KnowledgeBaseEntry.objects.create(
            title='How to request a service?',
            content='To request a service, go to services page',
            category='faq',
            keywords=['request', 'solicitar', 'how'],
            is_active=True
        )
        
        self.nav_entry = KnowledgeBaseEntry.objects.create(
            title='Navigation - Home Page',
            content='The home page shows available services',
            category='navigation',
            keywords=['home', 'inicio', 'navigation'],
            is_active=True
        )
    
    def test_search_with_query(self):
        """Test search method with query string"""
        results = self.kb.search('cleaning')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, 'Cleaning Services Info')
    
    def test_search_with_category_filter(self):
        """Test search with category filter"""
        results = self.kb.search('service', category='faq')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().category, 'faq')
    
    def test_search_empty_query(self):
        """Test search with empty query returns no results"""
        results = self.kb.search('')
        self.assertEqual(results.count(), 0)
    
    def test_get_service_info(self):
        """Test get_service_info method"""
        info = self.kb.get_service_info(self.service.id)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'Test Cleaning Service')
        self.assertEqual(info['category'], 'cleaning')
        self.assertEqual(float(info['base_price']), 100.00)
        self.assertEqual(info['estimated_duration_hours'], 2.0)
        self.assertEqual(len(info['knowledge_entries']), 1)
    
    def test_get_service_info_not_found(self):
        """Test get_service_info with non-existent service"""
        info = self.kb.get_service_info(99999)
        self.assertIsNone(info)
    
    def test_get_faq_with_topic(self):
        """Test get_faq method with specific topic"""
        faqs = self.kb.get_faq('request')
        
        self.assertEqual(len(faqs), 1)
        self.assertEqual(faqs[0]['title'], 'How to request a service?')
        self.assertIn('keywords', faqs[0])
    
    def test_get_faq_without_topic(self):
        """Test get_faq method without topic returns general FAQs"""
        faqs = self.kb.get_faq('')
        
        # Should return FAQ entries (limited to 10)
        self.assertIsInstance(faqs, list)
    
    def test_get_navigation_help(self):
        """Test get_navigation_help method"""
        help_content = self.kb.get_navigation_help('home')
        
        self.assertIsNotNone(help_content)
        self.assertEqual(help_content['title'], 'Navigation - Home Page')
        self.assertIn('content', help_content)
        self.assertIn('keywords', help_content)
    
    def test_get_navigation_help_not_found(self):
        """Test get_navigation_help with non-existent page"""
        help_content = self.kb.get_navigation_help('nonexistent')
        self.assertIsNone(help_content)
    
    def test_usage_count_increment(self):
        """Test that usage count increments when entries are accessed"""
        initial_count = self.faq_entry.usage_count
        
        # Access the FAQ
        self.kb.get_faq('request')
        
        # Refresh from database
        self.faq_entry.refresh_from_db()
        
        # Usage count should have incremented
        self.assertEqual(self.faq_entry.usage_count, initial_count + 1)
