import json
import os
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

class AIAnalyticsMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.data_file = 'analytics_data.json'
        self.load_data()
    
    def load_data(self):
        """Load existing analytics data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.analytics_data = json.load(f)
        else:
            self.analytics_data = {
                'user_interactions': [],
                'page_performance': [],
                'conversion_rates': []
            }
    
    def save_data(self):
        """Save analytics data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.analytics_data, f, indent=2)
    
    def __call__(self, request):
        # Record request start time for performance tracking
        request.start_time = datetime.now()
        
        response = self.get_response(request)
        
        # Collect analytics data after response
        self.collect_analytics(request, response)
        
        return response
    
    def collect_analytics(self, request, response):
        """Collect user interaction data for AI analysis"""
        try:
            # Skip if it's an admin page or static file
            if (request.path.startswith('/admin/') or 
                request.path.startswith('/static/') or 
                request.path.startswith('/media/')):
                return
            
            # Get user ID (if authenticated)
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            
            # Calculate time spent on page
            time_spent = 0
            if hasattr(request, 'start_time'):
                time_spent = (datetime.now() - request.start_time).total_seconds()
            
            # Determine if this was a conversion (successful form submission, purchase, etc.)
            converted = False
            conversion_indicators = [
                'success', 'confirm', 'complete', 'thank', 'order-confirmation'
            ]
            for indicator in conversion_indicators:
                if indicator in request.path or indicator in str(response.content).lower():
                    converted = True
                    break
            
            # Record interaction data
            interaction_data = {
                'user_id': str(user_id),
                'page_visited': request.path,
                'time_spent': time_spent,
                'actions_taken': self.get_user_actions(request),
                'converted': converted,
                'timestamp': datetime.now().isoformat(),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self.get_client_ip(request),
                'response_status': response.status_code
            }
            
            self.analytics_data['user_interactions'].append(interaction_data)
            
            # Save data periodically (every 10 interactions)
            if len(self.analytics_data['user_interactions']) % 10 == 0:
                self.save_data()
                
        except Exception as e:
            # Silently fail to avoid breaking the application
            pass
    
    def get_user_actions(self, request):
        """Extract user actions from request"""
        actions = []
        
        # Check for form submissions
        if request.method == 'POST':
            actions.append('form_submit')
        
        # Check for search queries
        if 'search' in request.GET or 'q' in request.GET:
            actions.append('search')
        
        # Check for filter usage
        filter_params = ['category', 'price_min', 'price_max', 'rating', 'location']
        for param in filter_params:
            if param in request.GET:
                actions.append('filter')
                break
        
        # Check for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            actions.append('ajax_request')
        
        return actions
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip