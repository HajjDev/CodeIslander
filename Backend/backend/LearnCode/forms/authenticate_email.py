from django.contrib.auth.models import User

def authenticate_email(request=None, email=None, password=None, **credentials):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if user.check_password(password):
        return user
    return None