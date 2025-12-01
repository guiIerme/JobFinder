from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Reset the database and recreate it with fresh migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            'This will delete the current database and recreate it from scratch.'
        )
        
        if not options['no_input']:
            confirm = input('Are you sure you want to do this? Type "yes" to continue: ')
            if confirm != 'yes':
                self.stdout.write('Reset cancelled.')
                return
        
        # Delete the database file if using SQLite
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            db_name = settings.DATABASES['default']['NAME']
            if os.path.exists(db_name):
                os.remove(db_name)
                self.stdout.write(f'Deleted database file: {db_name}')
            else:
                self.stdout.write(f'Database file not found: {db_name}')
        
        # Run migrations to create a fresh database
        self.stdout.write('Running migrations...')
        call_command('migrate', verbosity=1)
        
        # Create a superuser
        self.stdout.write('Creating superuser...')
        call_command('createsuperuser', 
                    '--username', 'admin',
                    '--email', 'admin@example.com',
                    '--noinput')
        
        # Set the superuser password
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username='admin')
            user.set_password('admin123')
            user.save()
            self.stdout.write('Superuser created with username: admin and password: admin123')
        except User.DoesNotExist:
            self.stdout.write('Failed to set superuser password')
        
        self.stdout.write(
            'Database reset completed successfully!'
        )