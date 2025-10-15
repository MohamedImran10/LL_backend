import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_jwt_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow(),
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token

def decode_jwt_token(token):
    """Decode JWT token and return user"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user = User.objects.get(id=payload['user_id'])
        return user
    except jwt.ExpiredSignatureError:
        return None
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None

def get_user_from_token(request):
    """Extract user from Authorization header"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return decode_jwt_token(token)
