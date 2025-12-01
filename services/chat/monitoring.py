"""
Chat Monitoring - Health checks and alerting for Chat IA Assistente

This module provides monitoring functionality including:
- Health checks for error rates, response times, and active sessions
- Alert sending via email and logging
- Metrics collection for analytics

Requirements: 7.1, 7.2
"""

from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ChatMonitor:
    """
    Monitor chat system health and send alerts when thresholds are exceeded.
    
    This class provides methods to check various metrics and send alerts
    when issues are detected.
    """
    
    @staticmethod
    def check_error_rate():
        """
        Check error rate and send alert if threshold exceeded.
        
        Thresholds:
        - Warning: > 5%
        - Critical: > 10%
        
        Requirements: 7.1, 7.2
        """
        from services.chat_models import ChatAnalytics
        
        try:
            # Get sessions from last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_sessions = ChatAnalytics.objects.filter(
                created_at__gte=one_hour_ago
            )
            
            total = recent_sessions.count()
            if total == 0:
                logger.info("No chat sessions in the last hour")
                return
            
            # Count sessions with errors (escalated or with issues)
            errors = recent_sessions.filter(escalated_to_human=True).count()
            error_rate = (errors / total) * 100
            
            logger.info(
                f"Error rate check: {error_rate:.1f}% ({errors}/{total})"
            )
            
            if error_rate > 10:  # Critical threshold
                ChatMonitor.send_alert(
                    subject='[CRITICAL] High Chat Error Rate',
                    message=f'Error rate is {error_rate:.1f}% (threshold: 10%)\n'
                           f'Total sessions: {total}\n'
                           f'Sessions with errors: {errors}\n'
                           f'Time period: Last hour\n\n'
                           f'Action required: Investigate chat logs and OpenAI API status',
                    level='critical'
                )
            elif error_rate > 5:  # Warning threshold
                ChatMonitor.send_alert(
                    subject='[WARNING] Elevated Chat Error Rate',
                    message=f'Error rate is {error_rate:.1f}% (threshold: 5%)\n'
                           f'Total sessions: {total}\n'
                           f'Sessions with errors: {errors}\n'
                           f'Time period: Last hour\n\n'
                           f'Action recommended: Monitor situation',
                    level='warning'
                )
                
        except Exception as e:
            logger.error(f"Error checking error rate: {e}", exc_info=True)
    
    @staticmethod
    def check_response_time():
        """
        Check average response time and alert if slow.
        
        Thresholds:
        - Warning: > 2 seconds
        - Critical: > 5 seconds
        
        Requirements: 7.1, 7.2, 8.4
        """
        from services.chat_models import ChatAnalytics
        
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_sessions = ChatAnalytics.objects.filter(
                created_at__gte=one_hour_ago,
                average_response_time_ms__isnull=False
            )
            
            if not recent_sessions.exists():
                logger.info("No chat sessions with response time data in the last hour")
                return
            
            avg_response_time = recent_sessions.aggregate(
                avg=models.Avg('average_response_time_ms')
            )['avg']
            
            logger.info(
                f"Response time check: {avg_response_time:.0f}ms average"
            )
            
            if avg_response_time > 5000:  # Critical: > 5s
                ChatMonitor.send_alert(
                    subject='[CRITICAL] Slow Chat Response Time',
                    message=f'Average response time is {avg_response_time:.0f}ms (threshold: 5000ms)\n'
                           f'Time period: Last hour\n\n'
                           f'Action required: Check OpenAI API status and server resources',
                    level='critical'
                )
            elif avg_response_time > 2000:  # Warning: > 2s
                ChatMonitor.send_alert(
                    subject='[WARNING] Elevated Chat Response Time',
                    message=f'Average response time is {avg_response_time:.0f}ms (threshold: 2000ms)\n'
                           f'Time period: Last hour\n\n'
                           f'Action recommended: Monitor OpenAI API performance',
                    level='warning'
                )
                
        except Exception as e:
            logger.error(f"Error checking response time: {e}", exc_info=True)
    
    @staticmethod
    def check_active_sessions():
        """
        Check number of active sessions against capacity.
        
        Thresholds:
        - Warning: > 80% capacity
        - Critical: > 90% capacity
        
        Requirements: 7.1, 7.2, 8.1
        """
        from services.chat_models import ChatSession
        
        try:
            active_count = ChatSession.objects.filter(is_active=True).count()
            max_sessions = settings.CHAT_CONFIG['MAX_CONCURRENT_SESSIONS']
            
            usage_pct = (active_count / max_sessions) * 100
            
            logger.info(
                f"Active sessions check: {active_count}/{max_sessions} ({usage_pct:.1f}%)"
            )
            
            if usage_pct > 90:  # Critical: > 90%
                ChatMonitor.send_alert(
                    subject='[CRITICAL] High Chat Session Usage',
                    message=f'Active sessions: {active_count}/{max_sessions} ({usage_pct:.1f}%)\n'
                           f'System is near capacity\n\n'
                           f'Action required: Consider scaling resources or increasing limits',
                    level='critical'
                )
            elif usage_pct > 80:  # Warning: > 80%
                ChatMonitor.send_alert(
                    subject='[WARNING] Elevated Chat Session Usage',
                    message=f'Active sessions: {active_count}/{max_sessions} ({usage_pct:.1f}%)\n'
                           f'System usage is high\n\n'
                           f'Action recommended: Monitor capacity',
                    level='warning'
                )
                
        except Exception as e:
            logger.error(f"Error checking active sessions: {e}", exc_info=True)
    
    @staticmethod
    def check_cache_effectiveness():
        """
        Check cache hit rate.
        
        Threshold:
        - Warning: < 30% hit rate
        
        Requirements: 7.1, 8.2
        """
        from django.core.cache import cache
        
        try:
            # Get cache stats (if available)
            # Note: This depends on cache backend supporting stats
            cache_stats = cache.get('chat_cache_stats', {
                'hits': 0,
                'misses': 0
            })
            
            total = cache_stats['hits'] + cache_stats['misses']
            if total == 0:
                logger.info("No cache statistics available")
                return
            
            hit_rate = (cache_stats['hits'] / total) * 100
            
            logger.info(
                f"Cache effectiveness check: {hit_rate:.1f}% hit rate "
                f"({cache_stats['hits']}/{total})"
            )
            
            if hit_rate < 30:  # Warning: < 30%
                ChatMonitor.send_alert(
                    subject='[WARNING] Low Chat Cache Hit Rate',
                    message=f'Cache hit rate is {hit_rate:.1f}% (threshold: 30%)\n'
                           f'Hits: {cache_stats["hits"]}\n'
                           f'Misses: {cache_stats["misses"]}\n\n'
                           f'Action recommended: Review cache strategy and TTL settings',
                    level='warning'
                )
                
        except Exception as e:
            logger.error(f"Error checking cache effectiveness: {e}", exc_info=True)
    
    @staticmethod
    def check_satisfaction_rating():
        """
        Check average satisfaction rating.
        
        Threshold:
        - Warning: < 3.5 stars
        
        Requirements: 7.1, 7.2, 6.4
        """
        from services.chat_models import ChatSession
        
        try:
            # Get sessions from last 7 days with ratings
            seven_days_ago = datetime.now() - timedelta(days=7)
            rated_sessions = ChatSession.objects.filter(
                created_at__gte=seven_days_ago,
                satisfaction_rating__isnull=False
            )
            
            if not rated_sessions.exists():
                logger.info("No rated chat sessions in the last 7 days")
                return
            
            avg_rating = rated_sessions.aggregate(
                avg=models.Avg('satisfaction_rating')
            )['avg']
            
            total_ratings = rated_sessions.count()
            
            logger.info(
                f"Satisfaction rating check: {avg_rating:.2f}/5.0 "
                f"({total_ratings} ratings)"
            )
            
            if avg_rating < 3.5:  # Warning: < 3.5
                ChatMonitor.send_alert(
                    subject='[WARNING] Low Chat Satisfaction Rating',
                    message=f'Average satisfaction rating is {avg_rating:.2f}/5.0 (threshold: 3.5)\n'
                           f'Total ratings: {total_ratings}\n'
                           f'Time period: Last 7 days\n\n'
                           f'Action recommended: Review chat quality and knowledge base',
                    level='warning'
                )
                
        except Exception as e:
            logger.error(f"Error checking satisfaction rating: {e}", exc_info=True)
    
    @staticmethod
    def send_alert(subject, message, level='info'):
        """
        Send alert via email and log.
        
        Args:
            subject: Alert subject line
            message: Alert message body
            level: Alert level ('info', 'warning', 'critical')
        """
        # Log the alert
        log_level = {
            'info': logging.INFO,
            'warning': logging.WARNING,
            'critical': logging.CRITICAL
        }.get(level, logging.INFO)
        
        logger.log(
            log_level,
            f"ALERT: {subject}\n{message}"
        )
        
        # Send email if configured
        if hasattr(settings, 'CHAT_ALERT_EMAILS') and settings.CHAT_ALERT_EMAILS:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.CHAT_ALERT_EMAILS,
                    fail_silently=False,
                )
                logger.info(f"Alert email sent: {subject}")
            except Exception as e:
                logger.error(f"Failed to send alert email: {e}", exc_info=True)
        else:
            logger.warning("CHAT_ALERT_EMAILS not configured, alert not sent via email")
    
    @staticmethod
    def run_all_checks():
        """
        Run all health checks.
        
        This method runs all monitoring checks and is intended to be called
        periodically (e.g., via cron job).
        """
        logger.info("Starting chat system health checks")
        
        ChatMonitor.check_error_rate()
        ChatMonitor.check_response_time()
        ChatMonitor.check_active_sessions()
        ChatMonitor.check_cache_effectiveness()
        ChatMonitor.check_satisfaction_rating()
        
        logger.info("Chat system health checks complete")
    
    @staticmethod
    def get_system_status():
        """
        Get current system status summary.
        
        Returns:
            dict: System status information
        """
        from services.chat_models import ChatSession, ChatAnalytics
        
        try:
            # Active sessions
            active_sessions = ChatSession.objects.filter(is_active=True).count()
            max_sessions = settings.CHAT_CONFIG['MAX_CONCURRENT_SESSIONS']
            
            # Recent analytics (last hour)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_analytics = ChatAnalytics.objects.filter(
                created_at__gte=one_hour_ago
            )
            
            # Calculate metrics
            total_sessions = recent_analytics.count()
            avg_response_time = recent_analytics.aggregate(
                avg=models.Avg('average_response_time_ms')
            )['avg'] or 0
            
            escalated = recent_analytics.filter(escalated_to_human=True).count()
            error_rate = (escalated / total_sessions * 100) if total_sessions > 0 else 0
            
            # Recent ratings (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            avg_rating = ChatSession.objects.filter(
                created_at__gte=seven_days_ago,
                satisfaction_rating__isnull=False
            ).aggregate(
                avg=models.Avg('satisfaction_rating')
            )['avg'] or 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'active_sessions': active_sessions,
                'max_sessions': max_sessions,
                'capacity_usage_pct': (active_sessions / max_sessions * 100) if max_sessions > 0 else 0,
                'sessions_last_hour': total_sessions,
                'avg_response_time_ms': round(avg_response_time, 2),
                'error_rate_pct': round(error_rate, 2),
                'avg_satisfaction_rating': round(avg_rating, 2),
                'status': 'healthy' if error_rate < 5 and avg_response_time < 2000 else 'degraded'
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}", exc_info=True)
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
