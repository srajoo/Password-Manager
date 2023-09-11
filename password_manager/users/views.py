from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login, logout
import secrets
from collections import OrderedDict
from rest_framework.views import APIView

# Create your views here.

@permission_classes([permissions.AllowAny])
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

@permission_classes([permissions.AllowAny])
class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], secret_key=serializer.validated_data['secret_key'], password=serializer.validated_data['password'])

        if user:
            login(request, user)
            return Response({'message': 'User logged in successfully', 'user': serializer.data}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
   
@permission_classes([permissions.IsAuthenticated])
class UserLogoutView(APIView):
    def post(self, request):
        logout(request)

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)