# CDN Integration Documentation

## Overview

This document describes the CDN (Content Delivery Network) integration for the home services platform. The CDN integration optimizes the delivery of static assets and media files, reducing load times and bandwidth usage.

## Requirements Addressed

- **9.1**: Serve all static files through CDN
- **9.2**: Configure cache for images (30 days)
- **9.3**: Optimize images automatically for different devices
- **9.4**: Support modern formats like WebP and AVIF
- **9.5**: Validate reduction of loading time > 70%

## Architecture

### Components

1. **Storage Backends** (`services/storage_backends.py`)
   - `CDNStaticStorage`: Handles static file delivery through CDN
   - `CDNMediaStorage`: Handles media file delivery with optimization

2. **Image Optimizer** (`services/image_optimizer.py`)
   - Image compression and format conversion
   - Responsive image generation
   - WebP and AVIF support

3. **Cache Middleware** (`services/middleware/cdn_cache_middleware.py`)
   - `CDNCacheMiddleware`: Adds cache headers and ETags
   - `CacheInvalidationMiddleware`: Handles cache invalidation
   - `CDNPerformanceMiddleware`: Tracks performance metrics

4. **Management Commands**
   - `optimize_images`: Batch optimize existing images

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# CDN Configuration
CDN_ENABLED=true
CDN_URL=https://cdn.example.com
```

### Settings

The following settings are configured in `settings.py`:

```python
# CDN Settings
CDN_ENABLED = os.environ.get('CDN_ENABLED', 'False').lower() == 'true'
CDN_URL = os.environ.get('CDN_URL', '')
CDN_STATIC_PATH = '/static/'
CDN_MEDIA_PATH = '/media/'

# Image Optimization
CDN_OPTIMIZE_IMAGES = True
CDN_WEBP_ENABLED = True
CDN_AVIF_ENABLED = False  # Enable when pillow-avif-plugin is installed
```

## Usage

### Enabling CDN

1. Set environment variables:
   ```bash
   CDN_ENABLED=true
   CDN_URL=https://your-cdn-domain.com
   ```

2. Restart the Django application

3. All static and media URLs will automatically use the CDN

### Image Optimization

#### Automatic Optimization

Images uploaded through Django forms are automatically optimized when saved:

```python
# In your model
from django.db import models

class MyModel(models.Model):
    image = models.ImageField(upload_to='images/')
    # Image will be automatically optimized on save
```

#### Manual Optimization

Use the `ImageOptimizer` class directly:

```python
from services.image_optimizer import ImageOptimizer

optimizer = ImageOptimizer(webp_enabled=True, avif_enabled=False)

# Optimize a single image
optimizer.optimize_image('path/to/image.jpg', 'path/to/output.jpg')

# Generate responsive versions
versions = optimizer.generate_responsive_versions('path/to/image.jpg')
# Returns: {'thumbnail': 'path/to/image_thumbnail.jpg', ...}

# Convert to WebP
optimizer.convert_to_webp('path/to/image.jpg', 'path/to/image.webp')
```

#### Batch Optimization

Use the management command to optimize existing images:

```bash
# Optimize all images in media directory
python manage.py optimize_images --all

# Generate only responsive versions
python manage.py optimize_images --responsive

# Generate only WebP versions
python manage.py optimize_images --webp

# Optimize specific directory
python manage.py optimize_images --path avatars/ --all

