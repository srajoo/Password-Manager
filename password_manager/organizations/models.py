from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_organizations', default="")
    members = models.ManyToManyField(User, through='OrganizationMembership')

    def __str__(self):
        return self.name
    
    
class OrganizationMembership(models.Model):
    ROLE_CHOICES = (
        (0, 'Editor'),
        (1, 'Viewer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='organization_memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_members')
    role = models.IntegerField(choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        role_str = dict(self.ROLE_CHOICES).get(self.role, "Unknown")
        return f"{self.user} in {self.organization} as {role_str}"
    
class Vault(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="organization_vaults")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class VaultAccess(models.Model):
    vault = models.ForeignKey(Vault, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)


class Password(models.Model):
    vault = models.ForeignKey('Vault', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    password_expiration_days = models.PositiveIntegerField(default=90)
    notified = models.BooleanField(default=False)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
        

class SharedPasswordLink(models.Model):
    password = models.ForeignKey('Password', on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=255, unique=True)
    expiration_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Link for {self.password} shared by {self.shared_by}"



