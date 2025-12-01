"""
API Deprecation Management Views

Admin views for managing API version deprecation.

Requirements: 12.2, 12.3, 12.4
"""
from django.http import JsonResponse
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from datetime import datetime, timedelta
from .deprecation import DeprecationManager, get_version_support_status
from .versioning import APIVersionMiddleware
import json


@method_decorator(staff_member_required, name='dispatch')
class DeprecationDashboardView(View):
    """
    Dashboard for viewing and managing API deprecations.
    """
    
    def get(self, request):
        """
        Display deprecation dashboard.
        """
        schedule = DeprecationManager.get_deprecation_schedule()
        warnings = DeprecationManager.get_all_warnings()
        
        # Get all supported versions
        supported_versions = APIVersionMiddleware.SUPPORTED_VERSIONS
        
        # Build version status list
        version_statuses = []
        for version in supported_versions:
            status = get_version_support_status(version)
            info = DeprecationManager.get_deprecation_info(version)
            
            version_statuses.append({
                'version': version,
                'status': status,
                'deprecation_info': info
            })
        
        context = {
            'version_statuses': version_statuses,
            'warnings': warnings,
            'supported_versions': supported_versions,
            'minimum_support_days': DeprecationManager.MINIMUM_SUPPORT_PERIOD_DAYS
        }
        
        return render(request, 'services/api_deprecation_dashboard.html', context)


@method_decorator(staff_member_required, name='dispatch')
class ScheduleDeprecationView(View):
    """
    API endpoint to schedule a version deprecation.
    """
    
    def post(self, request):
        """
        Schedule a version for deprecation.
        
        POST data:
            version: Version to deprecate (e.g., 'v1')
            deprecation_date: ISO format date (optional, defaults to 6 months)
            reason: Reason for deprecation (optional)
        """
        try:
            data = json.loads(request.body)
            version = data.get('version')
            reason = data.get('reason')
            
            if not version:
                return JsonResponse({
                    'error': 'Version is required'
                }, status=400)
            
            # Parse deprecation date if provided
            deprecation_date = None
            if 'deprecation_date' in data:
                try:
                    deprecation_date = datetime.fromisoformat(data['deprecation_date'])
                except ValueError:
                    return JsonResponse({
                        'error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'
                    }, status=400)
            
            # Schedule deprecation
            result = DeprecationManager.schedule_deprecation(
                version=version,
                deprecation_date=deprecation_date,
                reason=reason
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Version {version} scheduled for deprecation',
                'deprecation': result
            })
            
        except ValueError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to schedule deprecation: {str(e)}'
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class CancelDeprecationView(View):
    """
    API endpoint to cancel a scheduled deprecation.
    """
    
    def post(self, request):
        """
        Cancel a scheduled deprecation.
        
        POST data:
            version: Version to cancel deprecation for
        """
        try:
            data = json.loads(request.body)
            version = data.get('version')
            
            if not version:
                return JsonResponse({
                    'error': 'Version is required'
                }, status=400)
            
            success = DeprecationManager.cancel_deprecation(version)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Deprecation cancelled for version {version}'
                })
            else:
                return JsonResponse({
                    'error': f'No scheduled deprecation found for version {version}'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to cancel deprecation: {str(e)}'
            }, status=500)


@method_decorator(staff_member_required, name='dispatch')
class DeprecationStatusView(View):
    """
    API endpoint to get deprecation status for all versions.
    """
    
    def get(self, request):
        """
        Get deprecation status for all API versions.
        """
        schedule = DeprecationManager.get_deprecation_schedule()
        warnings = DeprecationManager.get_all_warnings()
        supported_versions = APIVersionMiddleware.SUPPORTED_VERSIONS
        
        version_statuses = {}
        for version in supported_versions:
            version_statuses[version] = get_version_support_status(version)
        
        return JsonResponse({
            'supported_versions': supported_versions,
            'version_statuses': version_statuses,
            'deprecation_schedule': schedule,
            'active_warnings': warnings,
            'minimum_support_period_days': DeprecationManager.MINIMUM_SUPPORT_PERIOD_DAYS
        })


class PublicVersionInfoView(View):
    """
    Public endpoint for version information (no authentication required).
    """
    
    def get(self, request):
        """
        Get public information about API versions.
        """
        supported_versions = APIVersionMiddleware.SUPPORTED_VERSIONS
        default_version = APIVersionMiddleware.DEFAULT_VERSION
        
        # Get warnings for public display (without sensitive details)
        warnings = []
        for version in supported_versions:
            warning = DeprecationManager.get_deprecation_warning(version)
            if warning:
                warnings.append({
                    'version': warning['version'],
                    'message': warning['message'],
                    'deprecation_date': warning['deprecation_date'],
                    'days_remaining': warning['days_remaining'],
                    'migration_guide': warning['migration_guide']
                })
        
        return JsonResponse({
            'current_version': default_version,
            'supported_versions': supported_versions,
            'deprecation_warnings': warnings,
            'version_format': 'Specify version in URL path (/api/v1/) or Accept-Version header',
            'changelog': '/api/docs/changelog/',
            'documentation': '/api/docs/'
        })
