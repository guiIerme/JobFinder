"""
Context Manager - User and Navigation Context

This module manages context information for chat sessions,
including user profiles and navigation state.
"""

from django.contrib.auth.models import User
from services.models import UserProfile
from services.chat_models import KnowledgeBaseEntry
from django.db.models import Q
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages context for chat sessions.
    
    Responsibilities:
    - Extract user context from profiles
    - Track navigation context
    - Query knowledge base
    - Build contextual information for AI
    
    Requirements: 4.1, 5.5, 3.2, 3.4, 2.2
    """
    
    def get_user_context(self, user):
        """
        Extract context from user profile.
        
        Differentiates between client and provider user types and extracts
        relevant profile information for personalizing AI responses.
        
        Args:
            user: User object (can be None for anonymous users)
        
        Returns:
            Dictionary with user context including:
            - user_type: 'client', 'provider', or 'anonymous'
            - username: User's username (if authenticated)
            - profile_data: Relevant profile information based on user type
        
        Requirements: 4.1, 5.5
        """
        try:
            # Handle anonymous users
            if not user or not user.is_authenticated:
                return {
                    'user_type': 'anonymous',
                    'username': None,
                    'is_authenticated': False,
                    'profile_data': {}
                }
            
            # Get user profile
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # User exists but no profile yet
                return {
                    'user_type': 'client',  # Default to client
                    'username': user.username,
                    'is_authenticated': True,
                    'profile_data': {
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                }
            
            # Determine user type based on profile
            user_type = 'provider' if profile.user_type == 'professional' else 'client'
            
            # Build base context
            context = {
                'user_type': user_type,
                'username': user.username,
                'is_authenticated': True,
                'profile_data': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': profile.phone,
                    'city': profile.city,
                    'state': profile.state,
                }
            }
            
            # Add provider-specific context
            if user_type == 'provider':
                context['profile_data'].update({
                    'business_name': profile.business_name,
                    'specialties': profile.specialties_list,
                    'experience_years': profile.experience_years,
                    'rating': float(profile.rating) if profile.rating else 0.0,
                    'review_count': profile.review_count,
                    'is_verified': profile.is_verified,
                    'is_available': profile.is_available,
                    'total_jobs': profile.total_jobs,
                    'completed_jobs': profile.completed_jobs,
                    'completion_rate': profile.completion_rate,
                    'service_radius': profile.service_radius,
                })
            else:
                # Add client-specific context
                context['profile_data'].update({
                    'address': profile.address,
                    'has_location': bool(profile.latitude and profile.longitude),
                })
            
            logger.info(
                f"Extracted user context",
                extra={
                    'user_id': user.id,
                    'user_type': user_type,
                    'username': user.username
                }
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error extracting user context: {e}", exc_info=True)
            # Return minimal context on error
            return {
                'user_type': 'anonymous',
                'username': None,
                'is_authenticated': False,
                'profile_data': {},
                'error': str(e)
            }
    
    def get_navigation_context(self, current_url, referrer=None):
        """
        Extract navigation context from current page and referrer.
        
        Captures information about the user's current location in the site
        and provides special handling for error pages.
        
        Args:
            current_url: Current page URL
            referrer: Previous page URL (optional)
        
        Returns:
            Dictionary with navigation context including:
            - current_page: Parsed current page information
            - referrer_page: Parsed referrer information (if available)
            - is_error_page: Whether current page is an error page
            - page_type: Type of page (home, services, profile, etc.)
        
        Requirements: 3.2, 3.4
        """
        try:
            context = {
                'current_url': current_url,
                'referrer_url': referrer,
                'current_page': {},
                'referrer_page': {},
                'is_error_page': False,
                'page_type': 'unknown',
                'page_context': {}
            }
            
            # Parse current URL
            if current_url:
                parsed_url = urlparse(current_url)
                path = parsed_url.path.strip('/')
                
                context['current_page'] = {
                    'path': path,
                    'full_path': parsed_url.path,
                    'query': parsed_url.query,
                }
                
                # Determine page type and context
                page_info = self._analyze_page_path(path)
                context['page_type'] = page_info['type']
                context['page_context'] = page_info['context']
                context['is_error_page'] = page_info['is_error']
            
            # Parse referrer URL
            if referrer:
                parsed_referrer = urlparse(referrer)
                referrer_path = parsed_referrer.path.strip('/')
                
                context['referrer_page'] = {
                    'path': referrer_path,
                    'full_path': parsed_referrer.path,
                }
                
                referrer_info = self._analyze_page_path(referrer_path)
                context['referrer_page']['type'] = referrer_info['type']
            
            logger.info(
                f"Extracted navigation context",
                extra={
                    'page_type': context['page_type'],
                    'is_error_page': context['is_error_page'],
                    'current_path': context['current_page'].get('path', '')
                }
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error extracting navigation context: {e}", exc_info=True)
            return {
                'current_url': current_url,
                'referrer_url': referrer,
                'error': str(e)
            }
    
    def _analyze_page_path(self, path):
        """
        Analyze a URL path to determine page type and context.
        
        Args:
            path: URL path (without leading/trailing slashes)
        
        Returns:
            Dictionary with page type, context, and error status
        """
        path_lower = path.lower()
        
        # Error pages
        if any(error in path_lower for error in ['400', '403', '404', '500', 'error']):
            return {
                'type': 'error',
                'is_error': True,
                'context': {
                    'help_needed': True,
                    'suggestion': 'Posso ajudá-lo a encontrar o que procura?'
                }
            }
        
        # Home page
        if not path or path == 'home':
            return {
                'type': 'home',
                'is_error': False,
                'context': {
                    'description': 'Página inicial',
                    'available_actions': ['buscar serviços', 'ver categorias', 'fazer login']
                }
            }
        
        # Services pages
        if 'service' in path_lower or 'servico' in path_lower:
            return {
                'type': 'services',
                'is_error': False,
                'context': {
                    'description': 'Página de serviços',
                    'available_actions': ['buscar serviços', 'filtrar por categoria', 'solicitar serviço']
                }
            }
        
        # Profile pages
        if 'profile' in path_lower or 'perfil' in path_lower:
            return {
                'type': 'profile',
                'is_error': False,
                'context': {
                    'description': 'Página de perfil',
                    'available_actions': ['editar perfil', 'ver histórico', 'configurações']
                }
            }
        
        # Orders/requests pages
        if any(keyword in path_lower for keyword in ['order', 'pedido', 'request', 'solicitac']):
            return {
                'type': 'orders',
                'is_error': False,
                'context': {
                    'description': 'Página de pedidos',
                    'available_actions': ['ver pedidos', 'acompanhar status', 'fazer nova solicitação']
                }
            }
        
        # Dashboard pages
        if 'dashboard' in path_lower or 'painel' in path_lower:
            return {
                'type': 'dashboard',
                'is_error': False,
                'context': {
                    'description': 'Painel de controle',
                    'available_actions': ['ver estatísticas', 'gerenciar solicitações', 'configurações']
                }
            }
        
        # Contact page
        if 'contact' in path_lower or 'contato' in path_lower:
            return {
                'type': 'contact',
                'is_error': False,
                'context': {
                    'description': 'Página de contato',
                    'available_actions': ['enviar mensagem', 'ver informações de contato']
                }
            }
        
        # Authentication pages
        if any(keyword in path_lower for keyword in ['login', 'register', 'signup', 'cadastro']):
            return {
                'type': 'auth',
                'is_error': False,
                'context': {
                    'description': 'Página de autenticação',
                    'available_actions': ['fazer login', 'criar conta', 'recuperar senha']
                }
            }
        
        # Default
        return {
            'type': 'other',
            'is_error': False,
            'context': {
                'description': 'Outra página',
                'available_actions': []
            }
        }
    
    def build_knowledge_base_context(self, query, category=None, limit=5):
        """
        Query knowledge base for relevant information.
        
        Searches the KnowledgeBaseEntry model for entries matching the query
        and returns relevant information to help the AI provide better responses.
        
        Args:
            query: Search query string
            category: Optional category filter ('service', 'faq', 'navigation', etc.)
            limit: Maximum number of entries to return (default: 5)
        
        Returns:
            List of dictionaries with knowledge base entries, each containing:
            - title: Entry title
            - content: Entry content
            - category: Entry category
            - keywords: Associated keywords
        
        Requirements: 2.2
        """
        try:
            if not query:
                return []
            
            # Build query
            q_objects = Q()
            
            # Search in title, content, and keywords
            query_lower = query.lower()
            q_objects |= Q(title__icontains=query_lower)
            q_objects |= Q(content__icontains=query_lower)
            q_objects |= Q(keywords__icontains=query_lower)
            
            # Filter by category if provided
            if category:
                q_objects &= Q(category=category)
            
            # Only active entries
            q_objects &= Q(is_active=True)
            
            # Execute query
            entries = KnowledgeBaseEntry.objects.filter(q_objects).order_by(
                '-usage_count',  # Prioritize frequently used entries
                '-created_at'
            )[:limit]
            
            # Format results
            results = []
            for entry in entries:
                results.append({
                    'entry_id': str(entry.entry_id),
                    'title': entry.title,
                    'content': entry.content,
                    'category': entry.category,
                    'category_display': entry.get_category_display(),
                    'keywords': entry.keywords,
                    'usage_count': entry.usage_count,
                })
                
                # Increment usage counter
                entry.increment_usage()
            
            logger.info(
                f"Knowledge base query",
                extra={
                    'query': query,
                    'category': category,
                    'results_count': len(results)
                }
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}", exc_info=True)
            return []
    
    def get_service_context(self, service_id):
        """
        Get context for a specific service.
        
        Helper method to retrieve detailed information about a service
        for use in chat responses.
        
        Args:
            service_id: ID of the service
        
        Returns:
            Dictionary with service information or None if not found
        """
        try:
            from services.models import Service
            
            service = Service.objects.filter(id=service_id, is_active=True).first()
            if not service:
                return None
            
            return {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category,
                'category_display': service.get_category_display(),
                'base_price': float(service.base_price),
                'estimated_duration': str(service.estimated_duration),
            }
            
        except Exception as e:
            logger.error(f"Error getting service context: {e}", exc_info=True)
            return None
    
    def build_full_context(self, user, current_url, referrer=None, query=None):
        """
        Build complete context combining user, navigation, and knowledge base.
        
        Convenience method that combines all context sources into a single
        comprehensive context dictionary.
        
        Args:
            user: User object
            current_url: Current page URL
            referrer: Previous page URL (optional)
            query: Knowledge base query (optional)
        
        Returns:
            Dictionary with complete context
        """
        try:
            context = {
                'user': self.get_user_context(user),
                'navigation': self.get_navigation_context(current_url, referrer),
                'knowledge_base': [],
                'timestamp': None,
            }
            
            # Add knowledge base context if query provided
            if query:
                context['knowledge_base'] = self.build_knowledge_base_context(query)
            
            # Add timestamp
            from django.utils import timezone
            context['timestamp'] = timezone.now().isoformat()
            
            return context
            
        except Exception as e:
            logger.error(f"Error building full context: {e}", exc_info=True)
            return {
                'user': {'user_type': 'anonymous'},
                'navigation': {},
                'knowledge_base': [],
                'error': str(e)
            }
