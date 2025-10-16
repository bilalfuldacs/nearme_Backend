from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from datetime import date
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer, EventSerializer, EventCreateSerializer, EventListSerializer, EventImageUploadSerializer, ConversationCreateSerializer, ConversationSerializer, MessageSerializer, ConversationStatusUpdateSerializer, CategorySerializer
from .models import User, Event, EventImage, Conversation, Message, Category
from .jwt_utils import get_tokens_for_user

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow signup without authentication
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
        
        # Hash the password before saving
        data = request.data.copy()
        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens for the new user (custom User model)
            tokens = get_tokens_for_user(user)
            
            return Response({
                'success': True,
                'message': 'User created successfully',
                'user_id': user.id,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                },
                'tokens': tokens
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
@permission_classes([AllowAny])  # Allow login without authentication
def login_user(request):
    """
    Custom JWT Token endpoint for email-based login
    POST /api/token/
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Response:
    {
        "success": true,
        "message": "Login successful",
        "user": {...},
        "tokens": {
            "refresh": "refresh_token_here",
            "access": "access_token_here"
        }
    }
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({
                'success': False,
                'message': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # VALIDATE PASSWORD - Check if password matches (with hashing support)
        if not check_password(password, user.password):
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens for custom User model
        tokens = get_tokens_for_user(user)
        
        # Return success response with tokens
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            },
            'tokens': tokens
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        # Handle unexpected errors
        return Response({
            'success': False,
            'message': 'An error occurred during login',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow token refresh without authentication
def refresh_token(request):
    """
    Refresh JWT Token endpoint
    POST /api/token/refresh/
    
    Request body:
    {
        "refresh": "refresh_token_here"
    }
    
    Response:
    {
        "success": true,
        "access": "new_access_token_here"
    }
    """
    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate and refresh the token
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'success': True,
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except Exception as token_error:
            return Response({
                'success': False,
                'message': 'Invalid or expired refresh token',
                'error': str(token_error)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred during token refresh',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require authentication
def get_my_profile(request):
    """
    Get current user's profile
    GET /api/profile/
    
    Returns profile of the authenticated user
    Authentication required: Yes
    """
    try:
        user = request.user
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching profile',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])  # Require authentication
@csrf_exempt
def update_my_profile(request):
    """
    Update current user's profile
    PUT/PATCH /api/profile/
    
    Request body (all fields optional for PATCH):
    {
        "name": "New Name",
        "email": "newemail@example.com"
    }
    
    Note: Cannot change password here, use change-password endpoint
    Authentication required: Yes
    """
    try:
        user = request.user
        
        # Get data
        name = request.data.get('name')
        email = request.data.get('email')
        
        # Update name if provided
        if name:
            user.name = name
        
        # Update email if provided and not already taken
        if email and email != user.email:
            # Check if email already exists
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response({
                    'success': False,
                    'message': 'Email already in use by another account'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = email
        
        user.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_at': user.created_at
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while updating profile',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication
@csrf_exempt
def change_password(request):
    """
    Change user's password
    POST /api/profile/change-password/
    
    Request body:
    {
        "current_password": "oldpass123",
        "new_password": "newpass123"
    }
    
    Authentication required: Yes
    """
    try:
        user = request.user
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'success': False,
                'message': 'Both current_password and new_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not check_password(current_password, user.password):
            return Response({
                'success': False,
                'message': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password
        if len(new_password) < 6:
            return Response({
                'success': False,
                'message': 'New password must be at least 6 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        user.password = make_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while changing password',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])  # Public endpoint - no auth required
def get_categories(request):
    """
    Get all event categories
    GET /api/categories/
    
    Returns all predefined categories available for events
    Authentication required: No
    """
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        
        return Response({
            'success': True,
            'count': categories.count(),
            'categories': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching categories',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EventViewSet(ModelViewSet):
    """
    ViewSet for Event CRUD operations with filtering and search capabilities
    
    Permissions:
    - List/Retrieve: Anyone (no auth required)
    - Create/Update/Delete: Authenticated users only
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['city', 'state', 'category', 'organizer_id', 'is_active']  # start_date and end_date handled in get_queryset()
    search_fields = ['title', 'description', 'city', 'state', 'category__name']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'title', 'max_attendees']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Set permissions based on action
        All event operations require authentication
        """
        from rest_framework.permissions import IsAuthenticated
        
        # All operations require authentication
        permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateSerializer
        elif self.action == 'list':
            return EventListSerializer
        return EventSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = Event.objects.select_related('organizer_id').prefetch_related('images')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            # Both dates provided: Get events starting BETWEEN these dates
            queryset = queryset.filter(
                start_date__gte=start_date,
                start_date__lte=end_date
            )
        elif start_date:
            # Only start_date: Get events starting on or AFTER this date
            queryset = queryset.filter(start_date__gte=start_date)
        elif end_date:
            # Only end_date: Get events ending on or BEFORE this date
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
    
    # REMOVED: destroy() method - Not used by frontend
    # DELETE /api/events/{id}/ endpoint removed as per frontend documentation
    # If needed in future, soft delete can be implemented via toggle_active or is_active field
    
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
    
    # REMOVED: toggle_active() action - Not used by frontend
    # POST /api/events/{id}/toggle_active/ endpoint removed as per frontend documentation
    # If needed in future, can be re-implemented or use PATCH /api/events/{id}/ to update is_active field
    
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


# REMOVED: check_conversation() - Replaced by get_conversation_by_event()
# GET /api/conversations/check/ endpoint removed - use GET /api/conversations/event/{event_id}/my-conversation/ instead


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication
@csrf_exempt
def create_conversation(request):
    """
    Create a new conversation or add message to existing conversation
    POST /api/conversations/
    Input: event_id, message
    
    Behavior:
    - If conversation doesn't exist: Creates conversation + adds message
    - If conversation already exists: Adds message to existing conversation
    - Works for both attendee (user) and host sending messages
    
    Note: user_id is extracted from authenticated user (JWT token)
    Authentication required: Yes
    """
    try:
        # Get user from authenticated request
        authenticated_user = request.user
        
        # Get data from request
        event_id = request.data.get('event_id')
        message_text = request.data.get('message')
        
        if not event_id or not message_text:
            return Response({
                'success': False,
                'message': 'event_id and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the event
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if conversation already exists where authenticated user is participant
        # User can be either the attendee (user) OR the organizer (host)
        conversation = None
        conversation_exists = False
        
        try:
            # Try to find conversation where user is either the attendee or the host
            conversation = Conversation.objects.get(
                Q(event_id=event_id, user=authenticated_user) |
                Q(event_id=event_id, host=authenticated_user)
            )
            conversation_exists = True
            
            # Add message to existing conversation
            Message.objects.create(
                conversation=conversation,
                sender=authenticated_user,
                text=message_text
            )
            
        except Conversation.DoesNotExist:
            # No existing conversation - create new one
            # The authenticated user is requesting to join the event (they are the attendee)
            conversation, created = Conversation.objects.get_or_create(
                event=event,
                user=authenticated_user,
                host=event.organizer_id,
                defaults={}
            )
            
            # Add the initial message
            Message.objects.create(
                conversation=conversation,
                sender=authenticated_user,
                text=message_text
            )
            conversation_exists = False
        
        # Get the latest message count
        message_count = conversation.messages.count()
        
        return Response({
            'success': True,
            'message': 'Message sent successfully' if conversation_exists else 'Conversation created successfully',
            'conversation_id': conversation.id,
            'event_id': conversation.event.id,
            'user_id': conversation.user.id,
            'host_id': conversation.host.id,
            'message_count': message_count,
            'is_new_conversation': not conversation_exists
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while processing your request',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require authentication
def get_conversation(request, conversation_id):
    """
    Get a specific conversation with all messages (Authenticated)
    GET /api/conversations/{conversation_id}/
    
    Returns complete conversation details with:
    - Event information
    - User (attendee) details
    - Host (organizer) details  
    - All messages with sender information
    
    Authentication required: Yes
    """
    try:
        try:
            conversation = Conversation.objects.select_related('event', 'user', 'host').prefetch_related('messages__sender').get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize messages with full sender details
        messages_serializer = MessageSerializer(conversation.messages.all().order_by('created_at'), many=True)
        
        # Build comprehensive response
        return Response({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'status': conversation.status,
                'created_at': conversation.created_at,
                'updated_at': conversation.updated_at,
                'confirmed_at': conversation.confirmed_at,
                'rejected_at': conversation.rejected_at,
                'event': {
                    'id': conversation.event.id,
                    'title': conversation.event.title,
                    'description': conversation.event.description,
                    'start_date': conversation.event.start_date,
                    'end_date': conversation.event.end_date,
                    'start_time': conversation.event.start_time,
                    'end_time': conversation.event.end_time,
                    'city': conversation.event.city,
                    'state': conversation.event.state,
                    'max_attendees': conversation.event.max_attendees,
                    'confirmed_attendees': conversation.event.confirmed_attendees,
                    'is_full': conversation.event.is_full
                },
                'user': {
                    'id': conversation.user.id,
                    'name': conversation.user.name,
                    'email': conversation.user.email
                },
                'host': {
                    'id': conversation.host.id,
                    'name': conversation.host.name,
                    'email': conversation.host.email
                },
                'message_count': conversation.messages.count()
            },
            'messages': messages_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching conversation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require authentication
def get_conversation_by_event(request, event_id):
    """
    Get conversation for authenticated user and specific event
    GET /api/conversations/event/{event_id}/my-conversation/
    
    Uses:
    - event_id from URL parameter
    - user_id from JWT token (authenticated user)
    
    Returns complete conversation with all messages if exists,
    or 404 if no conversation found.
    
    Authentication required: Yes
    """
    try:
        # Get authenticated user from JWT token
        authenticated_user = request.user
        
        # Find conversation for this user and event
        try:
            conversation = Conversation.objects.select_related(
                'event', 'user', 'host'
            ).prefetch_related(
                'messages__sender'
            ).get(
                event_id=event_id,
                user=authenticated_user
            )
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'exists': False,
                'message': 'No conversation found for this event'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize messages with full sender details
        messages_serializer = MessageSerializer(
            conversation.messages.all().order_by('created_at'), 
            many=True
        )
        
        # Build comprehensive response
        return Response({
            'success': True,
            'exists': True,
            'conversation': {
                'id': conversation.id,
                'status': conversation.status,
                'created_at': conversation.created_at,
                'updated_at': conversation.updated_at,
                'confirmed_at': conversation.confirmed_at,
                'rejected_at': conversation.rejected_at,
                'event': {
                    'id': conversation.event.id,
                    'title': conversation.event.title,
                    'description': conversation.event.description,
                    'start_date': conversation.event.start_date,
                    'end_date': conversation.event.end_date,
                    'start_time': conversation.event.start_time,
                    'end_time': conversation.event.end_time,
                    'city': conversation.event.city,
                    'state': conversation.event.state,
                    'max_attendees': conversation.event.max_attendees,
                    'confirmed_attendees': conversation.event.confirmed_attendees,
                    'is_full': conversation.event.is_full
                },
                'user': {
                    'id': conversation.user.id,
                    'name': conversation.user.name,
                    'email': conversation.user.email
                },
                'host': {
                    'id': conversation.host.id,
                    'name': conversation.host.name,
                    'email': conversation.host.email
                },
                'message_count': conversation.messages.count()
            },
            'messages': messages_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching conversation',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require authentication
def get_my_conversations(request):
    """
    Get all conversations for authenticated user
    GET /api/conversations/my-conversations/
    
    Returns all conversations where user is either:
    - The attendee (user) requesting to join events
    - The host (organizer) receiving requests
    
    Each conversation includes:
    - Event details
    - Other participant info
    - Last message preview
    - Message count
    - Conversation status
    
    Authentication required: Yes
    """
    try:
        # Get authenticated user from JWT token
        authenticated_user = request.user
        
        # Get all conversations where user is participant (as user or host)
        conversations = Conversation.objects.filter(
            Q(user=authenticated_user) | Q(host=authenticated_user)
        ).select_related('event', 'user', 'host').prefetch_related('messages')
        
        # Build enhanced response with sorting by latest message
        conversations_data = []
        for conversation in conversations:
            # Determine the "other person" in the conversation
            if conversation.user == authenticated_user:
                # Current user is the attendee
                other_person = conversation.host
                my_role = 'attendee'
            else:
                # Current user is the host/organizer
                other_person = conversation.user
                my_role = 'host'
            
            # Get last message
            last_message = conversation.messages.last()
            
            # Count unread messages (messages from other person that current user hasn't read)
            unread_count = conversation.messages.filter(
                is_read=False
            ).exclude(sender=authenticated_user).count()
            
            conversations_data.append({
                'conversation_id': conversation.id,
                'status': conversation.status,
                'created_at': conversation.created_at,
                'updated_at': conversation.updated_at,
                'my_role': my_role,
                'event': {
                    'id': conversation.event.id,
                    'title': conversation.event.title,
                    'start_date': conversation.event.start_date,
                    'end_date': conversation.event.end_date,
                    'city': conversation.event.city,
                    'state': conversation.event.state
                },
                'other_person': {
                    'id': other_person.id,
                    'name': other_person.name,
                    'email': other_person.email
                },
                'last_message': {
                    'id': last_message.id,
                    'text': last_message.text,
                    'sender_name': last_message.sender.name,
                    'sender_id': last_message.sender.id,
                    'created_at': last_message.created_at,
                    'is_read': last_message.is_read
                } if last_message else None,
                'message_count': conversation.messages.count(),
                'unread_count': unread_count,
                # Add timestamp for sorting
                'last_message_time': last_message.created_at if last_message else conversation.created_at
            })
        
        # Sort by last message time (most recent first)
        conversations_data.sort(key=lambda x: x['last_message_time'], reverse=True)
        
        # Remove the sorting field from response
        for conv in conversations_data:
            del conv['last_message_time']
        
        return Response({
            'success': True,
            'count': len(conversations_data),
            'conversations': conversations_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching conversations',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# REMOVED: get_user_conversations() - Legacy endpoint, replaced by get_my_conversations()
# GET /api/conversations/user/{user_id}/ endpoint removed - use GET /api/conversations/my-conversations/ instead


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require authentication
def get_event_conversations(request, event_id):
    """
    Get all conversations for a specific event with event details and images
    GET /api/conversations/event/{event_id}/
    
    Note: Only the event organizer (host) can view this list
    Authentication required: Yes
    """
    try:
        # Get authenticated user
        authenticated_user = request.user
        
        # Get the event first to include event details
        try:
            event = Event.objects.prefetch_related('images').get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify that the authenticated user is the event organizer (host)
        if event.organizer_id != authenticated_user:
            return Response({
                'success': False,
                'message': 'Only the event organizer can view the list of attendees'
            }, status=status.HTTP_403_FORBIDDEN)
        
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
        
        # Build enhanced conversations list for host
        conversations_data = []
        for conv in conversations:
            # Get last message
            last_message = conv.messages.last()
            
            conversations_data.append({
                'conversation_id': conv.id,
                'user_id': conv.user.id,
                'user_name': conv.user.name,
                'user_email': conv.user.email,
                'status': conv.status,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at,
                'confirmed_at': conv.confirmed_at,
                'rejected_at': conv.rejected_at,
                'last_message': {
                    'id': last_message.id,
                    'text': last_message.text,
                    'sender_name': last_message.sender.name,
                    'sender_id': last_message.sender.id,
                    'created_at': last_message.created_at
                } if last_message else None,
                'message_count': conv.messages.count()
            })
        
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
                'id': event.organizer_id.id,
                'name': event.organizer_id.name,
                'email': event.organizer_id.email
            },
            'images': images
        }
        
        return Response({
            'success': True,
            'count': len(conversations_data),
            'event': event_data,
            'conversations': conversations_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while fetching event conversations',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# REMOVED: send_message() - Replaced by create_conversation()
# POST /api/messages/ endpoint removed - use POST /api/conversations/ instead (handles both new and existing conversations)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication
@csrf_exempt
def mark_messages_as_read(request):
    """
    Mark messages as read for a conversation
    POST /api/messages/mark-read/
    Input: conversation_id
    
    Marks all unread messages from the other person as read
    Authentication required: Yes
    """
    try:
        # Get authenticated user
        authenticated_user = request.user
        
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response({
                'success': False,
                'message': 'conversation_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get conversation
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is part of the conversation
        if authenticated_user not in [conversation.user, conversation.host]:
            return Response({
                'success': False,
                'message': 'You are not authorized to access this conversation'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Mark all unread messages from the OTHER person as read
        # (Don't mark own messages as read)
        from django.utils import timezone
        
        unread_messages = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=authenticated_user)
        
        # Get count before updating
        unread_count = unread_messages.count()
        
        # Update all unread messages
        unread_messages.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': f'{unread_count} messages marked as read',
            'marked_count': unread_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'An error occurred while marking messages as read',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# REMOVED: get_conversation_messages() - Redundant, messages already included in get_conversation()
# GET /api/conversations/{conversation_id}/messages/ endpoint removed - use GET /api/conversations/{conversation_id}/ instead


# REMOVED: get_user_confirmed_events() - Not used by frontend
# GET /api/conversations/user/{user_id}/confirmed-events/ endpoint removed
# Frontend filters confirmed events from GET /api/conversations/my-conversations/ with status='confirmed'


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # Require authentication
@csrf_exempt
def update_conversation_status(request, conversation_id):
    """
    Update conversation status (confirm/reject)
    PATCH /api/conversations/{conversation_id}/status/
    Input: status (confirmed/rejected)
    
    Note: Only the host (event organizer) can update conversation status
    Authentication required: Yes
    """
    try:
        # Get authenticated user
        authenticated_user = request.user
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify user is the host (event organizer) who can update status
        if authenticated_user != conversation.host:
            return Response({
                'success': False,
                'message': 'Only the event organizer can update conversation status'
            }, status=status.HTTP_403_FORBIDDEN)
        
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


    