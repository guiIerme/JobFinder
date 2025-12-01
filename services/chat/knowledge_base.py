"""
Knowledge Base - Service Information and FAQs

This module manages the knowledge base for chat responses,
including service information, FAQs, and help content.
"""

from django.db.models import Q
from services.chat_models import KnowledgeBaseEntry
from services.models import Service


class KnowledgeBase:
    """
    Manages knowledge base for chat system.
    
    Responsibilities:
    - Search knowledge base entries
    - Retrieve service information
    - Provide FAQs and help content
    
    Requirements: 2.2, 2.4, 3.3, 6.2
    """
    
    def search(self, query, category=None):
        """
        Search knowledge base with keyword matching.
        
        Searches through knowledge base entries by matching keywords
        and content. Supports optional category filtering.
        
        Args:
            query: Search query string
            category: Optional category filter ('service', 'faq', 'navigation', 'policy', 'troubleshooting')
        
        Returns:
            QuerySet of matching KnowledgeBaseEntry objects, ordered by usage count
            
        Requirements: 2.2
        """
        if not query:
            return KnowledgeBaseEntry.objects.none()
        
        # Build base query for active entries
        queryset = KnowledgeBaseEntry.objects.filter(is_active=True)
        
        # Apply category filter if provided
        if category:
            queryset = queryset.filter(category=category)
        
        # Search in title, content, and keywords
        search_query = Q(title__icontains=query) | Q(content__icontains=query)
        
        # Also search in keywords JSON field
        # Check if any keyword contains the query string
        queryset = queryset.filter(search_query)
        
        # Order by usage count (most used first) and then by creation date
        queryset = queryset.order_by('-usage_count', '-created_at')
        
        return queryset
    
    def get_service_info(self, service_id):
        """
        Get detailed service information including pricing and availability.
        
        Retrieves comprehensive information about a specific service,
        including base price, estimated duration, category, and description.
        
        Args:
            service_id: Service ID (integer)
        
        Returns:
            Dictionary with service information or None if not found:
            {
                'id': int,
                'name': str,
                'description': str,
                'category': str,
                'category_display': str,
                'base_price': Decimal,
                'estimated_duration': timedelta,
                'estimated_duration_hours': float,
                'is_active': bool,
                'knowledge_entries': list of related knowledge base entries
            }
            
        Requirements: 2.4
        """
        try:
            service = Service.objects.get(id=service_id, is_active=True)
            
            # Get related knowledge base entries
            knowledge_entries = []
            for entry in service.knowledge_entries.filter(is_active=True):
                knowledge_entries.append({
                    'title': entry.title,
                    'content': entry.content,
                    'category': entry.category
                })
            
            # Calculate duration in hours
            duration_hours = service.estimated_duration.total_seconds() / 3600
            
            return {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category,
                'category_display': service.get_category_display(),
                'base_price': service.base_price,
                'estimated_duration': service.estimated_duration,
                'estimated_duration_hours': duration_hours,
                'is_active': service.is_active,
                'knowledge_entries': knowledge_entries
            }
        except Service.DoesNotExist:
            return None
    
    def get_faq(self, topic):
        """
        Get FAQ entries for a specific topic.
        
        Retrieves frequently asked questions related to a topic.
        Searches both in title and keywords for matches.
        
        Args:
            topic: FAQ topic or keyword to search for
        
        Returns:
            List of dictionaries with FAQ information:
            [
                {
                    'id': UUID,
                    'title': str,
                    'content': str,
                    'keywords': list,
                    'usage_count': int
                },
                ...
            ]
            
        Requirements: 3.3, 6.2
        """
        if not topic:
            # Return general FAQs if no topic specified
            entries = KnowledgeBaseEntry.objects.filter(
                category='faq',
                is_active=True
            ).order_by('-usage_count')[:10]
        else:
            # Search for topic in title and content
            entries = KnowledgeBaseEntry.objects.filter(
                category='faq',
                is_active=True
            ).filter(
                Q(title__icontains=topic) | Q(content__icontains=topic)
            ).order_by('-usage_count')
        
        # Convert to list of dictionaries
        faq_list = []
        for entry in entries:
            faq_list.append({
                'id': str(entry.entry_id),
                'title': entry.title,
                'content': entry.content,
                'keywords': entry.keywords,
                'usage_count': entry.usage_count
            })
            # Increment usage counter
            entry.increment_usage()
        
        return faq_list
    
    def get_navigation_help(self, page):
        """
        Get navigation help for a specific page.
        
        Provides page-specific guidance to help users navigate
        and use features on different pages of the platform.
        
        Args:
            page: Page identifier (e.g., 'home', 'services', 'profile', 'orders')
        
        Returns:
            Dictionary with navigation help or None if not found:
            {
                'id': UUID,
                'title': str,
                'content': str,
                'keywords': list
            }
            
        Requirements: 3.3, 6.2
        """
        if not page:
            return None
        
        # Search for navigation entries matching the page
        # First try to match by title
        entry = KnowledgeBaseEntry.objects.filter(
            category='navigation',
            is_active=True,
            title__icontains=page
        ).first()
        
        # If not found by title, search through keywords manually
        if not entry:
            entries = KnowledgeBaseEntry.objects.filter(
                category='navigation',
                is_active=True
            )
            for e in entries:
                if page.lower() in [k.lower() for k in e.keywords]:
                    entry = e
                    break
        
        if entry:
            # Increment usage counter
            entry.increment_usage()
            
            return {
                'id': str(entry.entry_id),
                'title': entry.title,
                'content': entry.content,
                'keywords': entry.keywords
            }
        
        return None
