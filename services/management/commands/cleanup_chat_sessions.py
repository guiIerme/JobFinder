"""
Django management command to clean up old chat sessions.

This command closes chat sessions that haven't been updated in the last 24 hours.
It should be run periodically via a cron job or task scheduler.

Usage:
    python manage.py cleanup_chat_sessions
    python manage.py cleanup_chat_sessions --hours 48
    python manage.py cleanup_chat_sessions --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from services.chat_models import ChatSession
from services.chat.manager import ChatManager


class Command(BaseCommand):
    help = 'Clean up old chat sessions (closes sessions older than specified hours)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Close sessions older than this many hours (default: 24)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually cleaning',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        # Calculate cutoff time
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Find active sessions older than cutoff
        old_sessions = ChatSession.objects.filter(
            is_active=True,
            updated_at__lt=cutoff_time
        )
        
        count = old_sessions.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'No sessions older than {hours} hours found.'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would close {count} sessions older than {hours} hours '
                    f'(last updated before {cutoff_time.strftime("%Y-%m-%d %H:%M:%S")})'
                )
            )
            
            # Show sample of sessions that would be closed
            sample_sessions = old_sessions[:5]
            self.stdout.write('\nSample sessions that would be closed:')
            for session in sample_sessions:
                user_display = session.user.username if session.user else f"Anonymous ({session.anonymous_id})"
                self.stdout.write(
                    f'  - Session {session.session_id} ({user_display}) - '
                    f'Last updated: {session.updated_at.strftime("%Y-%m-%d %H:%M:%S")}'
                )
            
            if count > 5:
                self.stdout.write(f'  ... and {count - 5} more')
            
            return
        
        # Perform cleanup using ChatManager
        manager = ChatManager()
        cleaned_count = manager.cleanup_old_sessions()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully closed {cleaned_count} sessions older than {hours} hours'
            )
        )
