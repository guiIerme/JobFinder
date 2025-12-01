"""
Chat Models for Sophie AI Assistant

This module contains the database models for the chat system including
sessions, messages, knowledge base, and analytics.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    """
    Represents a chat conversation session between a user and Sophie.
    
    A session can be associated with an authenticated user or an anonymous visitor.
    Sessions store context data about the user's navigation and preferences.
    """
    
    USER_TYPE_CHOICES = [
        ('client', 'Cliente'),
        ('provider', 'Prestador'),
        ('anonymous', 'Anônimo')
    ]
    
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions')
    anonymous_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    context_data = models.JSONField(default=dict, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='anonymous')
    satisfaction_rating = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active', '-updated_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else f'Anonymous-{self.anonymous_id[:8]}'
        return f'ChatSession {self.session_id} - {user_str}'
    
    def close(self):
        """Close the session"""
        self.is_active = False
        self.closed_at = timezone.now()
        self.save(update_fields=['is_active', 'closed_at'])


class ChatMessage(models.Model):
    """
    Represents a single message in a chat session.
    
    Messages can be from the user, Sophie (assistant), or the system.
    Metadata stores additional information like intent, confidence, and links.
    """
    
    SENDER_TYPE_CHOICES = [
        ('user', 'Usuário'),
        ('assistant', 'Sophie'),
        ('system', 'Sistema')
    ]
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_cached_response = models.BooleanField(default=False)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.sender_type} message in {self.session.session_id}'


class KnowledgeBaseEntry(models.Model):
    """
    Stores information that Sophie can reference when answering questions.
    
    Entries are categorized and can be linked to specific services.
    Keywords help with search and retrieval.
    """
    
    CATEGORY_CHOICES = [
        ('service', 'Serviço'),
        ('faq', 'FAQ'),
        ('navigation', 'Navegação'),
        ('policy', 'Política'),
        ('troubleshooting', 'Solução de Problemas')
    ]
    
    entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.JSONField(default=list, blank=True)
    related_services = models.ManyToManyField('Service', blank=True, related_name='knowledge_entries')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'knowledge_base_entries'
        verbose_name_plural = 'Knowledge Base Entries'
        ordering = ['-usage_count', '-updated_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.category}: {self.title}'
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ChatAnalytics(models.Model):
    """
    Stores analytics data for chat sessions.
    
    Tracks metrics like message counts, response times, and user satisfaction.
    Used for monitoring and improving the chat system.
    """
    
    analytics_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(ChatSession, on_delete=models.CASCADE, related_name='analytics')
    total_messages = models.IntegerField(default=0)
    user_messages = models.IntegerField(default=0)
    assistant_messages = models.IntegerField(default=0)
    average_response_time_ms = models.FloatField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    escalated_to_human = models.BooleanField(default=False)
    topics_discussed = models.JSONField(default=list, blank=True)
    actions_taken = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_analytics'
        verbose_name_plural = 'Chat Analytics'
    
    def __str__(self):
        return f'Analytics for {self.session.session_id}'
    
    def update_metrics(self, response_time_ms=None):
        """Update analytics metrics"""
        self.total_messages = self.session.messages.count()
        self.user_messages = self.session.messages.filter(sender_type='user').count()
        self.assistant_messages = self.session.messages.filter(sender_type='assistant').count()
        
        if response_time_ms:
            if self.average_response_time_ms:
                # Calculate running average
                self.average_response_time_ms = (
                    (self.average_response_time_ms * (self.assistant_messages - 1) + response_time_ms) 
                    / self.assistant_messages
                )
            else:
                self.average_response_time_ms = response_time_ms
        
        self.save()
