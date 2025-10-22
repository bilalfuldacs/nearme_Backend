from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for EventViewSet
router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    # Category endpoints
    path('categories/', views.get_categories, name='get_categories'),
    
    # User endpoints
    path('create/', views.create_user, name='create_user'),
    path('profile/', views.get_my_profile, name='get_my_profile'),  # GET user profile
    path('profile/update/', views.update_my_profile, name='update_my_profile'),  # Update profile
    path('profile/change-password/', views.change_password, name='change_password'),  # Change password
    
    # JWT Token endpoints (email-based authentication)
    path('token/', views.login_user, name='token_obtain'),
    path('token/refresh/', views.refresh_token, name='token_refresh'),
    
    # Legacy login endpoint (for backward compatibility)
    path('login/', views.login_user, name='login_user'),
    
    # Conversation endpoints (Active - Used by Frontend)
    path('conversations/', views.create_conversation, name='create_conversation'),  # Create conversation & send messages
    path('conversations/my-conversations/', views.get_my_conversations, name='get_my_conversations'),  # Get user's inbox
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),  # Get conversation with messages
    path('conversations/event/<int:event_id>/my-conversation/', views.get_conversation_by_event, name='get_conversation_by_event'),  # Check my conversation for event
    path('conversations/event/<int:event_id>/', views.get_event_conversations, name='get_event_conversations'),  # Get event attendees (host only)
    path('conversations/<int:conversation_id>/status/', views.update_conversation_status, name='update_conversation_status'),  # Confirm/reject attendee
    
    # Message endpoints (Active - Used by Frontend)
    path('messages/mark-read/', views.mark_messages_as_read, name='mark_messages_as_read'),  # Mark messages as read
    
    # Review endpoints
    path('reviews/', views.create_review, name='create_review'),  # Create a review
    path('reviews/<int:review_id>/', views.update_review, name='update_review'),  # Update a review
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),  # Delete a review
    path('reviews/my-reviews/', views.get_my_reviews, name='get_my_reviews'),  # Get my reviews
    path('reviews/event/<int:event_id>/', views.get_event_reviews, name='get_event_reviews'),  # Get event reviews
    path('reviews/event/<int:event_id>/stats/', views.get_event_rating_stats, name='get_event_rating_stats'),  # Get event stats
    path('reviews/host/<int:host_id>/', views.get_host_reviews, name='get_host_reviews'),  # Get host reviews
    path('reviews/host/<int:host_id>/stats/', views.get_host_rating_stats, name='get_host_rating_stats'),  # Get host stats
    path('reviews/can-review/<int:event_id>/', views.check_can_review, name='check_can_review'),  # Check if user can review
    
    # Event endpoints
    path('', include(router.urls)),
] 
