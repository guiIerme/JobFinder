"""
Image Optimization Utilities for CDN Integration.

This module provides utilities for optimizing images for web delivery,
including format conversion, compression, and responsive image generation.

Requirements:
- 9.3: Optimize images automatically for different devices
- 9.4: Support WebP and AVIF formats
"""

import os
from PIL import Image
from io import BytesIO
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    Utility class for optimizing images for web delivery.
    
    Provides methods for:
    - Converting images to modern formats (WebP, AVIF)
    - Generating responsive image versions
    - Compressing images while maintaining quality
    """
    
    # Default responsive breakpoints (width, height)
    DEFAULT_SIZES = {
        'thumbnail': (150, 150),
        'small': (320, 320),
        'medium': (640, 640),
        'large': (1024, 1024),
        'xlarge': (1920, 1920),
    }
    
    # Quality settings for different formats
    QUALITY_SETTINGS = {
        'JPEG': 85,
        'PNG': None,  # PNG uses optimize flag instead
        'WEBP': 85,
        'AVIF': 85,
    }
    
    def __init__(self, webp_enabled=True, avif_enabled=False):
        """
        Initialize the image optimizer.
        
        Args:
            webp_enabled: Whether to enable WebP format support
            avif_enabled: Whether to enable AVIF format support
        """
        self.webp_enabled = webp_enabled
        self.avif_enabled = avif_enabled
    
    def optimize_image(self, image_path: str, output_path: str = None, 
                      format: str = None, quality: int = None) -> str:
        """
        Optimize a single image file.
        
        Requirement 9.3: Optimize images automatically
        
        Args:
            image_path: Path to the input image
            output_path: Path for the output image (optional)
            format: Target format (JPEG, PNG, WEBP, AVIF) (optional)
            quality: Quality setting 1-100 (optional)
            
        Returns:
            str: Path to the optimized image
        """
        try:
            with Image.open(image_path) as img:
                # Determine output format
                if format is None:
                    format = self._get_optimal_format(img, image_path)
                
                # Determine output path
                if output_path is None:
                    base, ext = os.path.splitext(image_path)
                    new_ext = self._get_extension_for_format(format)
                    output_path = f"{base}_optimized{new_ext}"
                
                # Convert RGBA to RGB for JPEG
                if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    img = self._convert_to_rgb(img)
                
                # Get quality setting
                if quality is None:
                    quality = self.QUALITY_SETTINGS.get(format, 85)
                
                # Save optimized image
                save_kwargs = self._get_save_kwargs(format, quality)
                img.save(output_path, format=format, **save_kwargs)
                
                logger.info(f"Optimized image saved to {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error optimizing image {image_path}: {e}")
            raise
    
    def generate_responsive_versions(self, image_path: str, 
                                    sizes: Dict[str, Tuple[int, int]] = None,
                                    output_dir: str = None) -> Dict[str, str]:
        """
        Generate multiple responsive versions of an image.
        
        Requirement 9.3: Optimize images for different devices
        
        Args:
            image_path: Path to the input image
            sizes: Dictionary of size_name -> (width, height) tuples
            output_dir: Directory for output images (optional)
            
        Returns:
            dict: Mapping of size names to output file paths
        """
        if sizes is None:
            sizes = self.DEFAULT_SIZES
        
        if output_dir is None:
            output_dir = os.path.dirname(image_path)
        
        versions = {}
        
        try:
            with Image.open(image_path) as img:
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                original_format = img.format
                
                for size_name, (max_width, max_height) in sizes.items():
                    # Create a copy of the image
                    resized_img = img.copy()
                    
                    # Calculate new size maintaining aspect ratio
                    resized_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                    
                    # Generate output filename
                    ext = self._get_extension_for_format(original_format)
                    output_filename = f"{base_name}_{size_name}{ext}"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # Convert RGBA to RGB for JPEG
                    if original_format == 'JPEG' and resized_img.mode in ('RGBA', 'LA', 'P'):
                        resized_img = self._convert_to_rgb(resized_img)
                    
                    # Save resized image
                    save_kwargs = self._get_save_kwargs(original_format, 
                                                       self.QUALITY_SETTINGS.get(original_format, 85))
                    resized_img.save(output_path, format=original_format, **save_kwargs)
                    
                    versions[size_name] = output_path
                    logger.info(f"Generated {size_name} version: {output_path}")
                
        except Exception as e:
            logger.error(f"Error generating responsive versions for {image_path}: {e}")
            raise
        
        return versions
    
    def convert_to_webp(self, image_path: str, output_path: str = None, 
                       quality: int = 85) -> str:
        """
        Convert an image to WebP format.
        
        Requirement 9.4: Support WebP format
        
        Args:
            image_path: Path to the input image
            output_path: Path for the output WebP image (optional)
            quality: Quality setting 1-100
            
        Returns:
            str: Path to the WebP image
        """
        if not self.webp_enabled:
            raise ValueError("WebP support is not enabled")
        
        if output_path is None:
            base, _ = os.path.splitext(image_path)
            output_path = f"{base}.webp"
        
        try:
            with Image.open(image_path) as img:
                # WebP supports transparency, no need to convert RGBA
                img.save(output_path, format='WEBP', quality=quality, method=6)
                logger.info(f"Converted to WebP: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error converting to WebP {image_path}: {e}")
            raise
    
    def convert_to_avif(self, image_path: str, output_path: str = None, 
                       quality: int = 85) -> str:
        """
        Convert an image to AVIF format.
        
        Requirement 9.4: Support AVIF format
        
        Note: Requires pillow-avif-plugin to be installed
        
        Args:
            image_path: Path to the input image
            output_path: Path for the output AVIF image (optional)
            quality: Quality setting 1-100
            
        Returns:
            str: Path to the AVIF image
        """
        if not self.avif_enabled:
            raise ValueError("AVIF support is not enabled")
        
        if output_path is None:
            base, _ = os.path.splitext(image_path)
            output_path = f"{base}.avif"
        
        try:
            with Image.open(image_path) as img:
                # AVIF supports transparency
                img.save(output_path, format='AVIF', quality=quality)
                logger.info(f"Converted to AVIF: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error converting to AVIF {image_path}: {e}")
            raise
    
    def generate_modern_formats(self, image_path: str, 
                               output_dir: str = None) -> Dict[str, str]:
        """
        Generate modern format versions (WebP, AVIF) of an image.
        
        Requirement 9.4: Support WebP and AVIF formats
        
        Args:
            image_path: Path to the input image
            output_dir: Directory for output images (optional)
            
        Returns:
            dict: Mapping of format names to output file paths
        """
        if output_dir is None:
            output_dir = os.path.dirname(image_path)
        
        formats = {}
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Generate WebP version
        if self.webp_enabled:
            try:
                webp_path = os.path.join(output_dir, f"{base_name}.webp")
                self.convert_to_webp(image_path, webp_path)
                formats['webp'] = webp_path
            except Exception as e:
                logger.warning(f"Failed to generate WebP version: {e}")
        
        # Generate AVIF version
        if self.avif_enabled:
            try:
                avif_path = os.path.join(output_dir, f"{base_name}.avif")
                self.convert_to_avif(image_path, avif_path)
                formats['avif'] = avif_path
            except Exception as e:
                logger.warning(f"Failed to generate AVIF version: {e}")
        
        return formats
    
    def _get_optimal_format(self, img: Image.Image, original_path: str) -> str:
        """
        Determine the optimal output format for an image.
        
        Args:
            img: PIL Image object
            original_path: Path to the original image
            
        Returns:
            str: Optimal format (JPEG, PNG, WEBP, AVIF)
        """
        # Check if image has transparency
        has_transparency = img.mode in ('RGBA', 'LA') or (
            img.mode == 'P' and 'transparency' in img.info
        )
        
        # If WebP is enabled, prefer it for all images
        if self.webp_enabled:
            return 'WEBP'
        
        # If AVIF is enabled, prefer it (better compression than WebP)
        if self.avif_enabled:
            return 'AVIF'
        
        # Fall back to traditional formats
        if has_transparency:
            return 'PNG'
        else:
            return 'JPEG'
    
    def _get_extension_for_format(self, format: str) -> str:
        """
        Get the file extension for a given format.
        
        Args:
            format: Image format name
            
        Returns:
            str: File extension including the dot
        """
        extensions = {
            'JPEG': '.jpg',
            'PNG': '.png',
            'WEBP': '.webp',
            'AVIF': '.avif',
            'GIF': '.gif',
        }
        return extensions.get(format, '.jpg')
    
    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """
        Convert an image with transparency to RGB.
        
        Args:
            img: PIL Image object
            
        Returns:
            Image.Image: RGB image
        """
        # Create a white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        
        # Paste the image on the background
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        elif img.mode == 'LA':
            background.paste(img, mask=img.split()[1])  # Use alpha channel as mask
        elif img.mode == 'P':
            img = img.convert('RGBA')
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        
        return background
    
    def _get_save_kwargs(self, format: str, quality: int) -> dict:
        """
        Get the keyword arguments for saving an image in a specific format.
        
        Args:
            format: Image format
            quality: Quality setting
            
        Returns:
            dict: Keyword arguments for Image.save()
        """
        kwargs = {}
        
        if format == 'JPEG':
            kwargs = {
                'quality': quality,
                'optimize': True,
                'progressive': True,
            }
        elif format == 'PNG':
            kwargs = {
                'optimize': True,
            }
        elif format == 'WEBP':
            kwargs = {
                'quality': quality,
                'method': 6,  # Slowest but best compression
            }
        elif format == 'AVIF':
            kwargs = {
                'quality': quality,
            }
        
        return kwargs
    
    @staticmethod
    def get_image_info(image_path: str) -> Dict:
        """
        Get information about an image file.
        
        Args:
            image_path: Path to the image
            
        Returns:
            dict: Image information (format, size, mode, etc.)
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'file_size': os.path.getsize(image_path),
                }
        except Exception as e:
            logger.error(f"Error getting image info for {image_path}: {e}")
            return {}
    
    @staticmethod
    def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
        """
        Calculate the compression ratio as a percentage.
        
        Args:
            original_size: Original file size in bytes
            compressed_size: Compressed file size in bytes
            
        Returns:
            float: Compression ratio as percentage (0-100)
        """
        if original_size == 0:
            return 0.0
        
        reduction = original_size - compressed_size
        ratio = (reduction / original_size) * 100
        return round(ratio, 2)
