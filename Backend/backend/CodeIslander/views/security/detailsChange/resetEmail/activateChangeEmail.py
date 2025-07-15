from .....tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.shortcuts import redirect

def activateChangeEmail(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        print("hii")
        user.email = user.emailChangeRequest
        user.emailChangeRequest = ""
        user.save()

        messages.success(request, 'Your email has been changed! Please log-in back to your account.')
        return redirect('login')
    else:
        messages.error(request, 'Email confirmation link is invalid!')

    return redirect('home')