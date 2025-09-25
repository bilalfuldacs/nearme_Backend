from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for EventViewSet
router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    # User endpoints
    path('create/', views.create_user, name='create_user'),
    path('login/', views.login_user, name='login_user'),
    
    # Conversation endpoints
    path('conversations/', views.create_conversation, name='create_conversation'),
    path('conversations/check/', views.check_conversation, name='check_conversation'),
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('conversations/user/<int:user_id>/', views.get_user_conversations, name='get_user_conversations'),
    path('conversations/user/<int:user_id>/confirmed-events/', views.get_user_confirmed_events, name='get_user_confirmed_events'),
    path('conversations/event/<int:event_id>/', views.get_event_conversations, name='get_event_conversations'),
    path('conversations/<int:conversation_id>/messages/', views.get_conversation_messages, name='get_conversation_messages'),
    
    # Message endpoints
    path('messages/', views.send_message, name='send_message'),
    
    # Conversation Status Update
    path('conversations/<int:conversation_id>/status/', views.update_conversation_status, name='update_conversation_status'),
    
    # Event endpoints
    path('', include(router.urls)),
] 
