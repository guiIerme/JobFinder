# Generated migration for search optimization indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0026_contactmessage'),
    ]

    operations = [
        # Add indexes for CustomService search fields
        migrations.AddIndex(
            model_name='customservice',
            index=models.Index(fields=['name'], name='services_cu_name_idx'),
        ),
        migrations.AddIndex(
            model_name='customservice',
            index=models.Index(fields=['category'], name='services_cu_category_idx'),
        ),
        migrations.AddIndex(
            model_name='customservice',
            index=models.Index(fields=['estimated_price'], name='services_cu_price_idx'),
        ),
        migrations.AddIndex(
            model_name='customservice',
            index=models.Index(fields=['is_active', '-created_at'], name='services_cu_active_created_idx'),
        ),
        migrations.AddIndex(
            model_name='customservice',
            index=models.Index(fields=['category', 'is_active'], name='services_cu_cat_active_idx'),
        ),
        
        # Add indexes for UserProfile search fields
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['user_type'], name='services_up_type_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['rating'], name='services_up_rating_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['city'], name='services_up_city_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['state'], name='services_up_state_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['is_verified'], name='services_up_verified_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['is_available'], name='services_up_available_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['latitude', 'longitude'], name='services_up_location_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['user_type', '-rating'], name='services_up_type_rating_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['user_type', 'is_available', '-rating'], name='services_up_type_avail_rating_idx'),
        ),
    ]
