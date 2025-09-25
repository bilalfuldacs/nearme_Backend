from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from datetime import date
from .serializers import UserSerializer, LoginSerializer, EventSerializer, EventCreateSerializer, EventListSerializer, EventImageUploadSerializer, ConversationCreateSerializer, ConversationSerializer, MessageSerializer, ConversationStatusUpdateSerializer
from .models import User, Event, EventImage, Conversation, Message

@api_view(['POST'])
@csrf_exempt
def create_user(request):
    try:
        # Check if request has JSON data
        if not request.data:
            return Response({
                'success': False,
                'message': 'No data provided. Please send JSON data with Content-Type: application/json',
                'error': 'Missing request data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user_id': user.id,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        
        # Send structured error response
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred during user creation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login_user(request):
    """
    Login user endpoint
    POST /api/login/
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by email (no validation)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Return success response (no password validation)
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Handle unexpected errors
        return Response({
            'success': False,
            'message': 'An error occurred during login',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class EventViewSet(ModelViewSet):
    """
    ViewSet for Event CRUD operations with filtering and search capabilities
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['city', 'state', 'organizer', 'is_active', 'start_date']
    search_fields = ['title', 'description', 'city', 'state']
    ordering_fields = ['created_at', 'start_date', 'title', 'max_attendees']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return EventCreateSerializer
        elif self.action == 'list':
            return EventListSerializer
        return EventSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = Event.objects.select_related('organizer').prefetch_related('images')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filter by upcoming events
        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() == 'true':
            today = date.today()
            queryset = queryset.filter(start_date__gte=today)
        
        # Filter by past events
        past = self.request.query_params.get('past')
        if past and past.lower() == 'true':
            today = date.today()
            queryset = queryset.filter(end_date__lt=today)
        
        # Filter by active events only (default)
        active_only = self.request.query_params.get('active_only', 'true')
        if active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List events with enhanced filtering
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while fetching events',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new event
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                event = serializer.save()
                
                # Return full event details
                response_serializer = EventSerializer(event, context={'request': request})
                return Response({
                    'success': True,
                    'message': 'Event created successfully',
                    'event': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while creating the event',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific event
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'event': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while fetching the event',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """
        Update an event
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
            
            if serializer.is_valid():
                event = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Event updated successfully',
                    'event': EventSerializer(event, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while updating the event',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an event (soft delete by setting is_active=False)
        """
        try:
            instance = self.get_object()
            instance.is_active = False
            instance.save()
            
            return Response({
                'success': True,
                'message': 'Event deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while deleting the event',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming events
        """
        try:
            today = date.today()
            queryset = self.get_queryset().filter(start_date__gte=today)
            
            # Apply additional filters
            queryset = self.filter_queryset(queryset)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = EventListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = EventListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while fetching upcoming events',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def past(self, request):
        """
        Get past events
        """
        try:
            today = date.today()
            queryset = self.get_queryset().filter(end_date__lt=today)
            
            # Apply additional filters
            queryset = self.filter_queryset(queryset)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = EventListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = EventListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while fetching past events',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """
        Get events by location (city, state)
        """
        try:
            city = request.query_params.get('city')
            state = request.query_params.get('state')
            
            if not city and not state:
                return Response({
                    'success': False,
                    'message': 'Please provide city or state parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.get_queryset()
            
            if city:
                queryset = queryset.filter(city__icontains=city)
            if state:
                queryset = queryset.filter(state__icontains=state)
            
            # Apply additional filters
            queryset = self.filter_queryset(queryset)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = EventListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = EventListSerializer(queryset, many=True, context={'request': request})
            return Response({
                'success': True,
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while fetching events by location',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Toggle event active status
        """
        try:
            event = self.get_object()
            event.is_active = not event.is_active
            event.save()
            
            status_text = 'activated' if event.is_active else 'deactivated'
            return Response({
                'success': True,
                'message': f'Event {status_text} successfully',
                'is_active': event.is_active
            }, status=status.HTTP_200_OK)
            
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while updating event status',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """
        Upload images to an event
        """
        try:
            event = self.get_object()
            
            # Check if request has files
            if not request.FILES:
                return Response({
                    'success': False,
                    'message': 'No images provided. Please upload at least one image.',
                    'error': 'Missing image files'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract images from request.FILES
            images_data = []
            for key, file in request.FILES.items():
                if key.startswith('images') or key == 'image':
                    images_data.append(file)
            
            if not images_data:
                return Response({
                    'success': False,
                    'message': 'No valid image files found. Please upload images with proper field names.',
                    'error': 'Invalid file field names'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate images
            serializer = EventImageUploadSerializer(data={'images': images_data})
            if serializer.is_valid():
                # Save images
                uploaded_images = []
                for i, image in enumerate(serializer.validated_data['images']):
                    event_image = EventImage.objects.create(
                        event=event,
                        image=image,
                        is_primary=(i == 0)  # First image is primary
                    )
                    uploaded_images.append({
                        'id': event_image.id,
                        'image_url': request.build_absolute_uri(event_image.image.url),
                        'is_primary': event_image.is_primary,
                        'uploaded_at': event_image.uploaded_at
                    })
                
                return Response({
                    'success': True,
                    'message': f'Successfully uploaded {len(uploaded_images)} images',
                    'images': uploaded_images
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Image validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An error occurred while uploading images',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_conversation(request):
    """
    Check if conversation exists for user and event
    GET /api/conversations/check/?user_id=1&event_id=1
    """
    try:
        user_id = request.GET.get('user_id')
        event_id = request.GET.get('event_id')
        
        if not user_id or not event_id:
            return Response({
                'success': False,
                'message': 'Both user_id and event_id parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if conversation exists
        try:
            conversation = Conversation.objects.get(
                user_id=user_id,
                event_id=event_id
            )
            
            # Get the last message for additional info
            last_message = conversation.messages.last()
            last_message_text = last_message.text if last_message else None
            last_message_time = last_message.created_at if last_message else None
            
            return Response({
                'success': True,
                'exists': True,
                'conversation_id': conversation.id,
                'event_id': conversation.event.id,
                'user_id': conversation.user.id,
                'host_id': conversation.host.id,
                'created_at': conversation.created_at,
                'last_message': last_message_text,
                'last_message_time': last_message_time,
                'message_count': conversation.messages.count()
            }, status=status.HTTP_200_OK)
            
        except Conversation.DoesNotExist:
            return Response({
                'success': True,
                'exists': False,
                'conversation_id': None,
                'message': 'No conversation found for this user and event'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while checking conversation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def create_conversation(request):
    """
    Create a new conversation with initial message
    POST /api/conversations/
    Input: event_id, user_id, message
    """
    try:
        serializer = ConversationCreateSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Conversation created successfully',
                'conversation_id': conversation.id,
                'event_id': conversation.event.id,
                'user_id': conversation.user.id,
                'host_id': conversation.host.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while creating conversation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_conversation(request, conversation_id):
    """
    Get a specific conversation with all messages
    GET /api/conversations/{conversation_id}/
    """
    try:
        try:
            conversation = Conversation.objects.select_related('event', 'user', 'host').prefetch_related('messages__sender').get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize conversation with messages
        conversation_serializer = ConversationSerializer(conversation)
        messages_serializer = MessageSerializer(conversation.messages.all().order_by('created_at'), many=True)
        
        return Response({
            'success': True,
            'conversation': conversation_serializer.data,
            'messages': messages_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching conversation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_conversations(request, user_id):
    """
    Get all conversations for a specific user
    GET /api/conversations/user/{user_id}/
    """
    try:
        conversations = Conversation.objects.filter(
            Q(user_id=user_id) | Q(host_id=user_id)
        ).select_related('event', 'user', 'host').prefetch_related('messages').order_by('-updated_at')
        
        serializer = ConversationSerializer(conversations, many=True)
        
        return Response({
            'success': True,
            'count': conversations.count(),
            'conversations': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching user conversations',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_event_conversations(request, event_id):
    """
    Get all conversations for a specific event with event details and images
    GET /api/conversations/event/{event_id}/
    """
    try:
        # Get the event first to include event details
        try:
            event = Event.objects.prefetch_related('images').get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all conversations for this event
        conversations = Conversation.objects.filter(
            event_id=event_id
        ).select_related('event', 'user', 'host').prefetch_related('messages').order_by('-updated_at')
        
        # Get event images
        images = []
        for img in event.images.all():
            # Get full URL for the image
            image_url = None
            if img.image:
                # Build full URL
                from django.conf import settings
                image_url = f"{request.scheme}://{request.get_host()}{img.image.url}"
            
            images.append({
                'id': img.id,
                'image': image_url,
                'image_path': img.image.url if img.image else None,  # Keep relative path too
                'caption': img.caption,
                'is_primary': img.is_primary,
                'uploaded_at': img.uploaded_at
            })
        
        # Serialize conversations
        conversation_serializer = ConversationSerializer(conversations, many=True)
        
        # Prepare event details
        event_data = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'location': {
                'street': event.street,
                'city': event.city,
                'state': event.state,
                'postal_code': event.postal_code,
                'full_address': event.full_address
            },
            'max_attendees': event.max_attendees,
            'confirmed_attendees': event.confirmed_attendees,
            'available_spots': event.available_spots,
            'is_full': event.is_full,
            'is_active': event.is_active,
            'created_at': event.created_at,
            'updated_at': event.updated_at,
            'organizer': {
                'id': event.organizer.id,
                'name': event.organizer.name,
                'email': event.organizer.email
            },
            'images': images
        }
        
        return Response({
            'success': True,
            'count': conversations.count(),
            'event': event_data,
            'conversations': conversation_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching event conversations',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def send_message(request):
    """
    Send a message to an existing conversation
    POST /api/messages/
    Input: conversation_id, sender_id, text
    """
    try:
        conversation_id = request.data.get('conversation_id')
        sender_id = request.data.get('sender_id')
        text = request.data.get('text')
        
        if not all([conversation_id, sender_id, text]):
            return Response({
                'success': False,
                'message': 'conversation_id, sender_id, and text are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            sender = User.objects.get(id=sender_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Sender not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if sender is part of the conversation
        if sender not in [conversation.user, conversation.host]:
            return Response({
                'success': False,
                'message': 'You are not authorized to send messages to this conversation'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text
        )
        
        # Update conversation's updated_at field
        conversation.save()
        
        serializer = MessageSerializer(message)
        
        return Response({
            'success': True,
            'message': 'Message sent successfully',
            'message_data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while sending message',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_conversation_messages(request, conversation_id):
    """
    Get all messages for a specific conversation
    GET /api/conversations/{conversation_id}/messages/
    """
    try:
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        messages = conversation.messages.select_related('sender').order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            'success': True,
            'conversation_id': conversation_id,
            'count': messages.count(),
            'messages': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching messages',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user_confirmed_events(request, user_id):
    """
    Get all events where user has confirmed status with complete event details
    GET /api/conversations/user/{user_id}/confirmed-events/
    """
    try:
        # Get all conversations where user has confirmed status
        confirmed_conversations = Conversation.objects.filter(
            user_id=user_id,
            status='confirmed'
        ).select_related('event', 'host').prefetch_related('event__images').order_by('-confirmed_at')
        
        # Extract unique events from conversations
        events_data = []
        seen_events = set()
        
        for conversation in confirmed_conversations:
            if conversation.event.id not in seen_events:
                seen_events.add(conversation.event.id)
                event = conversation.event
                
                # Get all images for this event
                images = []
                for img in event.images.all():
                    # Get full URL for the image
                    image_url = None
                    if img.image:
                        # Build full URL
                        from django.conf import settings
                        image_url = f"{request.scheme}://{request.get_host()}{img.image.url}"
                    
                    images.append({
                        'id': img.id,
                        'image': image_url,
                        'image_path': img.image.url if img.image else None,  # Keep relative path too
                        'caption': img.caption,
                        'is_primary': img.is_primary,
                        'uploaded_at': img.uploaded_at
                    })
                
                # Get all participants for this event (all confirmed conversations)
                participants = []
                all_conversations = Conversation.objects.filter(
                    event=event,
                    status='confirmed'
                ).select_related('user')
                
                for conv in all_conversations:
                    participants.append({
                        'user_id': conv.user.id,
                        'user_name': conv.user.name,
                        'user_email': conv.user.email,
                        'confirmed_at': conv.confirmed_at,
                        'conversation_id': conv.id
                    })
                
                # Get all pending requests for this event
                pending_requests = []
                pending_conversations = Conversation.objects.filter(
                    event=event,
                    status='pending'
                ).select_related('user')
                
                for conv in pending_conversations:
                    pending_requests.append({
                        'user_id': conv.user.id,
                        'user_name': conv.user.name,
                        'user_email': conv.user.email,
                        'created_at': conv.created_at,
                        'conversation_id': conv.id
                    })
                
                events_data.append({
                    # Basic event info
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start_date': event.start_date,
                    'end_date': event.end_date,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'location': {
                        'street': event.street,
                        'city': event.city,
                        'state': event.state,
                        'postal_code': event.postal_code,
                        'full_address': event.full_address
                    },
                    'max_attendees': event.max_attendees,
                    'confirmed_attendees': event.confirmed_attendees,
                    'available_spots': event.available_spots,
                    'is_full': event.is_full,
                    'is_active': event.is_active,
                    'created_at': event.created_at,
                    'updated_at': event.updated_at,
                    
                    # Organizer info
                    'organizer': {
                        'id': event.organizer.id,
                        'name': event.organizer.name,
                        'email': event.organizer.email
                    },
                    
                    # Images
                    'images': images,
                    
                    # Participants
                    'participants': participants,
                    'participant_count': len(participants),
                    
                    # Pending requests
                    'pending_requests': pending_requests,
                    'pending_count': len(pending_requests),
                    
                    # User's confirmation info
                    'user_confirmation': {
                        'confirmed_at': conversation.confirmed_at,
                        'conversation_id': conversation.id
                    }
                })
        
        return Response({
            'success': True,
            'count': len(events_data),
            'user_id': user_id,
            'confirmed_events': events_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching confirmed events',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@csrf_exempt
def update_conversation_status(request, conversation_id):
    """
    Update conversation status (confirm/reject)
    PATCH /api/conversations/{conversation_id}/status/
    Input: status (confirmed/rejected)
    """
    try:
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ConversationStatusUpdateSerializer(conversation, data=request.data, partial=True)
        if serializer.is_valid():
            updated_conversation = serializer.save()
            
            return Response({
                'success': True,
                'message': f'Conversation {updated_conversation.status} successfully',
                'conversation': ConversationSerializer(updated_conversation).data,
                'event': {
                    'id': updated_conversation.event.id,
                    'title': updated_conversation.event.title,
                    'confirmed_attendees': updated_conversation.event.confirmed_attendees,
                    'available_spots': updated_conversation.event.available_spots,
                    'is_full': updated_conversation.event.is_full
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while updating conversation status',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    