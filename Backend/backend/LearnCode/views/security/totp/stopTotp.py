from django.shortcuts import redirect

def stopTotp(request):
    return redirect("disable_totp")