import json
import os
import statistics
from datetime import datetime, timedelta
from collections import defaultdict

class WebsiteOptimizer:
    def __init__(self):
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
    
    def collect_user_data(self, user_id, page_visited, time_spent, actions_taken, converted=False):
        """Collect user interaction data"""
        interaction_data = {
            'user_id': user_id,
            'page_visited': page_visited,
            'time_spent': time_spent,
            'actions_taken': actions_taken,
            'converted': converted,
            'timestamp': datetime.now().isoformat()
        }
        self.analytics_data['user_interactions'].append(interaction_data)
        self.save_data()
    
    def analyze_user_behavior(self):
        """Analyze user behavior patterns"""
        if not self.analytics_data['user_interactions']:
            return None
        
        interactions = self.analytics_data['user_interactions']
        
        # Calculate basic metrics
        total_interactions = len(interactions)
        conversions = sum(1 for i in interactions if i['converted'])
        conversion_rate = conversions / total_interactions if total_interactions > 0 else 0
        
        # Time spent analysis
        times_spent = [i['time_spent'] for i in interactions]
        avg_time_spent = statistics.mean(times_spent) if times_spent else 0
        
        # Actions analysis
        actions_counts = [len(i['actions_taken']) for i in interactions]
        avg_actions = statistics.mean(actions_counts) if actions_counts else 0
        
        # Page popularity
        page_visits = defaultdict(int)
        for interaction in interactions:
            page_visits[interaction['page_visited']] += 1
        
        most_popular_page = max(page_visits.items(), key=lambda x: x[1])[0] if page_visits else None
        
        return {
            'total_interactions': total_interactions,
            'conversion_rate': conversion_rate,
            'avg_time_spent': avg_time_spent,
            'avg_actions': avg_actions,
            'most_popular_page': most_popular_page,
            'page_visits': dict(page_visits)
        }
    
    def suggest_improvements(self):
        """Suggest website improvements based on analytics"""
        analysis = self.analyze_user_behavior()
        if not analysis:
            return ["Not enough data to provide suggestions. Continue collecting user interactions."]
        
        suggestions = []
        
        # Conversion rate suggestions
        if analysis['conversion_rate'] < 0.05:  # Less than 5% conversion
            suggestions.append("Consider simplifying the conversion process - reduce steps or form fields")
            suggestions.append("Add more prominent call-to-action buttons")
            suggestions.append("Improve page loading speed, especially for conversion pages")
        elif analysis['conversion_rate'] > 0.15:  # More than 15% conversion
            suggestions.append("Excellent conversion rate! Consider testing premium features or upsells")
        
        # Time spent suggestions
        if analysis['avg_time_spent'] < 30:  # Less than 30 seconds
            suggestions.append("Users are leaving quickly - improve page content relevance")
            suggestions.append("Add more engaging visuals or interactive elements")
        elif analysis['avg_time_spent'] > 300:  # More than 5 minutes
            suggestions.append("Users are engaged! Consider adding related content or recommendations")
        
        # Action-based suggestions
        if analysis['avg_actions'] < 2:
            suggestions.append("Users aren't interacting much - add more interactive elements")
            suggestions.append("Improve navigation clarity and accessibility")
        elif analysis['avg_actions'] > 10:
            suggestions.append("High user engagement! Consider adding advanced features or personalization")
        
        # Page-specific suggestions
        if analysis['most_popular_page']:
            suggestions.append(f"Most popular page: {analysis['most_popular_page']} - consider promoting it more prominently")
        
        return suggestions
    
    def auto_optimize_content(self, page_content, user_engagement_metrics):
        """Automatically optimize content based on engagement metrics"""
        suggestions = []
        
        if user_engagement_metrics.get('bounce_rate', 0) > 0.7:
            suggestions.append("High bounce rate detected - consider improving headline clarity")
            suggestions.append("Add more visual elements above the fold")
        
        if user_engagement_metrics.get('time_on_page', 0) < 30:
            suggestions.append("Short visit duration - content may need to be more engaging")
            suggestions.append("Break up long text with subheadings and bullet points")
        
        return suggestions

# Usage example
if __name__ == "__main__":
    optimizer = WebsiteOptimizer()
    
    # Example of collecting user data
    optimizer.collect_user_data(
        user_id="user_123",
        page_visited="/services/search_new.html",
        time_spent=120,  # 2 minutes
        actions_taken=["search", "filter", "view_profile"],
        converted=True
    )
    
    # Get improvement suggestions
    suggestions = optimizer.suggest_improvements()
    print("Website Improvement Suggestions:")
    for suggestion in suggestions:
        print(f"- {suggestion}")