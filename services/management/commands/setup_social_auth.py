"""
Django management command to setup social authentication
Usage: python manage.py setup_social_auth
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os


class Command(BaseCommand):
    help = 'Configura a autenticação social (Google, Facebook, Microsoft)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Configurando autenticação social...\n'))

        # Setup site
        site = self.setup_site()

        # Setup social apps
        self.setup_google(site)
        self.setup_facebook(site)
        self.setup_microsoft(site)

        self.stdout.write(self.style.SUCCESS('\n✨ Configuração concluída!\n'))
        self.stdout.write('📋 Próximos passos:')
        self.stdout.write('1. Acesse: http://localhost:8000/login/')
        self.stdout.write('2. Teste os botões de login social')
        self.stdout.write('\n📖 Consulte OAUTH_SETUP_INSTRUCTIONS.md para mais detalhes\n')

    def setup_site(self):
        """Configura o Site padrão"""
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Job Finder Local'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Site criado'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️  Site já existe'))
        return site

    def setup_google(self, site):
        """Configura Google OAuth"""
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

        # Check if credentials are example values
        example_values = ['your_google_client_id', 'here', '']
        if not client_id or any(ex in client_id.lower() for ex in example_values):
            self.stdout.write(self.style.WARNING('⚠️  Google: Credenciais não configuradas ou usando valores de exemplo'))
            self.stdout.write('   Configure credenciais reais no arquivo .env')
            return

        if not secret or any(ex in secret.lower() for ex in example_values):
            self.stdout.write(self.style.WARNING('⚠️  Google: Secret não configurado ou usando valor de exemplo'))
            return

        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if created:
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✅ Google OAuth configurado'))
        else:
            # Update existing app
            app.client_id = client_id
            app.secret = secret
            app.save()
            if site not in app.sites.all():
                app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✅ Google OAuth atualizado'))

    def setup_facebook(self, site):
        """Configura Facebook OAuth"""
        client_id = os.environ.get('FACEBOOK_CLIENT_ID', '')
        secret = os.environ.get('FACEBOOK_CLIENT_SECRET', '')

        example_values = ['your_facebook_app_id', 'here', '']
        if not client_id or any(ex in client_id.lower() for ex in example_values):
            self.stdout.write(self.style.WARNING('⚠️  Facebook: Credenciais não configuradas ou usando valores de exemplo'))
            return

        if not secret or any(ex in secret.lower() for ex in example_values):
            self.stdout.write(self.style.WARNING('⚠️  Facebook: Secret não configurado ou usando valor de exemplo'))
            return

        app, created = SocialApp.objects.get_or_create(
            provider='facebook',
            defaults={
                'name': 'Facebook OAuth',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if created:
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✅ Facebook OAuth configurado'))
        else:
            # Update existing app
            app.client_id = client_id
            app.secret = secret
            app.save()
            if site not in app.sites.all():
                app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✅ Facebook OAuth atualizado'))

    def setup_microsoft(self, site):
        """Configura Microsoft OAuth"""
        client_id = os.environ.get('MICROSOFT_CLIENT_ID', '')
        secret = os.environ.get('MICROSOFT_CLIENT_SECRET', '')

        example_values = ['your_microsoft_client_id', 'here', '']
        if not client_id or any(ex in client_id.lower() for ex in example_values):
            self.stdout.write(self.style.WARNING('⚠️  Microsoft: Credenciais não configuradas ou usando valores de exemplo'))
            return

        if not secret or any(ex in secret.lower() for ex in example_values):
            self.stdout.write(self.style.WARNING('⚠️  Microsoft: Secret não configurado ou usando valor de exemplo'))
            return

        app, created = SocialApp.objects.get_or_create(
            provider='microsoft',
            defaults={
                'name': 'Microsoft OAuth',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if created:
            app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✅ Microsoft OAuth configurado'))
        else:
            # Update existing app
            app.client_id = client_id
            app.secret = secret
            app.save()
            if site not in app.sites.all():
                app.sites.add(site)
            self.stdout.write(self.style.SUCCESS('✅ Microsoft OAuth atualizado'))
