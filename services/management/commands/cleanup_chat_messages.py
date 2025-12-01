from django.core.management.base import BaseCommand
from services.models import Message
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Clean up old chat messages to free up database space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete messages older than this many days (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=options['days'])
        
        # Find messages older than the cutoff date
        old_messages = Message.objects.filter(timestamp__lt=cutoff_date)
        count = old_messages.count()
        
        if options['dry_run']:
            self.stdout.write(
                f'Would delete {count} messages older than {options["days"]} days '
                f'(older than {cutoff_date.strftime("%Y-%m-%d")})'
            )
            return
        
        if count == 0:
            self.stdout.write('No old messages to delete')
            return
        
        # Delete the old messages
        old_messages.delete()
        
        self.stdout.write(
            f'Successfully deleted {count} messages older than {options["days"]} days'
        )