import os
import shutil
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = 'Create a backup of the database and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-dir',
            default='backups',
            help='Directory to store backups (default: backups)',
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Include media files in backup',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress backup into a zip file',
        )

    def handle(self, *args, **options):
        # Create backup directory if it doesn't exist
        os.makedirs(options['backup_dir'], exist_ok=True)
        
        # Generate timestamp for backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"jobfinder_backup_{timestamp}"
        backup_path = os.path.join(options['backup_dir'], backup_name)
        
        # Initialize db_backup_file variable
        db_backup_file = f"{backup_path}_db.json"
        
        try:
            # Create database backup using dumpdata
            self.stdout.write('Creating database backup...')
            
            # Export all data except contenttypes and auth permissions (they're recreated on load)
            call_command(
                'dumpdata',
                '--exclude', 'contenttypes',
                '--exclude', 'auth.Permission',
                '--indent', '2',
                stdout=open(db_backup_file, 'w')
            )
            
            self.stdout.write(f'Database backup created: {db_backup_file}')
            
            # Backup media files if requested
            if options['include_media'] and hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
                media_backup_dir = f"{backup_path}_media"
                if os.path.exists(settings.MEDIA_ROOT):
                    self.stdout.write('Copying media files...')
                    shutil.copytree(settings.MEDIA_ROOT, media_backup_dir)
                    self.stdout.write(f'Media files copied to: {media_backup_dir}')
                else:
                    self.stdout.write('Media directory does not exist, skipping media backup')
            
            # Compress backup if requested
            if options['compress']:
                self.stdout.write('Compressing backup...')
                zip_filename = f"{backup_path}.zip"
                
                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add database backup
                    zipf.write(db_backup_file, os.path.basename(db_backup_file))
                    
                    # Add media backup if it exists
                    if options['include_media'] and os.path.exists(f"{backup_path}_media"):
                        media_dir = f"{backup_path}_media"
                        for root, dirs, files in os.walk(media_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_path = os.path.join(
                                    os.path.basename(media_dir),
                                    os.path.relpath(file_path, media_dir)
                                )
                                zipf.write(file_path, arc_path)
                
                # Remove uncompressed files after compression
                os.remove(db_backup_file)
                if options['include_media'] and os.path.exists(f"{backup_path}_media"):
                    shutil.rmtree(f"{backup_path}_media")
                
                self.stdout.write(f'Backup compressed to: {zip_filename}')
            else:
                self.stdout.write(f'Backup completed: {backup_path}')
            
            self.stdout.write(
                f'Successfully created backup: {backup_name}'
            )
            
        except Exception as e:
            self.stdout.write(
                f'Error creating backup: {str(e)}'
            )
            # Clean up any partially created files
            if os.path.exists(db_backup_file):
                os.remove(db_backup_file)
            if os.path.exists(f"{backup_path}_media"):
                shutil.rmtree(f"{backup_path}_media")
            if os.path.exists(f"{backup_path}.zip"):
                os.remove(f"{backup_path}.zip")