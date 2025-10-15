from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import AppUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=True)
    
    class Meta:
        model = AppUser
        fields = ('email', 'password', 'confirm_password', 'name')
    
    def validate_email(self, value):
        if AppUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before creating user
        validated_data['password_hash'] = make_password(validated_data.pop('password'))
        return AppUser.objects.create(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            try:
                user = AppUser.objects.get(email=email)
                if check_password(password, user.password_hash):
                    if user.is_active:
                        data['user'] = user
                        return data
                    else:
                        raise serializers.ValidationError("User account is disabled")
                else:
                    raise serializers.ValidationError("Invalid email or password")
            except AppUser.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Must include email and password")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('id', 'email', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')
