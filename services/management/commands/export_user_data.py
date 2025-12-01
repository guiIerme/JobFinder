import json
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from services.models import UserProfile, Order, CustomService, Chat, Message
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Export user data for GDPR compliance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            required=True,
            help='ID of the user whose data should be exported',
        )
        parser.add_argument(
            '--format',
            choices=['json', 'csv'],
            default='json',
            help='Export format (default: json)',
        )
        parser.add_argument(
            '--output-dir',
            default='user_data_exports',
            help='Directory to save exported files (default: user_data_exports)',
        )

    def handle(self, *args, **options):
        try:
            # Get the user
            user = User.objects.get(id=options['user_id'])
            
            # Create output directory if it doesn't exist
            os.makedirs(options['output_dir'], exist_ok=True)
            
            # Export user data
            user_data = self.export_user_data(user)
            
            # Export related data
            profile_data = self.export_user_profile(user)
            orders_data = self.export_user_orders(user)
            services_data = self.export_user_custom_services(user)
            chats_data = self.export_user_chats(user)
            
            # Combine all data
            export_data = {
                'user': user_data,
                'profile': profile_data,
                'orders': orders_data,
                'custom_services': services_data,
                'chats': chats_data,
                'export_date': datetime.now().isoformat(),
                'export_user': 'System'
            }
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_data_{user.id}_{timestamp}.{options['format']}"
            filepath = os.path.join(options['output_dir'], filename)
            
            # Export in the requested format
            if options['format'] == 'json':
                self.export_as_json(export_data, filepath)
            else:
                self.export_as_csv(export_data, filepath, user)
            
            self.stdout.write(
                f'Successfully exported user data for {user.username} to {filepath}'
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                f'User with ID {options["user_id"]} does not exist'
            )
        except Exception as e:
            self.stdout.write(
                f'Error exporting user data: {str(e)}'
            )

    def export_user_data(self, user):
        """Export basic user data"""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }

    def export_user_profile(self, user):
        """Export user profile data"""
        try:
            profile = UserProfile.objects.get(user=user)
            return {
                'id': profile.id,
                'user_type': profile.user_type,
                'phone': profile.phone,
                'address': profile.address,
                'number': profile.number,
                'complement': profile.complement,
                'city': profile.city,
                'state': profile.state,
                'zip_code': profile.zip_code,
                'rating': str(profile.rating) if profile.rating else None,
                'review_count': profile.review_count,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat(),
            }
        except UserProfile.DoesNotExist:
            return None

    def export_user_orders(self, user):
        """Export user's orders"""
        orders = Order.objects.filter(customer=user)
        orders_data = []
        
        for order in orders:
            order_data = {
                'id': order.id,
                'service_id': order.service.id if order.service else None,
                'service_name': order.service.name if order.service else None,
                'professional_id': order.professional.id if order.professional else None,
                'professional_username': order.professional.username if order.professional else None,
                'status': order.status,
                'scheduled_date': order.scheduled_date.isoformat(),
                'address': order.address,
                'notes': order.notes,
                'total_price': str(order.total_price),
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
            }
            orders_data.append(order_data)
        
        return orders_data

    def export_user_custom_services(self, user):
        """Export user's custom services (if they are a provider)"""
        services = CustomService.objects.filter(provider=user)
        services_data = []
        
        for service in services:
            service_data = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category,
                'estimated_price': str(service.estimated_price),
                'estimated_duration': str(service.estimated_duration),
                'is_active': service.is_active,
                'created_at': service.created_at.isoformat(),
                'updated_at': service.updated_at.isoformat(),
            }
            services_data.append(service_data)
        
        return services_data

    def export_user_chats(self, user):
        """Export user's chats and messages"""
        # Get chats where user is either customer or professional
        chats = Chat.objects.filter(
            models.Q(customer=user) | models.Q(professional=user)
        )
        
        chats_data = []
        
        for chat in chats:
            # Get messages in this chat
            messages = Message.objects.filter(chat=chat)
            messages_data = []
            
            for message in messages:
                message_data = {
                    'id': message.id,
                    'sender_id': message.sender.id if message.sender else None,
                    'sender_username': message.sender.username if message.sender else None,
                    'content': message.content,
                    'message_type': message.message_type,
                    'status': message.status,
                    'timestamp': message.timestamp.isoformat(),
                    'is_ai_message': message.is_ai_message,
                }
                messages_data.append(message_data)
            
            chat_data = {
                'id': chat.id,
                'customer_id': chat.customer.id,
                'customer_username': chat.customer.username,
                'professional_id': chat.professional.id,
                'professional_username': chat.professional.username,
                'order_id': chat.order.id if chat.order else None,
                'created_at': chat.created_at.isoformat(),
                'updated_at': chat.updated_at.isoformat(),
                'messages': messages_data,
            }
            chats_data.append(chat_data)
        
        return chats_data

    def export_as_json(self, data, filepath):
        """Export data as JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, cls=DjangoJSONEncoder, ensure_ascii=False)

    def export_as_csv(self, data, filepath, user):
        """Export data as CSV (simplified version)"""
        # For CSV, we'll create multiple files for different data types
        base_path = filepath.replace('.csv', '')
        
        # Export user data
        user_file = f"{base_path}_user.csv"
        with open(user_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Field', 'Value'])
            for key, value in data['user'].items():
                writer.writerow([key, value])
        
        # Export profile data
        if data['profile']:
            profile_file = f"{base_path}_profile.csv"
            with open(profile_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Field', 'Value'])
                for key, value in data['profile'].items():
                    writer.writerow([key, value])
        
        self.stdout.write(
            f'Created multiple CSV files with prefix {base_path}_'
        )