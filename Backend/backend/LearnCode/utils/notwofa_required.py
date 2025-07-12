from functools import wraps
from django.shortcuts import render, redirect

def notwofa_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.totpEnabled:
            return redirect("profile")

        return view_func(request, *args, **kwargs)

    return wrapper