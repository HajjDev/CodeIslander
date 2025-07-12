from functools import wraps
from django.shortcuts import render, redirect

def twofa_enabled(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.user.totpEnabled:
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper