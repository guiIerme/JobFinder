from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import UserProfile, Review, Order

class Command(BaseCommand):
    help = 'Initialize the review system and update user profiles with rating information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the command without making changes to the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Initializing review system...')
        
        # Create UserProfile for users who don't have one
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        self.stdout.write(f'Found {users_without_profile.count()} users without profiles')
        
        if not dry_run:
            for user in users_without_profile:
                UserProfile.objects.create(user=user, user_type='customer')
                self.stdout.write(f'Created profile for user {user.username}')
        
        # Update existing profiles with default values for new fields
        profiles_without_rating = UserProfile.objects.filter(rating__isnull=True)
        self.stdout.write(f'Found {profiles_without_rating.count()} profiles without rating fields')
        
        if not dry_run:
            updated_count = profiles_without_rating.update(rating=0.00, review_count=0)
            self.stdout.write(f'Updated {updated_count} profiles with default rating values')
        
        # Calculate ratings for professionals based on existing reviews (if any)
        self.stdout.write('Calculating ratings for professionals...')
        
        # In a real implementation, you would calculate ratings based on existing data
        # For now, we'll just show what would be done
        
        professionals = UserProfile.objects.filter(user_type='professional')
        self.stdout.write(f'Found {professionals.count()} professionals')
        
        for profile in professionals:
            # In a real implementation, you would calculate the actual rating
            # For now, we'll just show the professional info
            self.stdout.write(f'Professional: {profile.user.username} - Current rating: {profile.rating}')
        
        self.stdout.write(
            self.style.SUCCESS(
                'Review system initialization completed successfully!'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    'This was a dry run. No changes were made to the database.'
                )
            )