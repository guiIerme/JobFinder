"""
Test script to validate compression middleware functionality.
Tests requirements 5.1, 5.2, 5.3, 5.4, 5.5
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.test import RequestFactory
from django.http import HttpResponse
from services.middleware.compression_middleware import BrotliMiddleware


def test_compression():
    """Test compression middleware functionality"""
    
    print("=" * 70)
    print("COMPRESSION MIDDLEWARE TEST")
    print("=" * 70)
    
    # Create a request factory
    factory = RequestFactory()
    
    # Test 1: Small response (< 1KB) should not be compressed
    print("\n[TEST 1] Small response (< 1KB) - Should NOT compress")
    print("-" * 70)
    request = factory.get('/')
    request.META['HTTP_ACCEPT_ENCODING'] = 'br, gzip, deflate'
    
    small_content = "Small content" * 10  # Less than 1KB
    response = HttpResponse(small_content, content_type='text/html')
    
    middleware = BrotliMiddleware(lambda r: response)
    processed_response = middleware.process_response(request, response)
    
    has_encoding = processed_response.has_header('Content-Encoding')
    print(f"Content size: {len(small_content)} bytes")
    print(f"Has Content-Encoding header: {has_encoding}")
    print(f"✓ PASS: Small content not compressed" if not has_encoding else "✗ FAIL: Small content was compressed")
    
    # Test 2: Large HTML response with Brotli support
    print("\n[TEST 2] Large HTML response with Brotli support - Should compress")
    print("-" * 70)
    request = factory.get('/')
    request.META['HTTP_ACCEPT_ENCODING'] = 'br, gzip, deflate'
    
    large_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Test Content</h1>
        <p>This is a large HTML document that should be compressed.</p>
    """ + ("<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>\n" * 100) + """
    </body>
    </html>
    """
    
    response = HttpResponse(large_content, content_type='text/html')
    original_size = len(large_content)
    
    middleware = BrotliMiddleware(lambda r: response)
    processed_response = middleware.process_response(request, response)
    
    has_encoding = processed_response.has_header('Content-Encoding')
    encoding_type = processed_response.get('Content-Encoding', 'none')
    compressed_size = len(processed_response.content)
    
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Content-Encoding: {encoding_type}")
    
    if has_encoding and compressed_size < original_size:
        compression_ratio = (1 - compressed_size / original_size) * 100
        print(f"Compression ratio: {compression_ratio:.1f}%")
        print(f"✓ PASS: Content compressed successfully")
        
        # Test requirement 5.4: Compression ratio > 60%
        if compression_ratio >= 60:
            print(f"✓ PASS: Compression ratio meets requirement (>= 60%)")
        else:
            print(f"✗ FAIL: Compression ratio below requirement ({compression_ratio:.1f}% < 60%)")
    else:
        print(f"✗ FAIL: Content not compressed")
    
    # Test 3: JSON response
    print("\n[TEST 3] Large JSON response - Should compress")
    print("-" * 70)
    request = factory.get('/api/data')
    request.META['HTTP_ACCEPT_ENCODING'] = 'br, gzip, deflate'
    
    json_content = '{"data": [' + ','.join([f'{{"id": {i}, "name": "Item {i}", "description": "This is a description for item {i}"}}' for i in range(100)]) + ']}'
    
    response = HttpResponse(json_content, content_type='application/json')
    original_size = len(json_content)
    
    middleware = BrotliMiddleware(lambda r: response)
    processed_response = middleware.process_response(request, response)
    
    has_encoding = processed_response.has_header('Content-Encoding')
    encoding_type = processed_response.get('Content-Encoding', 'none')
    compressed_size = len(processed_response.content)
    
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Content-Encoding: {encoding_type}")
    
    if has_encoding and compressed_size < original_size:
        compression_ratio = (1 - compressed_size / original_size) * 100
        print(f"Compression ratio: {compression_ratio:.1f}%")
        print(f"✓ PASS: JSON content compressed successfully")
    else:
        print(f"✗ FAIL: JSON content not compressed")
    
    # Test 4: CSS response
    print("\n[TEST 4] Large CSS response - Should compress")
    print("-" * 70)
    request = factory.get('/static/style.css')
    request.META['HTTP_ACCEPT_ENCODING'] = 'br, gzip, deflate'
    
    css_content = """
    body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
    """ + "\n".join([f".class-{i} {{ color: #{i:06x}; background: #{(i*2):06x}; }}" for i in range(100)])
    
    response = HttpResponse(css_content, content_type='text/css')
    original_size = len(css_content)
    
    middleware = BrotliMiddleware(lambda r: response)
    processed_response = middleware.process_response(request, response)
    
    has_encoding = processed_response.has_header('Content-Encoding')
    encoding_type = processed_response.get('Content-Encoding', 'none')
    compressed_size = len(processed_response.content)
    
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Content-Encoding: {encoding_type}")
    
    if has_encoding and compressed_size < original_size:
        compression_ratio = (1 - compressed_size / original_size) * 100
        print(f"Compression ratio: {compression_ratio:.1f}%")
        print(f"✓ PASS: CSS content compressed successfully")
    else:
        print(f"✗ FAIL: CSS content not compressed")
    
    # Test 5: Non-compressible content type (image)
    print("\n[TEST 5] Image response - Should NOT compress")
    print("-" * 70)
    request = factory.get('/image.jpg')
    request.META['HTTP_ACCEPT_ENCODING'] = 'br, gzip, deflate'
    
    image_content = b'\xFF\xD8\xFF\xE0' + (b'\x00' * 2000)  # Fake JPEG header + data
    response = HttpResponse(image_content, content_type='image/jpeg')
    
    middleware = BrotliMiddleware(lambda r: response)
    processed_response = middleware.process_response(request, response)
    
    has_encoding = processed_response.has_header('Content-Encoding')
    print(f"Content type: image/jpeg")
    print(f"Has Content-Encoding header: {has_encoding}")
    print(f"✓ PASS: Image not compressed (correct)" if not has_encoding else "✗ FAIL: Image was compressed (incorrect)")
    
    # Test 6: Client doesn't support Brotli
    print("\n[TEST 6] Client without Brotli support - Should skip Brotli")
    print("-" * 70)
    request = factory.get('/')
    request.META['HTTP_ACCEPT_ENCODING'] = 'gzip, deflate'  # No 'br'
    
    response = HttpResponse(large_content, content_type='text/html')
    
    middleware = BrotliMiddleware(lambda r: response)
    processed_response = middleware.process_response(request, response)
    
    has_encoding = processed_response.has_header('Content-Encoding')
    encoding_type = processed_response.get('Content-Encoding', 'none')
    
    print(f"Accept-Encoding: gzip, deflate (no br)")
    print(f"Content-Encoding: {encoding_type}")
    
    if encoding_type != 'br':
        print(f"✓ PASS: Brotli not used when client doesn't support it")
    else:
        print(f"✗ FAIL: Brotli used despite client not supporting it")
    
    print("\n" + "=" * 70)
    print("COMPRESSION TESTS COMPLETED")
    print("=" * 70)


if __name__ == '__main__':
    try:
        test_compression()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
