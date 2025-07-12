from django.shortcuts import redirect
from .....utils import twofa_enabled, thirdpartybanned
from django.contrib.auth.decorators import login_required

@login_required
@twofa_enabled
@thirdpartybanned
def stopTotp(request):
    return redirect("disable_totp")