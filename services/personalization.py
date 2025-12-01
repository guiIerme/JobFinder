import json
import os
from datetime import datetime
from collections import defaultdict, Counter

class PersonalizationEngine:
    def __init__(self):
        self.user_profiles_file = 'user_profiles.json'
        self.content_preferences_file = 'content_preferences.json'
        self.load_data()
    
    def load_data(self):
        """Load user profiles and content preferences"""
        if os.path.exists(self.user_profiles_file):
            with open(self.user_profiles_file, 'r') as f:
                self.user_profiles = json.load(f)
        else:
            self.user_profiles = {}
        
        if os.path.exists(self.content_preferences_file):
            with open(self.content_preferences_file, 'r') as f:
                self.content_preferences = json.load(f)
        else:
            self.content_preferences = {}
    
    def save_data(self):
        """Save user profiles and content preferences"""
        with open(self.user_profiles_file, 'w') as f:
            json.dump(self.user_profiles, f, indent=2)
        
        with open(self.content_preferences_file, 'w') as f:
            json.dump(self.content_preferences, f, indent=2)
    
    def create_user_profile(self, user_id, user_data):
        """Create or update user profile"""
        profile = {
            'user_id': user_id,
            'preferences': user_data.get('preferences', {}),
            'behavior_history': [],
            'last_updated': datetime.now().isoformat()
        }
        
        self.user_profiles[user_id] = profile
        self.save_data()
        return profile
    
    def record_user_interaction(self, user_id, page_visited, interaction_type, content_id=None, timestamp=None):
        """Record user interaction for learning"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        interaction = {
            'page': page_visited,
            'type': interaction_type,  # view, click, scroll, submit, etc.
            'content_id': content_id,
            'timestamp': timestamp
        }
        
        # Update user profile
        if user_id in self.user_profiles:
            self.user_profiles[user_id]['behavior_history'].append(interaction)
            self.user_profiles[user_id]['last_updated'] = timestamp
        else:
            # Create basic profile if it doesn't exist
            self.create_user_profile(user_id, {})
            self.user_profiles[user_id]['behavior_history'].append(interaction)
        
        # Update content preferences
        content_key = f"{page_visited}:{content_id}" if content_id else page_visited
        if content_key not in self.content_preferences:
            self.content_preferences[content_key] = {
                'views': 0,
                'clicks': 0,
                'interactions': []
            }
        
        if interaction_type == 'view':
            self.content_preferences[content_key]['views'] += 1
        elif interaction_type == 'click':
            self.content_preferences[content_key]['clicks'] += 1
        
        self.content_preferences[content_key]['interactions'].append({
            'user_id': user_id,
            'type': interaction_type,
            'timestamp': timestamp
        })
        
        self.save_data()
    
    def get_user_preferences(self, user_id):
        """Get user preferences based on behavior history"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        behavior_history = profile['behavior_history']
        
        # Analyze preferences
        preferences = {
            'favorite_categories': [],
            'preferred_content_types': [],
            'active_times': [],
            'engagement_level': 'low'
        }
        
        # Category preferences
        category_count = defaultdict(int)
        for interaction in behavior_history:
            page = interaction['page']
            # Extract category from page path
            if '/services/' in page:
                category = page.split('/')[2] if len(page.split('/')) > 2 else 'general'
                category_count[category] += 1
        
        # Get top 3 categories
        sorted_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)
        preferences['favorite_categories'] = [cat for cat, count in sorted_categories[:3]]
        
        # Content type preferences
        content_types = defaultdict(int)
        for interaction in behavior_history:
            if interaction['content_id']:
                content_type = interaction['content_id'].split('_')[0] if '_' in interaction['content_id'] else 'general'
                content_types[content_type] += 1
        
        sorted_content_types = sorted(content_types.items(), key=lambda x: x[1], reverse=True)
        preferences['preferred_content_types'] = [ctype for ctype, count in sorted_content_types[:3]]
        
        # Active times (hour of day)
        hours = []
        for interaction in behavior_history:
            try:
                hour = datetime.fromisoformat(interaction['timestamp']).hour
                hours.append(hour)
            except:
                continue
        
        if hours:
            hour_counts = Counter(hours)
            most_active_hours = [hour for hour, count in hour_counts.most_common(3)]
            preferences['active_times'] = most_active_hours
        
        # Engagement level
        total_interactions = len(behavior_history)
        if total_interactions > 20:
            preferences['engagement_level'] = 'high'
        elif total_interactions > 5:
            preferences['engagement_level'] = 'medium'
        else:
            preferences['engagement_level'] = 'low'
        
        return preferences
    
    def recommend_content(self, user_id, current_page=None, limit=5):
        """Recommend content based on user preferences"""
        preferences = self.get_user_preferences(user_id)
        recommendations = []
        
        # If we have user preferences, use them
        if preferences['favorite_categories']:
            # Recommend content from favorite categories
            for category in preferences['favorite_categories']:
                category_content = [
                    content for content in self.content_preferences.keys()
                    if category in content
                ]
                
                # Sort by popularity (views + clicks)
                ranked_content = sorted(
                    category_content,
                    key=lambda x: self.content_preferences[x]['views'] + self.content_preferences[x]['clicks'],
                    reverse=True
                )
                
                recommendations.extend(ranked_content[:limit//len(preferences['favorite_categories']) + 1])
        
        # If no recommendations based on preferences, recommend popular content
        if not recommendations:
            # Get most popular content overall
            popular_content = sorted(
                self.content_preferences.items(),
                key=lambda x: x[1]['views'] + x[1]['clicks'],
                reverse=True
            )
            recommendations = [content[0] for content in popular_content[:limit]]
        
        # Remove current page from recommendations
        if current_page:
            recommendations = [rec for rec in recommendations if current_page not in rec]
        
        return recommendations[:limit]
    
    def personalize_page_content(self, user_id, page_template):
        """Personalize page content based on user preferences"""
        preferences = self.get_user_preferences(user_id)
        
        # Customize based on engagement level
        if preferences['engagement_level'] == 'high':
            # Show advanced features and detailed content
            page_template['show_advanced_features'] = True
            page_template['content_depth'] = 'detailed'
        elif preferences['engagement_level'] == 'medium':
            # Show standard content
            page_template['show_advanced_features'] = False
            page_template['content_depth'] = 'standard'
        else:
            # Show simplified content for new users
            page_template['show_advanced_features'] = False
            page_template['content_depth'] = 'simple'
        
        # Add personalized recommendations
        recommendations = self.recommend_content(user_id)
        page_template['recommendations'] = recommendations
        
        # Customize based on favorite categories
        if preferences['favorite_categories']:
            page_template['featured_categories'] = preferences['favorite_categories'][:2]
        
        return page_template
    
    def get_ab_test_variant(self, user_id, test_name):
        """Determine A/B test variant for user"""
        # Simple hash-based assignment for A/B testing
        hash_value = hash(f"{user_id}_{test_name}") % 100
        if hash_value < 50:
            return 'A'
        else:
            return 'B'

# Usage example
if __name__ == "__main__":
    personalization = PersonalizationEngine()
    
    # Record some user interactions
    personalization.record_user_interaction(
        user_id="user_123",
        page_visited="/services/search_new.html",
        interaction_type="view"
    )
    
    personalization.record_user_interaction(
        user_id="user_123",
        page_visited="/services/search_new.html",
        interaction_type="click",
        content_id="service_card_456"
    )
    
    # Get user preferences
    preferences = personalization.get_user_preferences("user_123")
    print("User Preferences:", preferences)
    
    # Get content recommendations
    recommendations = personalization.recommend_content("user_123")
    print("Content Recommendations:", recommendations)