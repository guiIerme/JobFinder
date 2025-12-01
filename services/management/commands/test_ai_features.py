import json
from django.core.management.base import BaseCommand
from services.views import generate_performance_insights, predict_revenue, generate_personalized_recommendations

class Command(BaseCommand):
    help = 'Test AI features'

    def handle(self, *args, **options):
        # Test performance insights
        user_data = {
            'revenue_growth': 18,
            'on_time_completion': 92,
            'average_rating': 4.7,
            'completion_rate': 85
        }
        
        insights = generate_performance_insights(user_data)
        self.stdout.write(f"Performance Insights: {json.dumps(insights, indent=2, ensure_ascii=False)}")
        
        # Test revenue prediction
        historical_data = [1200, 1900, 1500, 2200, 1800, 2500]
        provider_profile = {
            'services': ['electrical', 'plumbing'],
            'competitiveness': 0.65,
            'total_orders': 50,
            'completed_orders': 45,
            'average_rating': 4.7
        }
        
        revenue_prediction = predict_revenue(historical_data, provider_profile)
        self.stdout.write(f"Revenue Prediction: {json.dumps(revenue_prediction, indent=2, ensure_ascii=False)}")
        
        # Test personalized recommendations
        market_data = {}
        # Fix the provider profile structure for testing
        provider_profile_fixed = {
            'services': [],  # Empty list for testing
            'competitiveness': 0.65,
            'total_orders': 50,
            'completed_orders': 45,
            'average_rating': 4.7
        }
        recommendations = generate_personalized_recommendations(provider_profile_fixed, market_data)
        self.stdout.write(f"Recommendations: {json.dumps(recommendations, indent=2, ensure_ascii=False)}")
        
        self.stdout.write('Successfully tested all AI features')