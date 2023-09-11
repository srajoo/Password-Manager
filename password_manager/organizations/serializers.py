from rest_framework import serializers
from .models import Organization, OrganizationMembership, Vault, Password, VaultAccess, SharedPasswordLink
from django.contrib.auth import get_user_model
from password_validator import validate_password_strength, show_password_strength
from django.contrib.auth.hashers import make_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')
    
class VaultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vault
        fields = '__all__'

class VaultAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultAccess
        fields = ('vault', 'user', 'can_view', 'can_edit')

class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = OrganizationMembership
        fields = ('user', 'organization', 'role', 'created_at', 'modified_at')

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'description','creator')

class OrganizationDetailSerializer(serializers.ModelSerializer):
    vaults = VaultSerializer(many=True, read_only=True, source='organization_vaults')
    memberships = OrganizationMembershipSerializer(many=True, read_only=True, source='organization_members')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description','creator', 'memberships', 'vaults')


    def create(self, validated_data):
    
        user_id = validated_data.pop('user')
        org_membership = OrganizationMembership.objects.create(**validated_data)

        return org_membership

class OrganizationMembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMembership
        fields = ('role',)


class PasswordSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        validators=[validate_password_strength],
    )

    password_strength = serializers.SerializerMethodField()

    class Meta:
        model = Password
        fields = ('id','title', 'username', 'password','password_strength', 'password_expiration_days', 'url', 'notes', 'created_at', 'modified_at', 'vault',)
    
    def create(self, validated_data):
        
        validated_data['password'] = make_password(validated_data['password'])
        password_obj = Password.objects.create(**validated_data)
        
        password_obj.save()

        return password_obj

    def get_password_strength(self, obj):
        password = obj.password
        strength = show_password_strength(password)

        return strength

class PasswordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Password
        fields = ['title', 'username', 'password', 'url', 'notes']

class SharedPasswordLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedPasswordLink
        fields = ('expiration_time',)

class SharedPasswordRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedPasswordLink
        fields = ('id', 'password', 'shared_by', 'expiration_time', 'link')


