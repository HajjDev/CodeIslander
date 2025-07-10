import pyotp
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def enableTotp(request):
    if request.method == 'POST':
        code = request.POST['digitcode']
        user = request.user
        verification = pyotp.TOTP(user.secret, interval=300)

        if verification.verify(code):
            user.totpEnabled = True
            user.save()

            mail_subject = 'Two-factor authentication (2FA) activated successfully!'
            message = render_to_string('email/totp/template_activated.html', {
                'user': user.username,
                'domain': get_current_site(request).domain,
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            logout(request)
            return redirect('login')

    return render(request, "security/totp/enable_totp.html")