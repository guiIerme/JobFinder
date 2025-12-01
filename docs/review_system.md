# Review System Documentation

## Overview
The Review System allows customers to rate and review services provided by professionals. This system helps build trust in the platform by providing transparent feedback mechanisms.

## Features
- Customers can rate professionals on a 1-5 star scale
- Customers can leave detailed comments about their experience
- Professional ratings are automatically calculated based on reviews
- Reviews are displayed on professional profiles
- Only completed orders can be reviewed

## Database Models

### Review Model
The Review model stores customer feedback for completed services:

```python
class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ])
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### UserProfile Updates
The UserProfile model has been updated with rating fields:

```python
class UserProfile(models.Model):
    # ... existing fields ...
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.IntegerField(default=0)
```

## API Endpoints

### Submit Review
```
POST /submit-review/<order_id>/
```

Parameters:
- `rating` (integer, 1-5): The star rating
- `comment` (string, optional): Review comment

Response:
```json
{
    "success": true,
    "message": "Review submitted successfully",
    "rating": 5,
    "comment": "Excellent service!",
    "created_at": "2025-10-16T10:30:00Z"
}
```

### Get Professional Reviews
```
GET /professional-reviews/<professional_id>/
```

Response:
```json
{
    "success": true,
    "reviews": [
        {
            "id": 1,
            "rating": 5,
            "comment": "Excellent service!",
            "created_at": "2025-10-16T10:30:00Z",
            "customer": {
                "username": "customer1",
                "first_name": "John",
                "last_name": "Doe"
            },
            "order": {
                "id": 100,
                "service_name": "Plumbing Service"
            }
        }
    ],
    "professional_rating": 4.5,
    "review_count": 12
}
```

## Templates

### Review Form Partial
Located at `templates/services/partials/review_form.html`, this partial can be included in any template to allow customers to submit reviews.

### Professional Profile
The professional profile page now displays reviews and ratings.

## Management Commands

### Initialize Reviews
```
python manage.py initialize_reviews
```

This command:
- Creates UserProfile entries for users who don't have them
- Initializes rating fields for existing profiles
- Calculates initial ratings for professionals

Options:
- `--dry-run`: Show what would be done without making changes

## Implementation Details

### Rating Calculation
Professional ratings are calculated using a weighted average formula:
```
new_rating = (current_rating * current_review_count + new_rating) / (current_review_count + 1)
```

### Review Verification
Reviews are automatically marked as verified (`is_verified = True`) in the current implementation. In a production environment, this could be enhanced with additional verification mechanisms.

### Security
- Only the order customer can submit a review
- Only completed orders can be reviewed
- CSRF protection is implemented for form submissions

## Testing
The review system includes comprehensive unit tests in `services/tests.py` that cover:
- Creating reviews for completed orders
- Updating professional ratings
- Preventing reviews for pending orders
- Correct rating calculations with multiple reviews

To run the tests:
```
python manage.py test services.tests.ReviewSystemTest
```

## Future Enhancements
1. Photo uploads with reviews
2. Response functionality for professionals
3. Review moderation system
4. Review filtering and sorting
5. Verified purchase badges
6. Review reporting and abuse prevention