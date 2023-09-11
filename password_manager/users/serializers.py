from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.response import Response
import secrets
from password_validator import validate_password_strength, show_password_strength
#from zxcvbn import zxcvbn

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        validators=[validate_password_strength],
    )
    secret_key = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('firstname', 'lastname', 'email', 'password', 'secret_key')
    
    def create(self, validated_data):
        
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.secret_key = secrets.token_urlsafe(30)
        user.save()
            
        token, created = Token.objects.get_or_create(user=user)
        self.context['request'].auth = token

        return user
    
    
    def to_representation(self, object):
        return {'message': 'User Registered successfully', 'firstname': object.firstname, 'lastname': object.lastname, 'email': object.email, 'secret_key': object.secret_key}
    

class UserLoginSerializer(serializers.Serializer):
    firstname = serializers.CharField(source='user.firstname', read_only=True)
    lastname = serializers.CharField(source='user.lastname', read_only=True)
    email = serializers.EmailField()
    secret_key = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'secret_key', 'password', 'firstname', 'lastname')
        