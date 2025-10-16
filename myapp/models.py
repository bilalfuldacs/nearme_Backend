from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User as DjangoUser

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=555)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    # Required for Django REST Framework authentication
    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been authenticated.
        """
        return True
    
    @property
    def is_anonymous(self):
        """
        Always return False. This is a way to tell if the user is anonymous.
        """
        return False
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']


class Event(models.Model):
    """
    Event model to store event information
    """
    # Basic Information
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(help_text="Event description")
    max_attendees = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10000)],
        help_text="Maximum number of attendees"
    )
    
    # Date and Time Information
    start_date = models.DateField(help_text="Event start date")
    end_date = models.DateField(help_text="Event end date")
    start_time = models.TimeField(help_text="Event start time")
    end_time = models.TimeField(help_text="Event end time")
    
    # Location Information
    street = models.CharField(max_length=255, help_text="Street address")
    city = models.CharField(max_length=100, help_text="City")
    state = models.CharField(max_length=100, help_text="State/Province")
    postal_code = models.CharField(max_length=20, help_text="Postal/ZIP code")
    
    # Event Management
    organizer_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='organized_events',
        help_text="Event organizer user reference"
    )
    organizer_name = models.CharField(max_length=255, default='', blank=True, help_text="Organizer name (from User)")
    organizer_email = models.EmailField(default='', blank=True, help_text="Organizer email (from User)")
    confirmed_attendees = models.PositiveIntegerField(default=0, help_text="Number of confirmed attendees")
    is_active = models.BooleanField(default=True, help_text="Whether the event is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Computed Properties
    @property
    def full_address(self):
        """Return formatted full address"""
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}"
    
    @property
    def available_spots(self):
        """Calculate available spots"""
        return max(0, self.max_attendees - self.confirmed_attendees)
    
    @property
    def is_full(self):
        """Check if event is full"""
        return self.available_spots <= 0
    
    @property
    def is_upcoming(self):
        """Check if event is upcoming"""
        now = timezone.now().date()
        return self.start_date >= now
    
    @property
    def is_past(self):
        """Check if event is past"""
        now = timezone.now().date()
        return self.end_date < now
    
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['organizer_id']),  # Fixed: organizer → organizer_id
            models.Index(fields=['is_active']),
        ]


class EventImage(models.Model):
    """
    Model to store event images
    """
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='images',
        help_text="Associated event"
    )
    image = models.ImageField(
        upload_to='event_images/%Y/%m/%d/',
        help_text="Event image"
    )
    caption = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Image caption"
    )
    is_primary = models.BooleanField(
        default=False, 
        help_text="Whether this is the primary image"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event.title} - Image {self.id}"
    
    class Meta:
        db_table = 'event_images'
        verbose_name = 'Event Image'
        verbose_name_plural = 'Event Images'
        ordering = ['-is_primary', 'uploaded_at']


class Conversation(models.Model):
    """
    Represents one chat thread per event per user with request status
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="conversations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_conversations")
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="host_conversations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'user', 'host')  # Prevent duplicate conversations

    def __str__(self):
        return f"Conversation for {self.event.title} with {self.user.name}"


class Message(models.Model):
    """
    Stores actual text messages with read tracking
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read by recipient")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the message was read")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.name}: {self.text[:20]}"
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['is_read']),
        ]




