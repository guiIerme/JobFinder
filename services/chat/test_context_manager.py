"""
Tests for ContextManager

Tests the user context extraction, navigation context tracking,
and knowledge base query functionality.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from services.models import UserProfile, Service
from services.chat_models import KnowledgeBaseEntry
from services.chat.context_manager import ContextManager


class ContextManagerTests(TestCase):
    """Test suite for ContextManager"""
    
    def setUp(self):
        """Set up test data"""
        self.context_manager = ContextManager()
        
        # Create test users
        self.client_user = User.objects.create_user(
            username='testclient',
            email='client@test.com',
            first_name='Test',
            last_name='Client'
        )
        
        self.provider_user = User.objects.create_user(
            username='testprovider',
            email='provider@test.com',
            first_name='Test',
            last_name='Provider'
        )
        
        # Create profiles
        self.client_profile = UserProfile.objects.create(
            user=self.client_user,
            user_type='customer',
            phone='1234567890',
            city='São Paulo',
            state='SP',
            address='Test Address',
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        self.provider_profile = UserProfile.objects.create(
            user=self.provider_user,
            user_type='professional',
            phone='0987654321',
            city='Rio de Janeiro',
            state='RJ',
            business_name='Test Services',
            specialties='Limpeza, Pintura',
            experience_years=5,
            rating=4.5,
            review_count=10,
            is_verified=True,
            is_available=True,
            total_jobs=50,
            completed_jobs=45,
            service_radius=15
        )
        
        # Create knowledge base entries
        self.kb_entry1 = KnowledgeBaseEntry.objects.create(
            category='service',
            title='Serviços de Limpeza',
            content='Oferecemos diversos serviços de limpeza residencial e comercial.',
            keywords=['limpeza', 'faxina', 'cleaning'],
            is_active=True
        )
        
        self.kb_entry2 = KnowledgeBaseEntry.objects.create(
            category='faq',
            title='Como solicitar um serviço',
            content='Para solicitar um serviço, navegue até a página de serviços e clique em "Solicitar".',
            keywords=['solicitar', 'pedir', 'contratar'],
            is_active=True
        )
    
    def test_get_user_context_anonymous(self):
        """Test user context extraction for anonymous users"""
        context = self.context_manager.get_user_context(None)
        
        self.assertEqual(context['user_type'], 'anonymous')
        self.assertIsNone(context['username'])
        self.assertFalse(context['is_authenticated'])
        self.assertEqual(context['profile_data'], {})
    
    def test_get_user_context_client(self):
        """Test user context extraction for client users"""
        context = self.context_manager.get_user_context(self.client_user)
        
        self.assertEqual(context['user_type'], 'client')
        self.assertEqual(context['username'], 'testclient')
        self.assertTrue(context['is_authenticated'])
        self.assertEqual(context['profile_data']['phone'], '1234567890')
        self.assertEqual(context['profile_data']['city'], 'São Paulo')
        self.assertTrue(context['profile_data']['has_location'])
    
    def test_get_user_context_provider(self):
        """Test user context extraction for provider users"""
        context = self.context_manager.get_user_context(self.provider_user)
        
        self.assertEqual(context['user_type'], 'provider')
        self.assertEqual(context['username'], 'testprovider')
        self.assertTrue(context['is_authenticated'])
        self.assertEqual(context['profile_data']['business_name'], 'Test Services')
        self.assertEqual(context['profile_data']['experience_years'], 5)
        self.assertEqual(context['profile_data']['specialties'], ['Limpeza', 'Pintura'])
        self.assertTrue(context['profile_data']['is_verified'])
        self.assertEqual(context['profile_data']['completion_rate'], 90.0)
    
    def test_get_navigation_context_home(self):
        """Test navigation context for home page"""
        context = self.context_manager.get_navigation_context('http://example.com/')
        
        self.assertEqual(context['page_type'], 'home')
        self.assertFalse(context['is_error_page'])
        self.assertIn('available_actions', context['page_context'])
    
    def test_get_navigation_context_services(self):
        """Test navigation context for services page"""
        context = self.context_manager.get_navigation_context('http://example.com/services/')
        
        self.assertEqual(context['page_type'], 'services')
        self.assertFalse(context['is_error_page'])
    
    def test_get_navigation_context_error_page(self):
        """Test navigation context for error pages"""
        context = self.context_manager.get_navigation_context('http://example.com/404')
        
        self.assertEqual(context['page_type'], 'error')
        self.assertTrue(context['is_error_page'])
        self.assertTrue(context['page_context']['help_needed'])
    
    def test_get_navigation_context_with_referrer(self):
        """Test navigation context with referrer"""
        context = self.context_manager.get_navigation_context(
            'http://example.com/services/',
            'http://example.com/'
        )
        
        self.assertEqual(context['page_type'], 'services')
        self.assertIn('referrer_page', context)
        self.assertEqual(context['referrer_page']['type'], 'home')
    
    def test_build_knowledge_base_context(self):
        """Test knowledge base query"""
        results = self.context_manager.build_knowledge_base_context('limpeza')
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['title'], 'Serviços de Limpeza')
        self.assertIn('limpeza', results[0]['keywords'])
    
    def test_build_knowledge_base_context_with_category(self):
        """Test knowledge base query with category filter"""
        results = self.context_manager.build_knowledge_base_context('solicitar', category='faq')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category'], 'faq')
    
    def test_build_knowledge_base_context_empty_query(self):
        """Test knowledge base query with empty query"""
        results = self.context_manager.build_knowledge_base_context('')
        
        self.assertEqual(len(results), 0)
    
    def test_build_full_context(self):
        """Test building complete context"""
        context = self.context_manager.build_full_context(
            self.client_user,
            'http://example.com/services/',
            'http://example.com/',
            'limpeza'
        )
        
        self.assertIn('user', context)
        self.assertIn('navigation', context)
        self.assertIn('knowledge_base', context)
        self.assertIn('timestamp', context)
        
        self.assertEqual(context['user']['user_type'], 'client')
        self.assertEqual(context['navigation']['page_type'], 'services')
        self.assertGreater(len(context['knowledge_base']), 0)
