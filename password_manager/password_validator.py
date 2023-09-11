from django.core.exceptions import ValidationError
from rest_framework import serializers

def validate_password_strength(password):
    """
    Validate that a password is strong.
    """
   
    min_length = 8
    if len(password) < min_length:
        raise ValidationError(
            f"The password must be at least {min_length} characters long."
        )

    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        raise ValidationError("The password must contain at least one uppercase letter.")

    # Check for at least one lowercase letter
    if not any(char.islower() for char in password):
        raise ValidationError("The password must contain at least one lowercase letter.")

    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        raise ValidationError("The password must contain at least one digit.")

    # Check for at least one special character
    special_characters = "!@#$%^&*()_-+=<>?/[]{}|"
    if not any(char in special_characters for char in password):
        raise ValidationError("The password must contain at least one special character.")


def show_password_strength(password):
    """
    Check strength of a password
    """
    complexity_score = 0

    if any(char.isupper() for char in password):
        complexity_score += 1

    if any(char.islower() for char in password):
        complexity_score += 1

    if any(char.isdigit() for char in password):
        complexity_score += 1

    special_characters = "!@#$%^&*()-_+=<>?/[]{}|"
    if any(char in special_characters for char in password):
        complexity_score += 1

    if complexity_score <= 1:
        return 'Weak'
    elif complexity_score == 3:
        return "Moderate"
    else:
        return "Strong"

   

    

    
