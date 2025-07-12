from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

def twofa_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        id=request.session.get("pre_2fa_id")
        if not id:
            return redirect('login')
        
        User = get_user_model()
        user = User.objects.get(id=id)
        print(user)
        
        if not user:
            return redirect('login')
        
        if not user.totpEnabled:
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper