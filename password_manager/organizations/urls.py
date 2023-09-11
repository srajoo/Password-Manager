from django.urls import path
from . import views

urlpatterns = [
    #Organizations
    path('', views.ListAllOrganizations.as_view(), name="organizations"),
    path('create/', views.CreateOrganization.as_view(), name="create-organization"),
    path('<int:pk>', views.ListDetailsOrganization.as_view(), name="view-organization"),
    path('<int:organization_id>/<str:name>', views.UpdateOrganization.as_view(), name="update-organization"),
    path('<int:organization_id>/delete/<str:name>', views.DeleteOrganization.as_view(), name="delete-organization"),

    # Organization Membership
    path('<int:organization_id>/members/<str:name>',  views.AddOrganizationMembers.as_view(), name="add-member"),
    path('<int:organization_id>/members/view/view-members', views.ListOrganizationMembers.as_view(), name="view-members"),
    path('<int:organization_id>/members/<int:user_id>/<str:name>/', views.UpdateUserOrganizationRole.as_view(), name='update-member-role'),
    path('<int:organization_id>/members/<int:user_id>/delete/<str:name>/', views.DeleteUserFromOrganization.as_view(), name='delete-member'),

    #Vaults
    path('<int:organization_id>/vaults/<str:name>/', views.CreateVault.as_view(), name='create-vault'),
    path('vaults/', views.ListAllVaults.as_view(), name='list-vaults'),
    path('<int:organization_id>/vaults/<int:vault_id>/<str:name>', views.VaultAccessView.as_view(), name='give-vault-access'),
    path('<int:organization_id>/vaults/<int:vault_id>/members/<str:name>', views.ViewVaultMembers.as_view(), name='view-vault-access-members'),
    path('vaults/<int:vault_id>/members/<int:user_id>/<str:name>/', views.UpdateVaultAccess.as_view(), name='update-vault-access'),
    path('vaults/<int:vault_id>/update/update-vault', views.UpdateVaultDetails.as_view(), name='update-vault-details'),
    path('vaults/<int:pk>/delete/delete-vault', views.DeleteVault.as_view(), name='delete-vault'),

    #Passwords
    path('vaults/<int:vault_id>/passwords/add-password/', views.CreatePassword.as_view(), name='create-password'),
    path('vaults/<int:vault_id>/passwords/view', views.ListVaultPasswords.as_view(), name='list-vault-passwords'),
    path('vaults/<int:vault_id>/passwords/<int:password_id>/update', views.UpdatePassword.as_view(), name='update-password'),
    path('vaults/<int:vault_id>/passwords/<int:password_id>/delete', views.DeletePassword.as_view(), name='delete-password'),
    path('vaults/<int:vault_id>/passwords/<int:password_id>/share-password/', views.SharePasswordView.as_view(), name='share-password'),
    path('shared-password/<str:link>/', views.SharedPasswordRetrieveView.as_view(), name='shared-password-retrieve'),
    
]   