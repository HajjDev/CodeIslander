from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
import pyotp
from .....utils import twofa_required, thirdpartybanned, logout_required


@twofa_required
@logout_required
def verify(request):
    User = get_user_model()

    if request.method == "POST":
        code = request.POST['digitcode']
        user = User.objects.get(id=request.session.get("pre_2fa_id"))
        verification = pyotp.TOTP(user.secretLogin, interval=300)

        if verification.verify(code):
            login(request, user)
            return redirect("home")

    return render(request, 'security/totp/login_verification.html')