"""
Management command for batch image optimization.

This command allows administrators to optimize existing images in the media directory,
generating responsive versions and modern format alternatives.

Requirements:
- 9.3: Optimize images for different devices
- 9.4: Support WebP and AVIF formats

Usage:
    python manage.py optimize_images [--responsive] [--webp] [--avif] [--path PATH]
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from services.image_optimizer import ImageOptimizer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize images in the media directory for CDN delivery'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Specific path to optimize (relative to MEDIA_ROOT)',
        )
        
        parser.add_argument(
            '--responsive',
            action='store_true',
            help='Generate responsive versions of images',
        )
        
        parser.add_argument(
            '--webp',
            action='store_true',
            help='Generate WebP versions of images',
        )
        
        parser.add_argument(
            '--avif',
            action='store_true',
            help='Generate AVIF versions of images',
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate all versions (responsive, WebP, AVIF)',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )
    
    def handle(self, *args, **options):
        """Execute the image optimization command."""
        
        # Get options
        target_path = options.get('path')
        generate_responsive = options.get('responsive') or options.get('all')
        generate_webp = options.get('webp') or options.get('all')
        generate_avif = options.get('avif') or options.get('all')
        dry_run = options.get('dry_run')
        
        # Initialize optimizer
        optimizer = ImageOptimizer(
            webp_enabled=generate_webp or getattr(settings, 'CDN_WEBP_ENABLED', True),
            avif_enabled=generate_avif or getattr(settings, 'CDN_AVIF_ENABLED', False)
        )
        
        # Determine base path
        if target_path:
            base_path = os.path.join(settings.MEDIA_ROOT, target_path)
            if not os.path.exists(base_path):
                raise CommandError(f"Path does not exist: {base_path}")
        else:
            base_path = settings.MEDIA_ROOT
        
        self.stdout.write(self.style.SUCCESS(f"Scanning images in: {base_path}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No files will be modified"))
        
        # Find all images
        image_files = self._find_images(base_path)
        
        if not image_files:
            self.stdout.write(self.style.WARNING("No images found to optimize"))
            return
        
        self.stdout.write(f"Found {len(image_files)} images to process")
        
        # Process each image
        processed = 0
        errors = 0
        
        for image_path in image_files:
            try:
                self.stdout.write(f"\nProcessing: {os.path.relpath(image_path, settings.MEDIA_ROOT)}")
                
                if not dry_run:
                    # Generate responsive versions
                    if generate_responsive:
                        self.stdout.write("  - Generating responsive versions...")
                        versions = optimizer.generate_responsive_versions(image_path)
                        self.stdout.write(f"    Generated {len(versions)} versions")
                    
                    # Generate modern formats
                    if generate_webp or generate_avif:
                        self.stdout.write("  - Generating modern format versions...")
                        formats = optimizer.generate_modern_formats(image_path)
                        for format_name, format_path in formats.items():
                            self.stdout.write(f"    Generated {format_name.upper()}: {os.path.basename(format_path)}")
                else:
                    if generate_responsive:
                        self.stdout.write("  - Would generate responsive versions")
                    if generate_webp:
                        self.stdout.write("  - Would generate WebP version")
                    if generate_avif:
                        self.stdout.write("  - Would generate AVIF version")
                
                processed += 1
                
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  Error: {str(e)}"))
                logger.error(f"Error processing {image_path}: {e}")
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Processed: {processed} images"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a dry run. No files were modified."))
            self.stdout.write("Run without --dry-run to actually optimize images.")
    
    def _find_images(self, base_path):
        """
        Find all image files in the given path.
        
        Args:
            base_path: Base directory to search
            
        Returns:
            list: List of image file paths
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        image_files = []
        
        if os.path.isfile(base_path):
            # Single file
            if os.path.splitext(base_path)[1].lower() in image_extensions:
                image_files.append(base_path)
        else:
            # Directory - walk through it
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in image_extensions:
                        # Skip already optimized versions
                        if not any(suffix in file for suffix in ['_thumbnail', '_small', '_medium', '_large', '_xlarge']):
                            image_files.append(os.path.join(root, file))
        
        return image_files
