"""
Custom pagination classes for API
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination configuration
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class OptimizedPagination(PageNumberPagination):
    """
    Optimized pagination with complete metadata for better client experience.
    
    Features:
    - Default page size of 20 items
    - Configurable page size via query parameter (10-100 items)
    - Complete metadata including total pages, current page, and navigation links
    - Optimized for performance with minimal database queries
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return paginated response with complete metadata.
        
        Response format:
        {
            'count': total number of items,
            'next': URL to next page (or null),
            'previous': URL to previous page (or null),
            'total_pages': total number of pages,
            'current_page': current page number,
            'page_size': items per page,
            'results': list of items
        }
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'results': data
        })
