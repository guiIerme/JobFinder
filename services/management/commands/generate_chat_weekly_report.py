"""
Django Management Command: Generate Chat Weekly Report

Generates a comprehensive weekly report of chat analytics including:
- Top topics discussed
- Resolution rate
- Common issues
- Performance metrics
- User engagement statistics

Requirements: 7.5
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
from services.chat_models import ChatSession, ChatMessage, ChatAnalytics
from collections import Counter
import json


class Command(BaseCommand):
    help = 'Generate weekly chat analytics report'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to include in report (default: 7)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output file path (default: print to console)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json'],
            help='Output format (default: text)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        output_file = options['output']
        output_format = options['format']
        
        self.stdout.write(self.style.SUCCESS(
            f'Generating chat analytics report for the last {days} days...'
        ))
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate report data
        report_data = self.generate_report(start_date, end_date)
        
        # Format output
        if output_format == 'json':
            output = self.format_json(report_data)
        else:
            output = self.format_text(report_data, days)
        
        # Write output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(
                f'Report saved to {output_file}'
            ))
        else:
            self.stdout.write(output)
    
    def generate_report(self, start_date, end_date):
        """
        Generate comprehensive report data.
        
        Args:
            start_date: Start of reporting period
            end_date: End of reporting period
        
        Returns:
            dict: Report data
        """
        # Get all sessions in period
        sessions = ChatSession.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        total_sessions = sessions.count()
        active_sessions = sessions.filter(is_active=True).count()
        closed_sessions = sessions.filter(is_active=False).count()
        
        # Get analytics data
        analytics_qs = ChatAnalytics.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Calculate aggregate metrics
        analytics_stats = analytics_qs.aggregate(
            avg_response_time=Avg('average_response_time_ms'),
            total_messages=Count('analytics_id'),
            resolved_count=Count('analytics_id', filter=Q(resolved=True)),
            escalated_count=Count('analytics_id', filter=Q(escalated_to_human=True))
        )
        
        # Calculate resolution rate
        resolution_rate = 0
        if total_sessions > 0:
            resolution_rate = round(
                (analytics_stats['resolved_count'] / total_sessions) * 100, 1
            )
        
        # Get satisfaction ratings
        satisfaction_stats = sessions.filter(
            satisfaction_rating__isnull=False
        ).aggregate(
            avg_rating=Avg('satisfaction_rating'),
            rating_count=Count('satisfaction_rating')
        )
        
        # Get top topics discussed
        all_topics = []
        for analytics in analytics_qs:
            all_topics.extend(analytics.topics_discussed)
        
        topic_counter = Counter(all_topics)
        top_topics = topic_counter.most_common(10)
        
        # Get user type distribution
        user_type_stats = sessions.values('user_type').annotate(
            count=Count('session_id')
        ).order_by('-count')
        
        # Get common issues (topics from unresolved sessions)
        unresolved_analytics = analytics_qs.filter(resolved=False)
        common_issues = []
        for analytics in unresolved_analytics:
            common_issues.extend(analytics.topics_discussed)
        
        issue_counter = Counter(common_issues)
        top_issues = issue_counter.most_common(10)
        
        # Get hourly distribution
        hourly_distribution = {}
        for hour in range(24):
            count = ChatMessage.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                created_at__hour=hour
            ).count()
            hourly_distribution[hour] = count
        
        # Find peak hours
        peak_hours = sorted(
            hourly_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Get engagement metrics
        engagement_scores = []
        for analytics in analytics_qs:
            engagement_scores.append(analytics.engagement_score)
        
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        
        # Calculate message statistics
        total_messages = ChatMessage.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        user_messages = ChatMessage.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            sender_type='user'
        ).count()
        
        assistant_messages = ChatMessage.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            sender_type='assistant'
        ).count()
        
        # Build report data
        report = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'sessions': {
                'total': total_sessions,
                'active': active_sessions,
                'closed': closed_sessions
            },
            'messages': {
                'total': total_messages,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'avg_per_session': round(total_messages / total_sessions, 2) if total_sessions > 0 else 0
            },
            'performance': {
                'avg_response_time_ms': round(analytics_stats['avg_response_time'] or 0, 2),
                'resolution_rate': resolution_rate,
                'resolved_count': analytics_stats['resolved_count'],
                'escalated_count': analytics_stats['escalated_count'],
                'avg_engagement_score': round(avg_engagement, 2)
            },
            'satisfaction': {
                'avg_rating': round(satisfaction_stats['avg_rating'] or 0, 2),
                'rating_count': satisfaction_stats['rating_count']
            },
            'top_topics': [
                {'topic': topic, 'count': count}
                for topic, count in top_topics
            ],
            'common_issues': [
                {'issue': issue, 'count': count}
                for issue, count in top_issues
            ],
            'user_types': [
                {'type': stat['user_type'], 'count': stat['count']}
                for stat in user_type_stats
            ],
            'peak_hours': [
                {'hour': hour, 'count': count}
                for hour, count in peak_hours
            ]
        }
        
        return report
    
    def format_text(self, report, days):
        """
        Format report as human-readable text.
        
        Args:
            report: Report data dictionary
            days: Number of days in report
        
        Returns:
            str: Formatted text report
        """
        lines = []
        lines.append('=' * 80)
        lines.append(f'CHAT ANALYTICS WEEKLY REPORT - Last {days} Days')
        lines.append('=' * 80)
        lines.append(f"Period: {report['period']['start_date']} to {report['period']['end_date']}")
        lines.append('')
        
        # Session Statistics
        lines.append('SESSION STATISTICS')
        lines.append('-' * 80)
        lines.append(f"Total Sessions: {report['sessions']['total']}")
        lines.append(f"Active Sessions: {report['sessions']['active']}")
        lines.append(f"Closed Sessions: {report['sessions']['closed']}")
        lines.append('')
        
        # Message Statistics
        lines.append('MESSAGE STATISTICS')
        lines.append('-' * 80)
        lines.append(f"Total Messages: {report['messages']['total']}")
        lines.append(f"User Messages: {report['messages']['user_messages']}")
        lines.append(f"Assistant Messages: {report['messages']['assistant_messages']}")
        lines.append(f"Average Messages per Session: {report['messages']['avg_per_session']}")
        lines.append('')
        
        # Performance Metrics
        lines.append('PERFORMANCE METRICS')
        lines.append('-' * 80)
        lines.append(f"Average Response Time: {report['performance']['avg_response_time_ms']}ms")
        lines.append(f"Resolution Rate: {report['performance']['resolution_rate']}%")
        lines.append(f"Resolved Sessions: {report['performance']['resolved_count']}")
        lines.append(f"Escalated to Human: {report['performance']['escalated_count']}")
        lines.append(f"Average Engagement Score: {report['performance']['avg_engagement_score']}")
        lines.append('')
        
        # Satisfaction
        lines.append('USER SATISFACTION')
        lines.append('-' * 80)
        lines.append(f"Average Rating: {report['satisfaction']['avg_rating']}/5.0")
        lines.append(f"Total Ratings: {report['satisfaction']['rating_count']}")
        lines.append('')
        
        # Top Topics
        lines.append('TOP TOPICS DISCUSSED')
        lines.append('-' * 80)
        if report['top_topics']:
            for i, topic_data in enumerate(report['top_topics'], 1):
                lines.append(f"{i}. {topic_data['topic']}: {topic_data['count']} times")
        else:
            lines.append('No topics data available')
        lines.append('')
        
        # Common Issues
        lines.append('COMMON ISSUES (Unresolved)')
        lines.append('-' * 80)
        if report['common_issues']:
            for i, issue_data in enumerate(report['common_issues'], 1):
                lines.append(f"{i}. {issue_data['issue']}: {issue_data['count']} times")
        else:
            lines.append('No unresolved issues')
        lines.append('')
        
        # User Type Distribution
        lines.append('USER TYPE DISTRIBUTION')
        lines.append('-' * 80)
        for user_type_data in report['user_types']:
            lines.append(f"{user_type_data['type'].title()}: {user_type_data['count']} sessions")
        lines.append('')
        
        # Peak Hours
        lines.append('PEAK USAGE HOURS')
        lines.append('-' * 80)
        for peak_data in report['peak_hours']:
            hour = peak_data['hour']
            count = peak_data['count']
            lines.append(f"{hour:02d}:00 - {hour+1:02d}:00: {count} messages")
        lines.append('')
        
        lines.append('=' * 80)
        lines.append(f"Report generated at: {timezone.now().isoformat()}")
        lines.append('=' * 80)
        
        return '\n'.join(lines)
    
    def format_json(self, report):
        """
        Format report as JSON.
        
        Args:
            report: Report data dictionary
        
        Returns:
            str: JSON formatted report
        """
        report['generated_at'] = timezone.now().isoformat()
        return json.dumps(report, indent=2, ensure_ascii=False)
