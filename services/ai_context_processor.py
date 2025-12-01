from .ml_analytics import WebsiteOptimizer
from .personalization import PersonalizationEngine

def ai_insights(request):
    """
    Context processor to make AI insights available in all templates
    """
    # Only run this for authenticated admin users to avoid performance issues
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        try:
            user_profile = request.user.userprofile
            if user_profile.user_type == 'admin':
                # Initialize AI modules
                optimizer = WebsiteOptimizer()
                personalization = PersonalizationEngine()
                
                # Get analytics data
                analytics_data = optimizer.analyze_user_behavior()
                
                # Get AI suggestions
                suggestions = optimizer.suggest_improvements()
                
                # Get user preferences for current user
                user_preferences = personalization.get_user_preferences(str(request.user.id))
                
                return {
                    'ai_analytics_data': analytics_data,
                    'ai_suggestions': suggestions[:3],  # Limit to top 3 suggestions
                    'user_preferences': user_preferences
                }
        except Exception:
            # Silently fail to avoid breaking the application
            pass
    
    # Return empty context if not admin or if there's an error
    return {
        'ai_analytics_data': None,
        'ai_suggestions': [],
        'user_preferences': None
    }