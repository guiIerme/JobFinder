# Geolocation and Maps Integration Documentation

## Overview
The Geolocation and Maps Integration feature allows users to find nearby professionals based on their current location. This feature enhances the user experience by providing a visual representation of service providers in their area.

## Features
- User location detection using browser geolocation
- Professional location storage in the database
- Distance calculation between users and professionals
- Interactive map display with markers
- Filtering by service category and distance
- Responsive design for all device sizes

## Database Models

### UserProfile Updates
The UserProfile model has been updated with geolocation fields:

```python
class UserProfile(models.Model):
    # ... existing fields ...
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
```

## API Endpoints

### Update User Location
```
POST /api/update-location/
```

Parameters:
- `latitude` (decimal): User's latitude coordinate
- `longitude` (decimal): User's longitude coordinate

Response:
```json
{
    "success": true,
    "message": "Location updated successfully"
}
```

### Get Nearby Professionals
```
GET /api/nearby-professionals/
```

Parameters:
- `category` (string, optional): Service category filter
- `max_distance` (float, optional): Maximum distance in kilometers (default: 50)

Response:
```json
{
    "success": true,
    "professionals": [
        {
            "id": 1,
            "username": "professional1",
            "name": "John Doe",
            "rating": 4.5,
            "review_count": 12,
            "latitude": -15.7801,
            "longitude": -47.9292,
            "distance": 5.2,
            "services": [
                {
                    "id": 1,
                    "name": "Plumbing Service",
                    "category": "Encanamento",
                    "price": 150.00
                }
            ]
        }
    ],
    "count": 1
}
```

## Views

### Map View
```
GET /map/
```

Displays the interactive map interface with nearby professionals.

## Templates

### Map View Template
Located at `templates/services/map_view.html`, this template provides:
- Interactive Google Maps integration
- Filtering options for service categories and distance
- List view of nearby professionals
- Responsive design for all device sizes

## Management Commands

### Initialize Geolocation
```
python manage.py initialize_geolocation
```

This command initializes geolocation fields for existing user profiles.

Options:
- `--dry-run`: Show what would be done without making changes

## Implementation Details

### Distance Calculation
Distances are calculated using the haversine formula, which accounts for the Earth's curvature:

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using haversine formula"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
```

### Map Integration
The feature uses Google Maps JavaScript API with:
- User location marker (green)
- Professional location markers (blue)
- Info windows with professional details
- Interactive filtering controls

### Security
- CSRF protection for location updates
- Input validation for coordinates
- Proper error handling for geolocation failures

## Testing
To test the geolocation feature:

1. Ensure you have a Google Maps API key
2. Update the API key in the base template
3. Create user profiles with latitude/longitude values
4. Access the map view at `/map/`

## Configuration

### Google Maps API Key
To use the map functionality, you need to:
1. Obtain a Google Maps API key from the Google Cloud Console
2. Enable the Maps JavaScript API
3. Update the API key in `templates/base.html`

## Future Enhancements
1. Route optimization between user and professional locations
2. Real-time location tracking for professionals
3. Heatmap visualization of service demand
4. Integration with Google Places for address autocomplete
5. Offline map support for mobile applications