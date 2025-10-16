from rest_framework import serializers
from .models import User, Event, EventImage, Conversation, Message, Category
import re
from datetime import datetime, date, time
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model (read-only)
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon']
        read_only_fields = ['id', 'name', 'description', 'icon']


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
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate_email(self, value):
        """Validate email is provided"""
        if not value:
            raise serializers.ValidationError("Email is required")
        return value

    
    def validate_password(self, value):
        """Validate password is provided"""
        if not value:
            raise serializers.ValidationError("Password is required")
        return value

    
    def validate(self, attrs):
        """Validate user credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")
        
        # Check if password matches
        if user.password != password:
            raise serializers.ValidationError("Invalid email or password")
        
        attrs['user'] = user
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
    category_details = CategorySerializer(source='category', read_only=True)
    organizer_name = serializers.CharField(read_only=True)
    organizer_email = serializers.EmailField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'category_details', 
            'max_attendees', 'confirmed_attendees', 'available_spots', 'is_full',
            'start_date', 'end_date', 'start_time', 'end_time',
            'street', 'city', 'state', 'postal_code',
            'organizer_id', 'organizer_name', 'organizer_email',
            'is_active', 'created_at', 'updated_at',
            'images', 'primary_image', 'image_count',
            'full_address', 'is_upcoming', 'is_past'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'organizer_name', 'organizer_email', 'confirmed_attendees', 'available_spots', 'is_full']
    
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
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'max_attendees',
            'start_date', 'end_date', 'start_time', 'end_time',
            'street', 'city', 'state', 'postal_code', 
            'organizer_id', 'images'
        ]
    
    def create(self, validated_data):
        """Create event with base64 images"""
        import base64
        import io
        from django.core.files.base import ContentFile
        from PIL import Image
        
        images_data = validated_data.pop('images', [])
        
        # Get organizer info from the User and populate event fields
        if 'organizer_id' in validated_data:
            organizer = validated_data['organizer_id']
            validated_data['organizer_name'] = organizer.name
            validated_data['organizer_email'] = organizer.email
        
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
    
    def update(self, instance, validated_data):
        """Update event with base64 images"""
        import base64
        import io
        from django.core.files.base import ContentFile
        from PIL import Image
        
        # Check if images field was provided in the original request data
        # Use initial_data because validated_data might not include empty arrays
        images_provided = 'images' in self.initial_data
        images_data = validated_data.pop('images', None)
        
        # If images_data is None but images were provided, get from initial_data
        if images_provided and images_data is None:
            images_data = self.initial_data.get('images', [])
        
        # Debug logging
        print(f"DEBUG: images_provided = {images_provided}")
        print(f"DEBUG: images_data = {images_data}")
        print(f"DEBUG: initial_data keys = {self.initial_data.keys()}")
        print(f"DEBUG: Type of images_data = {type(images_data)}")
        
        # Update organizer info if organizer_id changed
        if 'organizer_id' in validated_data:
            organizer = validated_data['organizer_id']
            validated_data['organizer_name'] = organizer.name
            validated_data['organizer_email'] = organizer.email
        
        # Update event fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle image updates only if images field was explicitly provided
        if images_provided:
            # Delete all existing images first
            instance.images.all().delete()
            
            # Add new images if any were provided
            if images_data:
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
                            event=instance,
                            image=image_file,
                            is_primary=(i == 0)  # First image is primary
                        )
                        
                    except Exception as e:
                        # Log the error but don't fail the entire event update
                        print(f"Error processing image {i+1}: {str(e)}")
                        continue
        
        return instance


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
    category_details = CategorySerializer(source='category', read_only=True)
    organizer_name = serializers.CharField(read_only=True)
    organizer_email = serializers.EmailField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    all_images = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    full_address = serializers.CharField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'category_details',
            'max_attendees', 'confirmed_attendees', 'available_spots', 'is_full',
            'start_date', 'end_date', 'start_time', 'end_time',
            'city', 'state', 'organizer_id', 'organizer_name', 'organizer_email',
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
        """Create conversation and add message (works for new and existing conversations)"""
        event_id = validated_data.pop('event_id')
        user_id = validated_data.pop('user_id')
        message_text = validated_data.pop('message')
        
        # Get objects
        event = Event.objects.get(id=event_id)
        user = User.objects.get(id=user_id)
        
        # Get host from event.organizer_id (the field name in Event model)
        host = event.organizer_id
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(
            event=event,
            user=user,
            host=host,
            defaults={}
        )
        
        # Always create the message (whether conversation is new or existing)
        Message.objects.create(
            conversation=conversation,
            sender=user,
            text=message_text
        )
        
        return conversation


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with full sender details and read status
    """
    sender = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'text', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_sender(self, obj):
        """Get full sender details"""
        return {
            'id': obj.sender.id,
            'name': obj.sender.name,
            'email': obj.sender.email
        }


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


    
    