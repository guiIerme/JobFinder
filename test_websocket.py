"""
Test script for WebSocket notification system.

This script tests the WebSocket notification functionality by:
1. Creating a test notification in the database
2. Sending it via WebSocket to a user
3. Verifying the notification was created

Usage:
    python test_websocket.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_services.settings')
django.setup()

from django.contrib.auth.models import User
from services.websocket_utils import create_and_send_notification
from services.models import Notification


def test_websocket_notification():
    """Test creating and sending a WebSocket notification."""
    
    print("=" * 60)
    print("WebSocket Notification System Test")
    print("=" * 60)
    
    # Get or create a test user
    try:
        user = User.objects.first()
        if not user:
            print("\n❌ No users found in database. Please create a user first.")
            return False
        
        print(f"\n✓ Using test user: {user.username} (ID: {user.id})")
        
        # Create and send a test notification
        print("\n📤 Creating and sending test notification...")
        notification_id = create_and_send_notification(
            user=user,
            notification_type='system',
            title='Teste de Notificação WebSocket',
            message='Esta é uma notificação de teste do sistema WebSocket. Se você está conectado, deve recebê-la em tempo real!',
            related_object_id=None,
            related_object_type=None
        )
        
        if notification_id:
            print(f"✓ Notification created with ID: {notification_id}")
            
            # Verify notification was created in database
            notification = Notification.objects.get(id=notification_id)
            print(f"✓ Notification verified in database:")
            print(f"  - Title: {notification.title}")
            print(f"  - Message: {notification.message}")
            print(f"  - Type: {notification.notification_type}")
            print(f"  - Created: {notification.created_at}")
            print(f"  - Is Read: {notification.is_read}")
            
            print("\n" + "=" * 60)
            print("✅ Test completed successfully!")
            print("=" * 60)
            print("\nTo see the notification in real-time:")
            print("1. Start the development server: python manage.py runserver")
            print("2. Log in as the test user")
            print("3. Open the browser console to see WebSocket connection")
            print("4. Run this test script again to send a notification")
            print("5. You should see the notification appear in real-time!")
            print("=" * 60)
            
            return True
        else:
            print("❌ Failed to create notification")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_notification_count():
    """Test getting notification count for users."""
    
    print("\n" + "=" * 60)
    print("Notification Count Test")
    print("=" * 60)
    
    users = User.objects.all()[:5]  # Get first 5 users
    
    if not users:
        print("\n❌ No users found in database.")
        return False
    
    print(f"\nChecking notifications for {users.count()} users:\n")
    
    for user in users:
        total = Notification.objects.filter(user=user).count()
        unread = Notification.objects.filter(user=user, is_read=False).count()
        print(f"  {user.username}:")
        print(f"    - Total notifications: {total}")
        print(f"    - Unread notifications: {unread}")
    
    print("\n" + "=" * 60)
    return True


def test_websocket_connection_info():
    """Display WebSocket connection information."""
    
    print("\n" + "=" * 60)
    print("WebSocket Connection Information")
    print("=" * 60)
    
    print("\nWebSocket URL: ws://localhost:8000/ws/notifications/")
    print("\nTo test the WebSocket connection:")
    print("1. Open your browser's developer console")
    print("2. Navigate to the Network tab")
    print("3. Filter by 'WS' (WebSocket)")
    print("4. You should see a connection to /ws/notifications/")
    print("5. Click on it to see messages being sent/received")
    
    print("\n" + "=" * 60)
    return True


if __name__ == '__main__':
    print("\n🚀 Starting WebSocket Notification Tests...\n")
    
    # Run tests
    test_websocket_connection_info()
    test_notification_count()
    test_websocket_notification()
    
    print("\n✅ All tests completed!\n")
