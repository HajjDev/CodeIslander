import pyotp
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .....utils import notwofa_required, thirdpartybanned

@login_required
@notwofa_required
@thirdpartybanned
def startTotp(request):
    user = request.user
    user.secretTotp = pyotp.random_base32()
    user.save()

    mail_subject = ' Your 2FA Activation Code (Valid for 5 Minutes)'
    message = render_to_string('email/totp/template_activate_totp.html', {
        'user': user.username,
        'token': pyotp.TOTP(user.secretTotp, interval=300).now(),
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()
    return redirect('verify_totp')