# Dry run (see what would be done)
python manage.py optimize_images --all --dry-run
```

## Cache Configuration

### Cache Headers

The CDN cache middleware automatically adds appropriate cache headers:

#### Static Files
- **Cache-Control**: `public, max-age=2592000, immutable`
- **Duration**: 30 days
- **Immutable**: Yes (files don't change)

#### Media Files
- **Cache-Control**: `public, max-age=2592000`
- **Duration**: 30 days
- **Immutable**: No (files can be updated)

#### HTML Pages
- **Cache-Control**: `public, max-age=300, must-revalidate`
- **Duration**: 5 minutes
- **Revalidation**: Required

### ETags

ETags are automatically generated for all static and media files:

1. First request: Server sends ETag header
2. Subsequent requests: Client sends `If-None-Match` header
3. If content unchanged: Server responds with `304 Not Modified`
4. If content changed: Server sends new content with new ETag

### Cache Invalidation

Cache is automatically invalidated when:

1. Content is modified (POST, PUT, PATCH, DELETE requests)
2. Files are uploaded or updated
3. Manual invalidation is triggered

The `CacheInvalidationMiddleware` adds headers to trigger CDN cache purge:
- `X-Cache-Invalidate: true`
- `X-Cache-Invalidate-Time: <timestamp>`

## Responsive Images

### Default Sizes

The image optimizer generates these responsive versions by default:

| Size Name | Max Dimensions | Use Case |
|-----------|---------------|----------|
| thumbnail | 150x150 | Thumbnails, avatars |
| small | 320x320 | Mobile phones (portrait) |
| medium | 640x640 | Tablets, mobile (landscape) |
| large | 1024x1024 | Desktop screens |
| xlarge | 1920x1920 | High-resolution displays |

### Custom Sizes

Generate custom responsive versions:

```python
from services.image_optimizer import ImageOptimizer

optimizer = ImageOptimizer()

custom_sizes = {
    'card': (300, 200),
    'hero': (1600, 900),
}

versions = optimizer.generate_responsive_versions(
    'path/to/image.jpg',
    sizes=custom_sizes
)
```

### Using in Templates

```html
<!-- Responsive image with srcset -->
<img src="{{ image.url }}"
     srcset="{{ image_small.url }} 320w,
             {{ image_medium.url }} 640w,
             {{ image_large.url }} 1024w"
     sizes="(max-width: 320px) 320px,
            (max-width: 640px) 640px,
            1024px"
     alt="Description">

<!-- Modern format with fallback -->
<picture>
  <source srcset="{{ image_webp.url }}" type="image/webp">
  <source srcset="{{ image_avif.url }}" type="image/avif">
  <img src="{{ image.url }}" alt="Description">
</picture>
```

## Modern Image Formats

### WebP Support

WebP provides better compression than JPEG/PNG:

- **Enabled by default**: `CDN_WEBP_ENABLED = True`
- **Compression**: ~30% smaller than JPEG
- **Browser support**: 95%+ of browsers

### AVIF Support

AVIF provides even better compression than WebP:

- **Disabled by default**: Requires `pillow-avif-plugin`
- **Compression**: ~50% smaller than JPEG
- **Browser support**: 70%+ of browsers (growing)

To enable AVIF:

```bash
# Install the plugin
pip install pillow-avif-plugin

# Update settings
CDN_AVIF_ENABLED = True
```

## Performance Testing

### Running Tests

Use the provided test script to validate CDN performance:

```bash
# Test local development server
python test_cdn_performance.py

# Test production server
python test_cdn_performance.py https://your-domain.com
```

### Test Coverage

The test script validates:

1. **Cache Headers**: Verifies 30-day cache for static/media files
2. **ETag Validation**: Tests 304 Not Modified responses
3. **Loading Performance**: Measures cold vs warm cache performance

### Performance Requirements

The CDN integration must achieve:

- **Cache hit rate**: > 80%
- **Loading time reduction**: > 70% (warm vs cold cache)
- **Image compression**: > 60% size reduction

### Example Results

```
Testing Loading Performance
==================================================

Testing: http://localhost:8000/static/css/style.css
  Average cold load time: 45.23ms
  Average warm load time: 12.34ms
  Performance improvement: 72.7%
  ✓ Meets 70% improvement requirement
