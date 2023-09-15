from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login, logout
import secrets
from collections import OrderedDict
from rest_framework.views import APIView
from throttles import UserThrottle
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

@permission_classes([permissions.AllowAny])
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    throttle_classes = [UserThrottle]

@permission_classes([permissions.AllowAny])
class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    throttle_classes = [UserThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        secret_key = serializer.validated_data['secret_key']
        password = serializer.validated_data['password']
        
        user = User.objects.filter(email=email).first()

        if user:
            if user.is_active is False:
                lock_duration = timezone.timedelta(minutes=30)
                if user.locked_at and user.locked_at + lock_duration >= timezone.now():
                    return Response({'error': 'Account locked out'}, status=status.HTTP_403_FORBIDDEN)
            
            auth_user = authenticate(email=email, secret_key=secret_key, password=password)
            
            if auth_user:
                login(request, user)
                return Response({'message': 'User logged in successfully', 'user': serializer.data}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
   
@permission_classes([permissions.IsAuthenticated])
class UserLogoutView(APIView):
    def post(self, request):
        logout(request)

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)