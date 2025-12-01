from django.urls import path
from . import views

urlpatterns = [
    path('track-page-view/', views.track_page_view, name='track_page_view'),
    path('track-user-action/', views.track_user_action, name='track_user_action'),
]