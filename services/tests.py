"""
Unit tests for the Job Finder platform.
This file includes tests for dark mode functionality.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile

class DarkModeTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a user profile
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            user_type='client',
            phone='11999999999',
            dark_mode=False  # Default to light mode
        )
    
    def test_dark_mode_preference_saved(self):
        """Test that dark mode preference is saved correctly"""
        # Change dark mode preference
        self.user_profile.dark_mode = True
        self.user_profile.save()
        
        # Retrieve and verify
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(updated_profile.dark_mode)
    
    def test_dark_mode_default_value(self):
        """Test that dark mode defaults to False"""
        self.assertFalse(self.user_profile.dark_mode)
    
    def test_toggle_dark_mode(self):
        """Test toggling dark mode preference"""
        # Initial state should be False
        self.assertFalse(self.user_profile.dark_mode)
        
        # Toggle to True
        self.user_profile.dark_mode = True
        self.user_profile.save()
        self.assertTrue(UserProfile.objects.get(user=self.user).dark_mode)
        
        # Toggle back to False
        self.user_profile.dark_mode = False
        self.user_profile.save()
        self.assertFalse(UserProfile.objects.get(user=self.user).dark_mode)

# Additional tests for other components would go here
