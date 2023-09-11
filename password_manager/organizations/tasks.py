from celery import shared_task
from django.utils import timezone
from .models import Password

@shared_task
def check_password_expiry_and_notify():
    # Get the current date
    current_date = timezone.now().date()

    # Calculate the date when passwords will expire
    expiration_date = current_date + timezone.timedelta(days=90)

    # Get passwords that are about to expire
    expiring_passwords = Password.objects.filter(
        password_expiration_days__gt=0,
        notified=False,
        modified_at__lte=expiration_date
    )

    for password in expiring_passwords:
        password.notified = True
        password.save()