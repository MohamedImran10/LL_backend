from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .jwt_utils import generate_jwt_token, get_user_from_token

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """User registration endpoint"""
    try:
        print(f"Signup request data: {request.data}")
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Account created successfully!',
                'token': token,
                'user': user_data
            }, status=status.HTTP_201_CREATED)
        else:
            print(f"Signup validation errors: {serializer.errors}")
            
            # Handle specific case of existing email
            if 'email' in serializer.errors:
                error_messages = serializer.errors['email']
                if any('already exists' in str(msg).lower() for msg in error_messages):
                    return Response({
                        'success': False,
                        'message': 'An account with this email already exists. Please try logging in instead.',
                        'errors': serializer.errors,
                        'existing_user': True
                    }, status=status.HTTP_409_CONFLICT)
            
            return Response({
                'success': False,
                'message': 'Registration failed. Please check your input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    try:
        print(f"Login request data: {request.data}")
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = generate_jwt_token(user)
            
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': user_data
            }, status=status.HTTP_200_OK)
        else:
            print(f"Login validation errors: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Invalid credentials',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
def validate_token(request):
    """Validate JWT token endpoint"""
    try:
        user = get_user_from_token(request)
        
        if user:
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'valid': True,
                'user': user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'valid': False,
                'message': 'Invalid or expired token'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
def user_profile(request):
    """Get user profile endpoint"""
    try:
        user = get_user_from_token(request)
        
        if user:
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'user': user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint to verify API is running"""
    return Response({
        'success': True,
        'message': 'API is running',
        'status': 'healthy'
    }, status=status.HTTP_200_OK)
