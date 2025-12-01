"""
Módulo de health checks para o Job Finder
Verifica o status dos serviços e dependências
"""

from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint para monitoramento
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Verificar conexão com o banco de dados
    db_status = check_database()
    health_status['checks']['database'] = db_status
    
    # Verificar outros serviços críticos
    # ... adicionar mais verificações conforme necessário
    
    # Se algum check falhar, marcar como unhealthy
    check_values = health_status['checks'].values()
    if not all(check['status'] == 'healthy' for check in check_values):
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

def check_database():
    """
    Verifica a conexão com o banco de dados
    """
    try:
        db_conn = connections['default']
        c = db_conn.cursor()
        c.execute('SELECT 1')
        c.fetchone()
        return {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error checking database: {e}")
        return {
            'status': 'unhealthy',
            'message': f'Unexpected error: {str(e)}'
        }

def check_cache():
    """
    Verifica o status do cache
    """
    try:
        from django.core.cache import cache
        cache.set('health_check', 'test', 30)
        if cache.get('health_check') == 'test':
            return {
                'status': 'healthy',
                'message': 'Cache is working'
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'Cache is not working properly'
            }
    except Exception as e:
        logger.error(f"Cache check failed: {e}")
        return {
            'status': 'unhealthy',
            'message': f'Cache check failed: {str(e)}'
        }

def check_external_services():
    """
    Verifica serviços externos (ex: Stripe, email, etc.)
    """
    checks = {}
    
    # Verificar Stripe (se configurado)
    try:
        import stripe
        if stripe.api_key:
            # Testar conexão com a API do Stripe
            # stripe.Balance.retrieve()  # Comentado para evitar chamadas reais
            checks['stripe'] = {
                'status': 'healthy',
                'message': 'Stripe API key configured'
            }
        else:
            checks['stripe'] = {
                'status': 'warning',
                'message': 'Stripe API key not configured'
            }
    except Exception as e:
        checks['stripe'] = {
            'status': 'unhealthy',
            'message': f'Stripe check failed: {str(e)}'
        }
    
    return checks