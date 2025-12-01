import json
import os
from django.core.management.base import BaseCommand
from services.ml_analytics import WebsiteOptimizer
from services.personalization import PersonalizationEngine
from services.content_generator import ContentGenerator

class Command(BaseCommand):
    help = 'Process collected analytics data and generate AI insights'

    def add_arguments(self, parser):
        parser.add_argument(
            '--generate-report',
            action='store_true',
            help='Generate a detailed analytics report',
        )
        parser.add_argument(
            '--optimize-content',
            action='store_true',
            help='Optimize website content based on analytics',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Processing AI analytics data...')
        )

        # Initialize AI modules
        optimizer = WebsiteOptimizer()
        personalization = PersonalizationEngine()
        content_generator = ContentGenerator()

        # Analyze user behavior
        analysis = optimizer.analyze_user_behavior()
        
        if analysis:
            self.stdout.write(
                self.style.SUCCESS('User Behavior Analysis:')
            )
            self.stdout.write(f"  Total Interactions: {analysis['total_interactions']}")
            self.stdout.write(f"  Conversion Rate: {analysis['conversion_rate']:.2%}")
            self.stdout.write(f"  Average Time Spent: {analysis['avg_time_spent']:.1f} seconds")
            self.stdout.write(f"  Average Actions: {analysis['avg_actions']:.1f}")
            self.stdout.write(f"  Most Popular Page: {analysis['most_popular_page']}")
            
            # Generate improvement suggestions
            suggestions = optimizer.suggest_improvements()
            self.stdout.write(
                self.style.SUCCESS('\nAI Improvement Suggestions:')
            )
            for i, suggestion in enumerate(suggestions, 1):
                self.stdout.write(f"  {i}. {suggestion}")
        else:
            self.stdout.write(
                self.style.WARNING('Not enough data to provide analysis. Continue collecting user interactions.')
            )

        # Generate personalized content recommendations
        self.stdout.write(
            self.style.SUCCESS('\nGenerating personalized content recommendations...')
        )
        
        # For demonstration, we'll use a sample user ID
        sample_user_id = "sample_user"
        
        # Get user preferences
        preferences = personalization.get_user_preferences(sample_user_id)
        if preferences:
            self.stdout.write(
                self.style.SUCCESS('User Preferences:')
            )
            self.stdout.write(f"  Favorite Categories: {', '.join(preferences['favorite_categories'])}")
            self.stdout.write(f"  Preferred Content Types: {', '.join(preferences['preferred_content_types'])}")
            self.stdout.write(f"  Active Times: {', '.join(map(str, preferences['active_times']))}")
            self.stdout.write(f"  Engagement Level: {preferences['engagement_level']}")
            
            # Generate content recommendations
            recommendations = personalization.recommend_content(sample_user_id)
            self.stdout.write(
                self.style.SUCCESS('\nContent Recommendations:')
            )
            for i, recommendation in enumerate(recommendations, 1):
                self.stdout.write(f"  {i}. {recommendation}")
        else:
            self.stdout.write(
                self.style.WARNING('No user preferences data available.')
            )

        # Generate sample content
        self.stdout.write(
            self.style.SUCCESS('\nGenerating sample content...')
        )
        
        sample_service_types = ["Elétrica", "Encanamento", "Limpeza", "Pintura"]
        for service_type in sample_service_types:
            description = content_generator.generate_service_description(service_type)
            testimonial = content_generator.generate_testimonial(service_type)
            faq = content_generator.generate_faq_pair(service_type)
            
            self.stdout.write(f"\n{service_type}:")
            self.stdout.write(f"  Description: {description}")
            self.stdout.write(f"  Testimonial: {testimonial['testimonial']} (Rating: {testimonial['rating']})")
            self.stdout.write(f"  FAQ: {faq['question']} - {faq['answer']}")

        # Generate optimization report if requested
        if options['generate_report']:
            self.generate_report(optimizer, personalization, content_generator)

        # Optimize content if requested
        if options['optimize_content']:
            self.optimize_content(content_generator)

        self.stdout.write(
            self.style.SUCCESS('\nAI analytics processing completed successfully!')
        )

    def generate_report(self, optimizer, personalization, content_generator):
        """Generate a detailed analytics report"""
        self.stdout.write(
            self.style.SUCCESS('\nGenerating detailed analytics report...')
        )
        
        # This would typically save to a file or database
        report_data = {
            'timestamp': '2025-10-14',
            'analytics_summary': optimizer.analyze_user_behavior(),
            'improvement_suggestions': optimizer.suggest_improvements(),
            'sample_content': {
                'electrician': content_generator.generate_service_description("Elétrica"),
                'plumber': content_generator.generate_service_description("Encanamento"),
                'cleaner': content_generator.generate_service_description("Limpeza")
            }
        }
        
        # Save report to file
        with open('ai_analytics_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS('Report saved to ai_analytics_report.json')
        )

    def optimize_content(self, content_generator):
        """Optimize website content based on best practices"""
        self.stdout.write(
            self.style.SUCCESS('\nOptimizing website content...')
        )
        
        # Example content optimization
        sample_content = """
        Nossa empresa oferece serviços de reparo residencial de alta qualidade. 
        Com mais de 10 anos de experiência, nossos profissionais estão prontos 
        para atender suas necessidades com rapidez e eficiência.
        """
        
        optimized_content = content_generator.optimize_existing_content(
            sample_content, 
            ['clarity', 'engagement', 'seo']
        )
        
        self.stdout.write(
            self.style.SUCCESS('Content optimization completed:')
        )
        self.stdout.write(f"Original: {sample_content.strip()}")
        self.stdout.write(f"Optimized: {optimized_content.strip()}")