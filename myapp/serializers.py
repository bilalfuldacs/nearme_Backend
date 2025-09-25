from rest_framework import serializers
from .models import User, Event, EventImage, Conversation, Message
import re
from datetime import datetime, date, time
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'password']
        extra_kwargs = {
            'name': {
                'max_length': 555,
                'error_messages': {
                    'blank': 'Name is required.',
                    'max_length': 'Name cannot be longer than 155 characters.'
                }
            },
            'email': {
                'error_messages': {
                    'blank': 'Email is required.',
                    'invalid': 'Please enter a valid email address.'
                }
            },
            'password': {
                'error_messages': {
                    'blank': 'Password is required.',
                    'max_length': 'Password cannot be longer than 055 characters.'
                }
            }
        }
    
    def validate_name(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_email(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_password(self, value):
        """Validation disabled for now"""
        return value

    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate_email(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_password(self, value):
        """Validation disabled for now"""
        return value

    
    def validate(self, attrs):
        """Validation disabled for now"""
        return attrs


class EventImageSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for EventImage model with absolute URLs
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_image_url(self, obj):
        """Get absolute URL for the image"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
    
    def validate_image(self, value):
        """Validation disabled for now"""
        return value
    

class EventSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Event model with enhanced image handling
    """
    images = EventImageSerializer(many=True, read_only=True)
    organizer_name = serializers.CharField(source='username', read_only=True)
    organizer_email = serializers.EmailField(required=False)
    full_address = serializers.CharField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'max_attendees',
            'start_date', 'end_date', 'start_time', 'end_time',
            'street', 'city', 'state', 'postal_code',
            'organizer', 'organizer_name', 'organizer_email',
            'is_active', 'created_at', 'updated_at',
            'images', 'primary_image', 'image_count',
            'full_address', 'is_upcoming', 'is_past'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_primary_image(self, obj):
        """Get primary image URL"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_image_count(self, obj):
        """Get total number of images"""
        return obj.images.count()



class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for event creation with base64 image support
    """
    images = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of base64 encoded images"
    )
    organizer_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'max_attendees',
            'start_date', 'end_date', 'start_time', 'end_time',
            'street', 'city', 'state', 'postal_code', 'organizer',
            'username', 'email', 'organizer_email', 'organizer_name', 'images'
        ]
    
    def validate_start_time(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_end_time(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_username(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_email(self, value):
        """Validation disabled for now"""
        return value

    
    def validate_organizer_email(self, value):
        """Validation disabled for now"""
        return value

    
    def create(self, validated_data):
        """Create event with base64 images"""
        import base64
        import io
        from django.core.files.base import ContentFile
        from PIL import Image
        
        images_data = validated_data.pop('images', [])
        organizer_name = validated_data.pop('organizer_name', None)
        organizer_email = validated_data.get('organizer_email', '')
        
        # Map organizer_name to username if provided
        if organizer_name:
            validated_data['username'] = organizer_name
        
        # Find or create organizer user based on organizer_email
        if organizer_email:
            try:
                organizer_user = User.objects.get(email=organizer_email)
            except User.DoesNotExist:
                # Create new user if organizer doesn't exist
                organizer_user = User.objects.create(
                    name=organizer_name or 'Event Organizer',
                    email=organizer_email,
                    password='default_password'  # You might want to handle this differently
                )
            validated_data['organizer'] = organizer_user
        
        event = Event.objects.create(**validated_data)
        
        # Handle base64 image uploads
        for i, base64_string in enumerate(images_data):
            try:
                # Remove data URL prefix if present
                if ',' in base64_string:
                    header, data = base64_string.split(',', 1)
                else:
                    data = base64_string
                
                # Decode base64 data
                image_data = base64.b64decode(data)
                
                # Create a ContentFile from the decoded data
                image_file = ContentFile(image_data, name=f'image_{i+1}.png')
                
                # Create EventImage instance
                EventImage.objects.create(
                    event=event,
                    image=image_file,
                    is_primary=(i == 0)  # First image is primary
                )
                
            except Exception as e:
                # Log the error but don't fail the entire event creation
                print(f"Error processing image {i+1}: {str(e)}")
                continue
        
        return event


class EventImageUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading multiple images to an event
    """
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        allow_empty=False,
        max_length=10,
        help_text="List of images (max 10)"
    )
    
    def validate_images(self, value):
        """Validation disabled for now"""
        return value


class EventListSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for event listing with comprehensive image handling
    """
    organizer_name = serializers.CharField(source='username', read_only=True)
    organizer_email = serializers.EmailField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    all_images = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    full_address = serializers.CharField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'max_attendees',
            'start_date', 'end_date', 'start_time', 'end_time',
            'city', 'state', 'organizer_name', 'organizer_email',
            'is_active', 'created_at', 
            'primary_image', 'all_images', 'image_count', 
            'full_address', 'is_upcoming', 'is_past'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image URL"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_all_images(self, obj):
        """Get all images with details"""
        images = obj.images.all()
        request = self.context.get('request')
        
        image_list = []
        for image in images:
            image_data = {
                'id': image.id,
                'url': request.build_absolute_uri(image.image.url) if request else image.image.url,
                'caption': image.caption,
                'is_primary': image.is_primary,
                'uploaded_at': image.uploaded_at
            }
            image_list.append(image_data)
        
        return image_list
    
    def get_image_count(self, obj):
        """Get total number of images"""
        return obj.images.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating conversations with initial message
    POST /api/conversations/
    Frontend sends: event_id, user_id, message
    Backend auto-fetches: host_id from event.organizer
    """
    event_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    message = serializers.CharField(write_only=True)
    
    class Meta:
        model = Conversation
        fields = ['event_id', 'user_id', 'message']
    
    def create(self, validated_data):
        """Create conversation and initial message"""
        event_id = validated_data.pop('event_id')
        user_id = validated_data.pop('user_id')
        message_text = validated_data.pop('message')
        
        # Get objects
        event = Event.objects.get(id=event_id)
        user = User.objects.get(id=user_id)
        
        # Get host from event.organizer (this should now be the correct user)
        host = event.organizer
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            event=event,
            user=user,
            host=host,
            defaults={}
        )
        
        # Create initial message if conversation is new
        if created:
            Message.objects.create(
                conversation=conversation,
                sender=user,
                text=message_text
            )
        
        return conversation


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with related data
    """
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    host_name = serializers.CharField(source='host.name', read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'event', 'event_title', 'user', 'user_name', 
            'host', 'host_name', 'status', 'created_at', 'updated_at',
            'confirmed_at', 'rejected_at', 'last_message', 'message_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'confirmed_at', 'rejected_at']
    
    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': last_msg.id,
                'text': last_msg.text,
                'sender_name': last_msg.sender.name,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_message_count(self, obj):
        """Get total number of messages in the conversation"""
        return obj.messages.count()


class ConversationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating conversation status
    """
    class Meta:
        model = Conversation
        fields = ['status']
    
    def update(self, instance, validated_data):
        """Update conversation status and handle event capacity"""
        from django.utils import timezone
        
        new_status = validated_data.get('status')
        old_status = instance.status
        
        # Update the conversation
        instance = super().update(instance, validated_data)
        
        # Handle capacity changes
        if new_status == 'confirmed' and old_status != 'confirmed':
            # Increment confirmed attendees
            instance.event.confirmed_attendees += 1
            instance.event.save()
            instance.confirmed_at = timezone.now()
            instance.save()
            
        elif old_status == 'confirmed' and new_status != 'confirmed':
            # Decrement confirmed attendees
            instance.event.confirmed_attendees = max(0, instance.event.confirmed_attendees - 1)
            instance.event.save()
            
        if new_status == 'rejected':
            instance.rejected_at = timezone.now()
            instance.save()
        
        return instance


    
    