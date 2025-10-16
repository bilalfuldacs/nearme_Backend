from django.contrib import admin
from .models import User, Event, EventImage, Conversation, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email']
    ordering = ['-created_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'organizer_name', 'organizer_email', 'start_date', 'end_date', 'city', 'state', 'is_active', 'created_at']
    list_filter = ['is_active', 'start_date', 'city', 'state', 'created_at']
    search_fields = ['title', 'description', 'city', 'state', 'organizer_name', 'organizer_email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'organizer_name', 'organizer_email']

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['event__title', 'caption']
    ordering = ['-uploaded_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'user', 'host', 'status', 'created_at', 'updated_at', 'confirmed_at', 'rejected_at']
    list_filter = ['status', 'created_at', 'event']
    search_fields = ['event__title', 'user__name', 'host__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'rejected_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'text_preview', 'created_at']
    list_filter = ['created_at', 'conversation__event']
    search_fields = ['text', 'sender__name', 'conversation__event__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Message Preview'
