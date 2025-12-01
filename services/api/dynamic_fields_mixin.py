"""
Mixin for dynamic field selection in serializers.

Allows clients to specify which fields they want in the response using
query parameters, reducing payload size and improving performance.
"""
from rest_framework import serializers


class DynamicFieldsMixin:
    """
    A mixin that allows dynamic field selection in serializers.
    
    Usage:
    - ?fields=field1,field2,field3 - Only return specified fields
    - ?compact=true - Return minimal set of fields for compact response
    
    The serializer must define a 'compact_fields' attribute for compact mode.
    """
    
    def __init__(self, *args, **kwargs):
        # Get the request context
        request = kwargs.get('context', {}).get('request')
        
        # Call parent constructor
        super().__init__(*args, **kwargs)
        
        if not request:
            return
        
        # Check for compact mode
        compact = request.query_params.get('compact', '').lower() == 'true'
        if compact and hasattr(self.Meta, 'compact_fields'):
            # Use compact fields if defined
            allowed = set(self.Meta.compact_fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
            return
        
        # Check for field selection
        fields_param = request.query_params.get('fields')
        if fields_param:
            # Split comma-separated fields
            fields = [f.strip() for f in fields_param.split(',') if f.strip()]
            allowed = set(fields)
            existing = set(self.fields.keys())
            
            # Remove fields not in the allowed list
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class CompactResponseMixin:
    """
    Mixin for views to support compact JSON responses.
    
    When ?compact=true is passed, the response JSON will be minified
    (no extra whitespace) to reduce payload size.
    """
    
    def finalize_response(self, request, response, *args, **kwargs):
        """Override to modify response rendering based on compact parameter"""
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Check if compact mode is requested
        compact = request.query_params.get('compact', '').lower() == 'true'
        if compact and hasattr(response, 'accepted_renderer'):
            # Set compact rendering (no indentation)
            if hasattr(response.accepted_renderer, 'compact'):
                response.accepted_renderer.compact = True
        
        return response
