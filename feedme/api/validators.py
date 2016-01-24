from django.conf import settings

from rest_framework.serializers import ValidationError

from feedme.utils import validate_user_funds

User = settings.AUTH_USER_MODEL


def validate_funds(user, amount):
    enough = validate_user_funds(user, amount)
    if not enough:
        raise ValidationError('Insufficient funds')
    return True
