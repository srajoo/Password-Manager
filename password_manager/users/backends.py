from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, secret_key=None, **kwargs):
        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if user is not None and user.check_password(password) and user.secret_key == secret_key:
            # Clear the failed login attempts on successful login
            user.failed_login_attempts = 0
            user.save()

            if user.is_active is False:
                lock_duration = timezone.timedelta(minutes=30) 
                if user.locked_at and user.locked_at + lock_duration < timezone.now():
                    user.is_active = True
                    user.failed_login_attempts = 0
                    user.save()

            return user

        # Increment the failed login attempts
        if user is not None:
            user.failed_login_attempts += 1
            user.save()

            # Lock the account after 3 failed attempts
            if user.failed_login_attempts >= 3:
                user.is_active = False
                user.locked_at = timezone.now()
                user.save()

                raise AuthenticationFailed(detail='Account locked out')

        return None
