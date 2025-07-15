from django.contrib.auth import get_user_model

def authenticate_email(request=None, email=None, password=None, **credentials):
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if user.check_password(password):
        return user
    return None