import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import Order, CustomService, UserProfile
from services.ml_analytics import WebsiteOptimizer
from services.personalization import PersonalizationEngine

class Command(BaseCommand):
    help = 'Process provider analytics and generate AI insights'

    def handle(self, *args, **options):
        # Initialize AI modules
        optimizer = WebsiteOptimizer()
        personalization = PersonalizationEngine()
        
        # Get all provider users
        provider_users = User.objects.filter(userprofile__user_type='professional')
        
        for provider in provider_users:
            try:
                # Collect provider data
                provider_orders = Order.objects.filter(professional=provider)
                custom_services = CustomService.objects.filter(provider=provider)
                
                # Calculate provider metrics
                total_orders = provider_orders.count()
                completed_orders = provider_orders.filter(status='completed').count()
                total_earnings = sum([float(order.total_price) for order in provider_orders if order.total_price])
                
                # Simulate user interaction data collection
                optimizer.collect_user_data(
                    user_id=str(provider.id),
                    page_visited=f"/provider/{provider.id}",
                    time_spent=180,  # Simulate 3 minutes
                    actions_taken=["view_dashboard", "check_orders"],
                    converted=completed_orders > 0
                )
                
                # Record user interactions for personalization
                personalization.record_user_interaction(
                    user_id=str(provider.id),
                    page_visited="/provider-dashboard",
                    interaction_type="view"
                )
                
                # Add custom services as interactions
                for service in custom_services:
                    personalization.record_user_interaction(
                        user_id=str(provider.id),
                        page_visited="/add-custom-service",
                        interaction_type="create",
                        content_id=f"service_{service.id}"
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed analytics for provider {provider.username}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing analytics for provider {provider.username}: {str(e)}'
                    )
                )
        
        # Save AI data
        optimizer.save_data()
        personalization.save_data()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully processed all provider analytics')
        )