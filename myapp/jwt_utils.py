"""
JWT Token utilities for custom User model
"""
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    Generate JWT tokens for our custom User model
    
    Args:
        user: Instance of myapp.models.User
    
    Returns:
        dict: Contains 'refresh' and 'access' tokens
    """
    refresh = RefreshToken()
    
    # Add custom claims
    refresh['user_id'] = str(user.id)  # Use our custom User's ID
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



