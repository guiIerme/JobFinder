"""
Advanced Search API Views

Provides advanced search functionality with text search, filtering,
geographic search, and multiple ordering options.

Performance optimizations:
- Database query optimization with select_related
- Intelligent caching with automatic invalidation
- Index-based filtering for fast lookups
- Response time monitoring
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Q, F, Value, FloatField, Case, When
from django.db.models.functions import Coalesce
from decimal import Decimal
import math
import time
import logging

from services.models import CustomService, UserProfile
from services.cache_manager import CacheManager
from .serializers import CustomServiceSerializer, UserProfileSerializer
from .pagination import OptimizedPagination

logger = logging.getLogger(__name__)


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula.
    
    Args:
        lat1 (float): Latitude of point 1 in degrees
        lon1 (float): Longitude of point 1 in degrees
        lat2 (float): Latitude of point 2 in degrees
        lon2 (float): Longitude of point 2 in degrees
    
    Returns:
        float: Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


class AdvancedSearchView(APIView):
    """
    Advanced search endpoint with text search, filtering, and ordering.
    
    Supports:
    - Text search across multiple fields (q parameter)
    - Category filtering
    - Price range filtering (min_price, max_price)
    - Rating filtering (min_rating)
    - Multiple ordering options (sort parameter)
    
    Example:
        GET /api/v1/search/?q=encanamento&category=plumbing&min_price=50&max_price=200&sort=price
    """
    
    permission_classes = [AllowAny]
    pagination_class = OptimizedPagination
    
    def get(self, request):
        """
        Handle GET request for advanced search.
        
        Performance target: < 500ms response time for 95% of requests
        
        Query Parameters:
            q (str): Search query for text search
            category (str): Filter by service category
            min_price (float): Minimum price filter
            max_price (float): Maximum price filter
            min_rating (float): Minimum provider rating
            lat (float): Latitude for geographic search
            lng (float): Longitude for geographic search
            radius (float): Search radius in kilometers (default: 10)
            sort (str): Sort order (relevance, price, -price, rating, -rating, distance)
            page (int): Page number for pagination
            page_size (int): Items per page (10-100)
        
        Returns:
            Response: Paginated search results with metadata
        """
        # Start performance timer
        start_time = time.time()
        
        # Extract query parameters
        query = request.query_params.get('q', '').strip()
        category = request.query_params.get('category', '').strip()
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        min_rating = request.query_params.get('min_rating', None)
        lat = request.query_params.get('lat', None)
        lng = request.query_params.get('lng', None)
        radius = request.query_params.get('radius', '10')
        sort = request.query_params.get('sort', 'relevance')
        
        # Generate cache key
        cache_key = CacheManager.get_cache_key(
            'search:services',
            q=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            lat=lat,
            lng=lng,
            radius=radius,
            sort=sort,
            page=request.query_params.get('page', 1),
            page_size=request.query_params.get('page_size', 20)
        )
        
        # Try to get from cache
        cached_result = CacheManager.get(cache_key)
        if cached_result is not None:
            # Calculate response time for cached result
            response_time = (time.time() - start_time) * 1000
            
            # Update performance metadata for cached response
            cached_result['performance'] = {
                'response_time_ms': round(response_time, 2),
                'cached': True,
                'target_met': True  # Cached responses are always fast
            }
            
            return Response(cached_result)
        
        # Build queryset
        queryset = self._build_queryset(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating
        )
        
        # Apply geographic filtering if coordinates provided
        user_lat = None
        user_lng = None
        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
                radius_km = float(radius)
                
                # Filter by providers with location data
                queryset = queryset.filter(
                    provider__userprofile__latitude__isnull=False,
                    provider__userprofile__longitude__isnull=False
                )
                
                # Calculate distance for each result (done in Python after query)
                # For better performance with large datasets, consider using PostGIS
                
            except (ValueError, TypeError):
                user_lat = None
                user_lng = None
        
        # Apply ordering
        queryset = self._apply_ordering(queryset, sort, user_lat, user_lng)
        
        # Convert to list if we need to filter by distance
        if user_lat and user_lng and sort != 'distance':
            # Filter by radius
            try:
                radius_km = float(radius)
                results_list = []
                for service in queryset:
                    if (service.provider.userprofile.latitude and 
                        service.provider.userprofile.longitude):
                        distance = haversine_distance(
                            user_lat, user_lng,
                            float(service.provider.userprofile.latitude),
                            float(service.provider.userprofile.longitude)
                        )
                        if distance <= radius_km:
                            # Add distance as attribute for serialization
                            service.distance = round(distance, 2)
                            results_list.append(service)
                queryset = results_list
            except (ValueError, TypeError):
                pass
        elif user_lat and user_lng and sort == 'distance':
            # Calculate distance and sort
            results_list = []
            for service in queryset:
                if (service.provider.userprofile.latitude and 
                    service.provider.userprofile.longitude):
                    distance = haversine_distance(
                        user_lat, user_lng,
                        float(service.provider.userprofile.latitude),
                        float(service.provider.userprofile.longitude)
                    )
                    try:
                        radius_km = float(radius)
                        if distance <= radius_km:
                            service.distance = round(distance, 2)
                            results_list.append(service)
                    except (ValueError, TypeError):
                        service.distance = round(distance, 2)
                        results_list.append(service)
            
            # Sort by distance
            results_list.sort(key=lambda x: x.distance)
            queryset = results_list
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize data
        serializer = CustomServiceSerializer(paginated_queryset, many=True)
        serialized_data = serializer.data
        
        # Add distance to serialized data if available
        if user_lat and user_lng:
            for i, item in enumerate(serialized_data):
                if hasattr(paginated_queryset[i], 'distance'):
                    item['distance_km'] = paginated_queryset[i].distance
        
        # Get paginated response
        response_data = paginator.get_paginated_response(serialized_data).data
        
        # Add search metadata
        response_data['search_metadata'] = {
            'query': query,
            'filters_applied': {
                'category': category if category else None,
                'min_price': min_price,
                'max_price': max_price,
                'min_rating': min_rating,
                'location': {
                    'lat': lat,
                    'lng': lng,
                    'radius_km': radius
                } if lat and lng else None,
            },
            'sort': sort
        }
        
        # Calculate and log response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Add performance metadata to response
        response_data['performance'] = {
            'response_time_ms': round(response_time, 2),
            'cached': False,
            'target_met': response_time < 500
        }
        
        # Log slow queries for monitoring
        if response_time > 500:
            logger.warning(
                f"Slow search query: {response_time:.2f}ms - "
                f"q={query}, category={category}, sort={sort}"
            )
        
        # Cache the result
        CacheManager.set(cache_key, response_data, timeout=CacheManager.TIMEOUT_SEARCH)
        
        return Response(response_data)
    
    def _build_queryset(self, query, category, min_price, max_price, min_rating):
        """
        Build the base queryset with filters applied.
        
        Optimizations:
        - Uses select_related to reduce database queries
        - Applies filters in order of selectivity (most restrictive first)
        - Uses indexed fields for better performance
        
        Args:
            query (str): Text search query
            category (str): Category filter
            min_price (str): Minimum price
            max_price (str): Maximum price
            min_rating (str): Minimum rating
        
        Returns:
            QuerySet: Filtered queryset
        """
        # Start with active services and optimize with select_related
        # select_related reduces queries from N+1 to 1 for related objects
        queryset = CustomService.objects.filter(is_active=True).select_related(
            'provider', 'provider__userprofile'
        )
        
        # Apply category filter first (most selective, uses index)
        if category:
            queryset = queryset.filter(category=category)
        
        # Price range filter (uses index)
        if min_price:
            try:
                queryset = queryset.filter(estimated_price__gte=Decimal(min_price))
            except (ValueError, TypeError):
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(estimated_price__lte=Decimal(max_price))
            except (ValueError, TypeError):
                pass
        
        # Rating filter (filter by provider rating, uses index)
        if min_rating:
            try:
                min_rating_value = float(min_rating)
                queryset = queryset.filter(
                    provider__userprofile__rating__gte=min_rating_value
                )
            except (ValueError, TypeError):
                pass
        
        # Text search across multiple fields (applied last as it's least selective)
        # Note: For better performance with large datasets, consider using
        # PostgreSQL full-text search or Elasticsearch
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(provider__username__icontains=query) |
                Q(provider__first_name__icontains=query) |
                Q(provider__last_name__icontains=query) |
                Q(provider__userprofile__bio__icontains=query) |
                Q(provider__userprofile__specialties__icontains=query)
            )
        
        return queryset
    
    def _apply_ordering(self, queryset, sort, user_lat=None, user_lng=None):
        """
        Apply ordering to the queryset based on sort parameter.
        
        Supports multiple sorting options:
        - price: Lowest price first
        - -price: Highest price first
        - rating: Lowest rating first (rarely used)
        - -rating: Highest rating first (most common)
        - name: Alphabetical A-Z
        - -name: Alphabetical Z-A
        - distance: Nearest first (requires lat/lng)
        - relevance: Most recent first (default)
        
        Args:
            queryset (QuerySet): Base queryset
            sort (str): Sort parameter
            user_lat (float): User latitude for distance sorting
            user_lng (float): User longitude for distance sorting
        
        Returns:
            QuerySet: Ordered queryset
        """
        # Use Coalesce to handle NULL ratings (treat as 0)
        if sort == 'price':
            # Lowest price first, then most recent
            return queryset.order_by('estimated_price', '-created_at')
        elif sort == '-price':
            # Highest price first, then most recent
            return queryset.order_by('-estimated_price', '-created_at')
        elif sort == 'rating':
            # Lowest rating first (rarely used), handle NULLs
            return queryset.annotate(
                rating_value=Coalesce('provider__userprofile__rating', Value(0.0), output_field=FloatField())
            ).order_by('rating_value', '-created_at')
        elif sort == '-rating':
            # Highest rating first (most common), handle NULLs
            return queryset.annotate(
                rating_value=Coalesce('provider__userprofile__rating', Value(0.0), output_field=FloatField())
            ).order_by('-rating_value', '-created_at')
        elif sort == 'name':
            # Alphabetical A-Z
            return queryset.order_by('name', '-created_at')
        elif sort == '-name':
            # Alphabetical Z-A
            return queryset.order_by('-name', '-created_at')
        elif sort == 'distance':
            # Distance sorting is handled in get() method after distance calculation
            # Return queryset as-is, will be sorted after distance computation
            return queryset
        elif sort == 'relevance':
            # Explicit relevance: most recent first
            return queryset.order_by('-created_at')
        else:
            # Default: relevance (most recent first)
            return queryset.order_by('-created_at')


class ProfessionalSearchView(APIView):
    """
    Search endpoint specifically for professionals.
    
    Supports:
    - Text search across professional profiles
    - Location filtering (city, state)
    - Rating filtering
    - Availability filtering
    - Verification status filtering
    
    Example:
        GET /api/v1/search/professionals/?q=eletricista&city=São Paulo&min_rating=4.0
    """
    
    permission_classes = [AllowAny]
    pagination_class = OptimizedPagination
    
    def get(self, request):
        """
        Handle GET request for professional search.
        
        Performance target: < 500ms response time for 95% of requests
        
        Query Parameters:
            q (str): Search query
            city (str): Filter by city
            state (str): Filter by state
            min_rating (float): Minimum rating
            is_verified (bool): Filter verified professionals
            is_available (bool): Filter available professionals
            lat (float): Latitude for geographic search
            lng (float): Longitude for geographic search
            radius (float): Search radius in kilometers (default: 10)
            sort (str): Sort order (rating, -rating, experience, -experience, distance)
        
        Returns:
            Response: Paginated search results
        """
        # Start performance timer
        start_time = time.time()
        
        # Extract query parameters
        query = request.query_params.get('q', '').strip()
        city = request.query_params.get('city', '').strip()
        state = request.query_params.get('state', '').strip()
        min_rating = request.query_params.get('min_rating', None)
        is_verified = request.query_params.get('is_verified', None)
        is_available = request.query_params.get('is_available', None)
        lat = request.query_params.get('lat', None)
        lng = request.query_params.get('lng', None)
        radius = request.query_params.get('radius', '10')
        sort = request.query_params.get('sort', '-rating')
        
        # Generate cache key
        cache_key = CacheManager.get_cache_key(
            'search:professionals',
            q=query,
            city=city,
            state=state,
            min_rating=min_rating,
            is_verified=is_verified,
            is_available=is_available,
            lat=lat,
            lng=lng,
            radius=radius,
            sort=sort,
            page=request.query_params.get('page', 1),
            page_size=request.query_params.get('page_size', 20)
        )
        
        # Try to get from cache
        cached_result = CacheManager.get(cache_key)
        if cached_result is not None:
            # Calculate response time for cached result
            response_time = (time.time() - start_time) * 1000
            
            # Update performance metadata for cached response
            cached_result['performance'] = {
                'response_time_ms': round(response_time, 2),
                'cached': True,
                'target_met': True  # Cached responses are always fast
            }
            
            return Response(cached_result)
        
        # Build queryset - only professionals
        queryset = UserProfile.objects.filter(
            user_type='professional'
        ).select_related('user')
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(bio__icontains=query) |
                Q(specialties__icontains=query) |
                Q(business_name__icontains=query)
            )
        
        # Location filters
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        if state:
            queryset = queryset.filter(state__iexact=state)
        
        # Rating filter
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except (ValueError, TypeError):
                pass
        
        # Verification filter
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Availability filter
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        # Apply geographic filtering if coordinates provided
        user_lat = None
        user_lng = None
        if lat and lng:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
                
                # Filter by professionals with location data
                queryset = queryset.filter(
                    latitude__isnull=False,
                    longitude__isnull=False
                )
            except (ValueError, TypeError):
                user_lat = None
                user_lng = None
        
        # Apply ordering (except distance which is handled later)
        if sort == 'rating':
            queryset = queryset.order_by('rating', '-created_at')
        elif sort == '-rating':
            queryset = queryset.order_by('-rating', '-created_at')
        elif sort == 'experience':
            queryset = queryset.order_by('experience_years', '-created_at')
        elif sort == '-experience':
            queryset = queryset.order_by('-experience_years', '-created_at')
        elif sort == 'name':
            queryset = queryset.order_by('user__first_name', 'user__last_name')
        elif sort == 'distance':
            # Distance sorting handled after calculation
            pass
        else:
            queryset = queryset.order_by('-rating', '-created_at')
        
        # Calculate distance and filter by radius if coordinates provided
        if user_lat and user_lng:
            try:
                radius_km = float(radius)
                results_list = []
                
                for profile in queryset:
                    if profile.latitude and profile.longitude:
                        distance = haversine_distance(
                            user_lat, user_lng,
                            float(profile.latitude),
                            float(profile.longitude)
                        )
                        if distance <= radius_km:
                            profile.distance = round(distance, 2)
                            results_list.append(profile)
                
                # Sort by distance if requested
                if sort == 'distance':
                    results_list.sort(key=lambda x: x.distance)
                
                queryset = results_list
            except (ValueError, TypeError):
                pass
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize data
        serializer = UserProfileSerializer(paginated_queryset, many=True)
        serialized_data = serializer.data
        
        # Add distance to serialized data if available
        if user_lat and user_lng:
            for i, item in enumerate(serialized_data):
                if hasattr(paginated_queryset[i], 'distance'):
                    item['distance_km'] = paginated_queryset[i].distance
        
        # Get paginated response
        response_data = paginator.get_paginated_response(serialized_data).data
        
        # Add search metadata
        response_data['search_metadata'] = {
            'query': query,
            'filters_applied': {
                'city': city if city else None,
                'state': state if state else None,
                'min_rating': min_rating,
                'is_verified': is_verified,
                'is_available': is_available,
                'location': {
                    'lat': lat,
                    'lng': lng,
                    'radius_km': radius
                } if lat and lng else None,
            },
            'sort': sort
        }
        
        # Calculate and log response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Add performance metadata to response
        response_data['performance'] = {
            'response_time_ms': round(response_time, 2),
            'cached': False,
            'target_met': response_time < 500
        }
        
        # Log slow queries for monitoring
        if response_time > 500:
            logger.warning(
                f"Slow professional search query: {response_time:.2f}ms - "
                f"q={query}, city={city}, state={state}, sort={sort}"
            )
        
        # Cache the result
        CacheManager.set(cache_key, response_data, timeout=CacheManager.TIMEOUT_SEARCH)
        
        return Response(response_data)
