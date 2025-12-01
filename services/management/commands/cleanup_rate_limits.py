"""
Management command to clean up old rate limit records.

This command should be run periodically (e.g., daily via cron) to prevent
the RateLimitRecord table from growing indefinitely.
"""

from django.core.management.base import BaseCommand
from services.models import RateLimitRecord
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Clean up old rate limit records to free up database space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Delete records older than this many days (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Find records older than the cutoff date
        old_records = RateLimitRecord.objects.filter(created_at__lt=cutoff_date)
        count = old_records.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No old rate limit records to delete'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Would delete {count} rate limit records older than {days} days '
                    f'(older than {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")})'
                )
            )
            
            # Show some statistics
            exceeded_count = old_records.filter(exceeded=True).count()
            self.stdout.write(f'  - Records with violations: {exceeded_count}')
            self.stdout.write(f'  - Records without violations: {count - exceeded_count}')
            return
        
        # Delete the old records
        exceeded_count = old_records.filter(exceeded=True).count()
        old_records.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {count} rate limit records older than {days} days'
            )
        )
        self.stdout.write(f'  - Records with violations: {exceeded_count}')
        self.stdout.write(f'  - Records without violations: {count - exceeded_count}')
