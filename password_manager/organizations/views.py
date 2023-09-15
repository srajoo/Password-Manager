from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .permissions import CreatorAndEditorPermission, CreatorAndMemberPermission, VaultAccessPermission, PasswordAccessPermission
from django.db.models import Q
from .utils import generate_unique_link
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

from .models import Organization, OrganizationMembership, Vault, Password, VaultAccess, SharedPasswordLink
from .serializers import UserSerializer, OrganizationSerializer, OrganizationDetailSerializer, OrganizationMembershipSerializer, OrganizationMembershipUpdateSerializer, VaultSerializer, PasswordSerializer, PasswordUpdateSerializer, VaultAccessSerializer, SharedPasswordLinkSerializer, SharedPasswordRetrieveSerializer

from throttles import UserThrottle

User = get_user_model()


# Create your views here.

#Organization Views

@permission_classes([permissions.IsAuthenticated])
class ListAllOrganizations(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    pagination_class = PageNumberPagination
    throttle_classes = [UserThrottle]

    def get_queryset(self):
        user = self.request.user

        queryset = Organization.objects.filter(
            models.Q(creator=user) | models.Q(members=user)
        ).distinct()
        
        return queryset

    def list(self, request, *args, **kwargs):
        organizations = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(organizations, many=True)

        response_data = {
            'organizations': serializer.data,
        }

        return self.get_paginated_response(response_data)
   
@permission_classes([permissions.IsAuthenticated])
class CreateOrganization(generics.CreateAPIView):
    throttle_classes = [UserThrottle]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


@permission_classes([permissions.IsAuthenticated, CreatorAndMemberPermission])
class ListDetailsOrganization(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationDetailSerializer
    throttle_classes = [UserThrottle]


@permission_classes([permissions.IsAuthenticated, CreatorAndEditorPermission])
class UpdateOrganization(generics.UpdateAPIView):
    serializer_class = OrganizationSerializer
    throttle_classes = [UserThrottle]

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(creator=user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset, pk=self.kwargs.get('organization_id'))
        
        return obj


@permission_classes([permissions.IsAuthenticated, CreatorAndEditorPermission])
class DeleteOrganization(generics.DestroyAPIView):
    serializer_class = OrganizationSerializer
    throttle_classes = [UserThrottle]
    
    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(creator=user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset, pk=self.kwargs.get('organization_id'))
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({'message': 'Organization has been deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# Organization Membership views

@permission_classes([permissions.IsAuthenticated, CreatorAndEditorPermission])
class AddOrganizationMembers(generics.CreateAPIView):
    queryset = OrganizationMembership.objects.all()
    serializer_class = OrganizationMembershipSerializer
    throttle_classes = [UserThrottle]
    
    def create(self, request, *args, **kwargs):
        existing_user = User.objects.filter(email=request.data['user.email']).first()
        organization_data = request.data.copy()
        
        if existing_user:
            user = existing_user
        else:
            user_serializer = UserSerializer(data={'email': request.data['user']})
        
            if user_serializer.is_valid():
                user = user_serializer.save()
            else:
                return Response({'detail': 'Could not create user'}, status=status.HTTP_403_FORBIDDEN)
        

        del organization_data['user.email']
        organization_data['user'] = user
      
        organization_serializer = OrganizationMembershipSerializer(data=organization_data)
    
        if organization_serializer.is_valid():
            organization_membership = organization_serializer.save()
            organization_membership.user = user
            organization_membership.save()
        else:
            return Response({'detail': 'Failed to add member'}, status=status.HTTP_400_BAD_REQUEST)
    
        return Response({'detail': 'Member has been added'}, status=status.HTTP_200_OK)

@permission_classes([permissions.IsAuthenticated])
class ListOrganizationMembers(generics.ListAPIView):
    serializer_class = OrganizationMembershipSerializer
    pagination_class = PageNumberPagination
    throttle_classes = [UserThrottle]

    def get_queryset(self):
        organization_id = self.kwargs.get('organization_id')
        organization = get_object_or_404(Organization, pk=organization_id)
        user = self.request.user

        if organization.creator == user or organization.members.filter(id=user.id).exists():
            return OrganizationMembership.objects.filter(organization=organization).select_related('user')

        return None
    

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is not None:
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            
            return self.get_paginated_response(serializer.data)
        else:
            return Response({'detail': 'You are not part of this organization'}, status=status.HTTP_403_FORBIDDEN)


@permission_classes([permissions.IsAuthenticated, CreatorAndEditorPermission])
class UpdateUserOrganizationRole(generics.UpdateAPIView):
    queryset = OrganizationMembership.objects.all()
    serializer_class = OrganizationMembershipUpdateSerializer
    throttle_classes = [UserThrottle]

    def get_object(self):
        organization_id = self.kwargs.get('organization_id')
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(OrganizationMembership, organization_id=organization_id, user_id=user_id)


@permission_classes([permissions.IsAuthenticated, CreatorAndEditorPermission])
class DeleteUserFromOrganization(generics.DestroyAPIView):
    queryset = OrganizationMembership.objects.all()
    serializer_class = OrganizationMembershipSerializer
    throttle_classes = [UserThrottle]

    def get_object(self):
        organization_id = self.kwargs.get('organization_id')
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(OrganizationMembership, organization_id=organization_id, user_id=user_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'User has been deleted from the organization.'}, status=status.HTTP_204_NO_CONTENT)


# Vault Views
@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class VaultAccessView(generics.CreateAPIView):
    queryset = VaultAccess.objects.all()
    serializer_class = VaultAccessSerializer
    throttle_classes = [UserThrottle]

    def create(self, request, *args, **kwargs):
        user = request.user
        vault_id = kwargs.get('vault_id')
        return super().create(request, *args, **kwargs)


@permission_classes([permissions.IsAuthenticated, CreatorAndEditorPermission])
class CreateVault(generics.CreateAPIView):
    queryset = Vault.objects.all()
    serializer_class = VaultSerializer
    throttle_classes = [UserThrottle]

    def get_organization(self):
        organization_id = self.kwargs.get('organization_id')
        return Organization.objects.get(pk=organization_id)

    def create(self, request, *args, **kwargs):
        organization = self.get_organization()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vault = serializer.save(organization=organization)

        VaultAccess.objects.create(vault=vault, user=request.user, can_view=True, can_edit=True)
        VaultAccess.objects.create(vault=vault, user=organization.creator, can_view=True, can_edit=True)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

@permission_classes([permissions.IsAuthenticated])
class ListAllVaults(generics.ListAPIView):
    serializer_class = VaultSerializer
    throttle_classes = [UserThrottle]

    def get_queryset(self):
        organization_id = self.kwargs.get('organization_id')
        return Vault.objects.filter(organization__id=organization_id)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({'message': 'No vaults exist for this organization.'}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@permission_classes([permissions.IsAuthenticated, PasswordAccessPermission])
class ViewVaultMembers(generics.ListAPIView):
    serializer_class = VaultAccessSerializer
    throttle_classes = [UserThrottle]

    def get_queryset(self):
        vault_id = self.kwargs.get('vault_id')
        return VaultAccess.objects.filter(vault_id=vault_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class UpdateVaultAccess(generics.UpdateAPIView):
    queryset = VaultAccess.objects.all()
    serializer_class = VaultAccessSerializer
    throttle_classes = [UserThrottle]

    def get_object(self):
        vault_id = self.kwargs.get('vault_id')
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(VaultAccess, vault_id=vault_id, user_id=user_id)

    

@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class UpdateVaultDetails(generics.UpdateAPIView):
    queryset = Vault.objects.all()
    serializer_class = VaultSerializer
    throttle_classes = [UserThrottle]
    
    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['vault_id'])

@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class DeleteVault(generics.DestroyAPIView):
    queryset = Vault.objects.all()
    throttle_classes = [UserThrottle]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        return obj


@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class CreatePassword(generics.CreateAPIView):
    throttle_classes = [UserThrottle]
    serializer_class = PasswordSerializer
    
    
@permission_classes([permissions.IsAuthenticated, PasswordAccessPermission])
class ListVaultPasswords(generics.ListAPIView):
    serializer_class = PasswordSerializer
    throttle_classes = [UserThrottle]

    def get_queryset(self):
        vault_id = self.kwargs.get('vault_id')
        return Password.objects.filter(vault_id=vault_id)


@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class UpdatePassword(generics.UpdateAPIView):
    throttle_classes = [UserThrottle]
    queryset = Password.objects.all()
    serializer_class = PasswordUpdateSerializer
    
    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['password_id'])


@permission_classes([permissions.IsAuthenticated, VaultAccessPermission])
class DeletePassword(generics.DestroyAPIView):
    throttle_classes = [UserThrottle]
    queryset = Password.objects.all()
    lookup_url_kwarg = 'password_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@permission_classes([permissions.IsAuthenticated, PasswordAccessPermission])
class SharePasswordView(generics.CreateAPIView):
    queryset = SharedPasswordLink.objects.all()
    serializer_class = SharedPasswordLinkSerializer
    throttle_classes = [UserThrottle]

    def create(self, request, *args, **kwargs):
        vault_id = self.kwargs.get('vault_id')
        print(vault_id)
        password_id = self.kwargs.get('password_id')

        try:
            password = Password.objects.get(pk=password_id, vault_id=vault_id)
        except Password.DoesNotExist:
            return Response({'error': 'Password not found in the vault.'}, status=status.HTTP_404_NOT_FOUND)

        shared_by = self.request.user
        expiration_time = self.request.data.get('expiration_time')

        if not expiration_time:
            expiration_time = timezone.now() + timezone.timedelta(days=1)

        shared_password =SharedPasswordLink(
            password=password,
            shared_by=shared_by,
            expiration_time=expiration_time,
        )

        shared_password.link = generate_unique_link()

        shared_password.save()

        return Response({'link': shared_password.link}, status=status.HTTP_201_CREATED)

@permission_classes([permissions.AllowAny])
class SharedPasswordRetrieveView(generics.RetrieveAPIView):
    queryset = SharedPasswordLink.objects.all()
    serializer_class = SharedPasswordRetrieveSerializer
    throttle_classes = [UserThrottle]

    def get_object(self):
        link = self.kwargs.get('link')
        return SharedPasswordLink.objects.filter(link=link).first()

    def retrieve(self, request, *args, **kwargs):
        shared_password = self.get_object()
        
        current_time = timezone.now()
    
        if shared_password.expiration_time >= current_time:
            password_serializer = PasswordSerializer(shared_password.password)
            return Response({'password': password_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Link expired.'}, status=status.HTTP_404_NOT_FOUND)
