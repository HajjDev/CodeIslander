from django.shortcuts import redirect, render
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import logout, authenticate

def disableTotp(request):
    if request.method == "POST":
        user = request.user
        password = request.POST['inputPass']

        # Compare the pass
        verif = authenticate(request, username=user, password=password)
        if verif:
            user.totpEnabled = False
            user.secretTotp = ""
            user.save()

            mail_subject = 'Two-factor authentication (2FA) deactivated successfully!'
            message = render_to_string('email/totp/template_deactivated.html', {
                'user': user.username,
                'domain': get_current_site(request).domain,
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            logout(request)
            return redirect('login')
    
    return render(request, "security/totp/disable_totp.html")