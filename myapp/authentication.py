"""
Custom JWT Authentication for Custom User Model
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import User


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that uses our custom User model
    instead of Django's default auth.User
    """
    
    def get_user(self, validated_token):
        """
        Get user from our custom User model based on user_id in token
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token contained no recognizable user identification')
            
            # Get user from our custom User model
            user = User.objects.get(id=user_id)
            return user
            
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')