```

## CDN Provider Integration

### Cloudflare

1. Sign up for Cloudflare
2. Add your domain
3. Update DNS to point to Cloudflare
4. Configure settings:
   ```
   CDN_ENABLED=true
   CDN_URL=https://your-domain.com
   ```

### AWS CloudFront

1. Create CloudFront distribution
2. Set origin to your server
3. Configure cache behaviors
4. Update settings:
   ```
   CDN_ENABLED=true
   CDN_URL=https://d1234567890.cloudfront.net
   ```

### Custom CDN

For custom CDN providers:

1. Configure CDN to pull from your origin server
2. Set up cache rules (30 days for static/media)
3. Update settings with CDN URL
4. Test with `test_cdn_performance.py`

## Monitoring

### Performance Metrics

The `CDNPerformanceMiddleware` logs performance data:

```python
# View logs
tail -f django.log | grep "CDN Performance"
```

### Key Metrics

Monitor these metrics:

1. **Response Time**: Average time to serve files
2. **Cache Hit Rate**: Percentage of requests served from cache
3. **Bandwidth Savings**: Reduction in origin server traffic
4. **Error Rate**: Failed requests to CDN

### Dashboard

Create a monitoring dashboard to track:

- CDN response times
- Cache hit/miss ratio
- Bandwidth usage
- Top requested files
- Geographic distribution

## Troubleshooting

### Images Not Optimizing

**Problem**: Uploaded images are not being optimized

**Solutions**:
1. Check `CDN_OPTIMIZE_IMAGES` setting is `True`
2. Verify Pillow is installed: `pip install Pillow`
3. Check logs for optimization errors
4. Ensure sufficient disk space

### Cache Not Working

**Problem**: Files are not being cached

**Solutions**:
1. Verify `CDN_ENABLED` is `true`
2. Check middleware is in `MIDDLEWARE` list
3. Verify cache headers in browser dev tools
4. Clear browser cache and test again

### WebP Not Generating

**Problem**: WebP versions are not being created

**Solutions**:
1. Check `CDN_WEBP_ENABLED` is `True`
2. Verify Pillow supports WebP: `python -c "from PIL import Image; print(Image.EXTENSION)"`
3. Install WebP support: `pip install Pillow --upgrade`

### Performance Not Improving

**Problem**: Loading times not meeting 70% requirement

**Solutions**:
1. Verify CDN is properly configured
2. Check cache headers are being sent
3. Test from different geographic locations
4. Optimize image sizes further
5. Enable compression (gzip/brotli)

## Best Practices

### Image Upload

1. **Validate file types**: Only allow image formats
2. **Limit file size**: Set maximum upload size (e.g., 5MB)
3. **Generate thumbnails**: Create responsive versions on upload
4. **Use modern formats**: Enable WebP for better compression

### Cache Strategy

1. **Long cache for static**: 30+ days for versioned assets
2. **Shorter cache for media**: 30 days with ETag validation
3. **No cache for dynamic**: Don't cache user-specific content
4. **Invalidate on update**: Clear cache when content changes

### Performance Optimization

1. **Lazy loading**: Load images only when visible
2. **Responsive images**: Serve appropriate size for device
3. **Modern formats**: Use WebP/AVIF with fallbacks
4. **Compression**: Enable gzip/brotli for text files
5. **Minification**: Minify CSS/JS files

## Security Considerations

### Access Control

1. **Private media**: Don't serve sensitive files through CDN
2. **Signed URLs**: Use signed URLs for protected content
3. **CORS**: Configure CORS headers appropriately
4. **HTTPS**: Always use HTTPS for CDN

### Content Validation

1. **File type checking**: Validate uploaded file types
2. **Virus scanning**: Scan uploaded files for malware
3. **Size limits**: Enforce maximum file sizes
4. **Rate limiting**: Limit upload frequency

## Migration Guide

### Migrating Existing Files

1. **Backup**: Create backup of media directory
2. **Optimize**: Run batch optimization
   ```bash
   python manage.py optimize_images --all
   ```
3. **Upload**: Upload optimized files to CDN
4. **Test**: Verify files are accessible
5. **Enable**: Set `CDN_ENABLED=true`
6. **Monitor**: Watch for errors in logs

### Rollback Plan

If issues occur:

1. Set `CDN_ENABLED=false`
2. Restart application
3. Files will be served from origin server
4. Investigate and fix issues
5. Re-enable CDN when ready

## Support

For issues or questions:

1. Check logs: `tail -f django.log`
2. Run tests: `python test_cdn_performance.py`
3. Review documentation
4. Contact development team

## References

- [Django Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [WebP Format](https://developers.google.com/speed/webp)
- [AVIF Format](https://aomediacodec.github.io/av1-avif/)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
