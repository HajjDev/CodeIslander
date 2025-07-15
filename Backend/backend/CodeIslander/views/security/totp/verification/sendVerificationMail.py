from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import redirect
import pyotp

def sendVerificationMail(request, user):
    user.secretLogin = pyotp.random_base32()
    user.save()

    mail_subject = 'Your login verification Code'
    message = render_to_string('email/totp/template_login.html', {
        'user': user.username,
        'token': pyotp.TOTP(user.secretLogin, interval=300).now()
    })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()