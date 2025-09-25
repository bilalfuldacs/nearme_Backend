from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, UserListSerializer
from .models import User

@api_view(['POST'])
def user_registration(request):
    """
    Register a new user
    """
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response({
                'message': 'User registered successfully!',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'created_at': user.created_at
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'Failed to create user',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_users(request):
    """
    Get all users (for testing purposes)
    """
    users = User.objects.all().order_by('-created_at')
    serializer = UserListSerializer(users, many=True)
    return Response({
        'users': serializer.data,
        'count': len(serializer.data)
    }) 