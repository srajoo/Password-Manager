from rest_framework import permissions
from .models import Organization, OrganizationMembership, Vault, VaultAccess

def is_creator(user, organization):
    return Organization.objects.filter(id=organization, creator=user).exists()

def is_editor(user, organization):
    return OrganizationMembership.objects.filter(organization_id=organization, user=user, role=0).exists()

def is_member(user, organization):
    return Organization.objects.filter(id=organization, members=user).exists()

def is_vault_owner(user, vault):
    return Vault.objects.filter(id=vault, owner=user).exists()

def has_vault_edit_access(user, vault):
    return VaultAccess.objects.filter(vault_id=vault, can_edit=True).exists()

def has_vault_view_access(user, vault):
    return VaultAccess.objects.filter(vault_id=vault, can_view=True).exists()
    

class CreatorAndMemberPermission(permissions.BasePermission):
    message = 'You do not have permission to view the details of this organization'

    def has_permission(self, request, view):
        organization_id = view.kwargs.get('pk')

        user_is_creator = is_creator(request.user, organization_id)
        user_is_member = is_member(request.user, organization_id)
        
        if user_is_creator | user_is_member:
            return True
   
class CreatorAndEditorPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        action = view.kwargs.get('name')
        if action == 'update-organization':
            self.message = 'You do not have permission to update this organization'
        elif action == 'delete-organization':
            self.message = 'You do not have permission to delete this organization'
        elif action == 'add-member':
            self.message = 'You do not have permission to add members to this organization'
        elif action == 'update-member-role':
            self.message = 'You do not have permission to update this user role'
        elif action == 'delete-member':
            self.message = 'You do not have permission to delete this user'
        elif action == 'create-vault':
            self.message = 'You do not have permission to create a vault in this organization'

    
        organization_id = view.kwargs.get('organization_id')

        user_is_creator = is_creator(request.user, organization_id)
        has_editor_role = is_editor(request.user, organization_id)

        if user_is_creator | has_editor_role:
            return True

class VaultAccessPermission(permissions.BasePermission):
    message = "You do not have access to this vault"

    def has_permission(self, request, view):
        organization_id = view.kwargs.get('organization_id')
        vault_id = view.kwargs.get('vault_id')
        
        user_is_creator = is_creator(request.user, organization_id)
        user_is_owner = is_vault_owner(request.user, vault_id)
        user_has_vault_edit_access = has_vault_edit_access(request.user, vault_id)

        if user_is_creator | user_is_owner | user_has_vault_edit_access:
            return True

class PasswordAccessPermission(permissions.BasePermission):
    message = "You do not have access to this vault"

    def has_permission(self, request, view):
        vault_id = view.kwargs.get('vault_id')
        
        vault = Vault.objects.get(pk=vault_id)
        organization_id = vault.organization_id

        user_is_creator = is_creator(request.user, organization_id)
        user_is_owner = is_vault_owner(request.user, vault_id)
        user_has_vault_edit_access = has_vault_edit_access(request.user, vault_id)
        user_has_vault_view_access = has_vault_view_access(request.user, vault_id)

        if user_is_creator | user_is_owner | user_has_vault_edit_access | user_has_vault_view_access:
            return True



