from .models import UserProfile


class ProfileTrackingMiddleware:
    """
    Middleware to attach the request object to UserProfile instances
    for tracking purposes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach the request to the thread-local storage
        # so it can be accessed in signals
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # If the view is updating a user profile, attach the request to the profile instance
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Try to get the user's profile
                profile = request.user.userprofile
                # Attach the request to the profile instance
                profile._request = request
            except UserProfile.DoesNotExist:
                # If the user doesn't have a profile yet, that's okay
                pass
        return None