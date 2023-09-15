from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Create your models here.

class UserManager(BaseUserManager):
	def create_user(self, **extra_fields):
		user = self.model(**extra_fields)
		user.save(using=self._db)
		return user


	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')
		
		return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	firstname = models.CharField(max_length=255, default="First")
	lastname = models.CharField(max_length=255, default="Last")
	email = models.EmailField(max_length=254, unique=True)
	secret_key = models.CharField(max_length=100)
	failed_login_attempts = models.PositiveIntegerField(default=0)
	locked_at = models.DateTimeField(null=True, blank=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	last_login = models.DateTimeField(null=True, blank=True)
	date_joined = models.DateTimeField(auto_now_add=True)

	USERNAME_FIELD = 'email'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = ['firstname', 'lastname']

	objects = UserManager()

	def __str__(self):
		return self.email
		