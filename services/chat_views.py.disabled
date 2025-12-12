"""
Chat API Views for Sophie AI Assistant

Provides REST API endpoints for chat functionality when WebSocket is not available.
"""

import json
import logging
import asyncio
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .ai_processor import AIProcessor
from .chat_models import ChatSession, ChatMessage, ChatAnalytics

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def chat_message(request):
    """
    Handle chat message via REST API.
    
    POST /api/chat/message/
    Body: {
        "message": "user message text",
        "session_id": "optional session uuid",
        "context": {"current_page": "/services/", ...}
    }
    """
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        session_id = data.get('session_id')
        context = data.get('context', {})
        
        if not message_text:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create session
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                session = create_session(request)
        else:
            session = create_session(request)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            sender_type='user',
            content=message_text
        )
        
        # Get conversation history
        history = list(session.messages.values('sender_type', 'content').order_by('created_at'))
        
        # Add user context
        full_context = {
            'user_type': session.user_type,
            'current_page': context.get('current_page', ''),
            **context
        }
        
        # Process with AI
        ai_processor = AIProcessor()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response_text, metadata = loop.run_until_complete(
            ai_processor.process_message(message_text, full_context, history)
        )
        loop.close()
        
        # Save assistant response
        assistant_message = ChatMessage.objects.create(
            session=session,
            sender_type='assistant',
            content=response_text,
            metadata=metadata,
            is_cached_response=metadata.get('cached', False),
            processing_time_ms=metadata.get('processing_time_ms')
        )
        
        # Update analytics
        analytics, created = ChatAnalytics.objects.get_or_create(session=session)
        analytics.update_metrics(metadata.get('processing_time_ms'))
        
        # Update session
        session.updated_at = timezone.now()
        session.save()
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.session_id),
            'message': {
                'id': str(assistant_message.message_id),
                'content': response_text,
                'sender_type': 'assistant',
                'created_at': assistant_message.created_at.isoformat(),
                'metadata': metadata
            }
        })
        
    except Exception as e:
        logger.error(f'Error in chat_message: {e}', exc_info=True)
        return JsonResponse({
            'error': 'Internal server error',
            'message': 'Desculpe, ocorreu um erro. Por favor, tente novamente.'
        }, status=500)


def create_session(request):
    """Create a new chat session"""
    user = request.user if request.user.is_authenticated else None
    
    # Determine user type
    if user:
        if hasattr(user, 'userprofile'):
            user_type = user.userprofile.user_type
        else:
            user_type = 'client'
    else:
        user_type = 'anonymous'
    
    session = ChatSession.objects.create(
        user=user,
        user_type=user_type,
        anonymous_id=request.session.session_key if not user else None
    )
    
    # Create analytics
    ChatAnalytics.objects.create(session=session)
    
    return session


@csrf_exempt
@require_http_methods(["POST"])
def chat_rating(request):
    """
    Save chat satisfaction rating.
    
    POST /api/chat/rating/
    Body: {
        "session_id": "session uuid",
        "rating": 1-5
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        rating = data.get('rating')
        
        if not session_id or not rating:
            return JsonResponse({'error': 'session_id and rating are required'}, status=400)
        
        if not (1 <= rating <= 5):
            return JsonResponse({'error': 'rating must be between 1 and 5'}, status=400)
        
        session = ChatSession.objects.get(session_id=session_id)
        session.satisfaction_rating = rating
        session.save()
        
        return JsonResponse({'success': True})
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f'Error saving rating: {e}', exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
