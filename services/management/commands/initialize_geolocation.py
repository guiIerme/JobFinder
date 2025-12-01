from django.core.management.base import BaseCommand
from services.models import UserProfile

class Command(BaseCommand):
    help = 'Initialize geolocation fields for existing user profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the command without making changes to the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Initializing geolocation fields for user profiles...')
        
        # Get all user profiles
        profiles = UserProfile.objects.all()
        self.stdout.write(f'Found {profiles.count()} user profiles')
        
        # Update profiles with default geolocation values
        updated_count = 0
        for profile in profiles:
            if profile.latitude is None or profile.longitude is None:
                if not dry_run:
                    profile.latitude = None
                    profile.longitude = None
                    profile.save(update_fields=['latitude', 'longitude'])
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized geolocation fields for {updated_count} user profiles!'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    'This was a dry run. No changes were made to the database.'
                )
            )