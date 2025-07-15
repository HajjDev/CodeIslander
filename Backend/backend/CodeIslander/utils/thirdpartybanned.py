from functools import wraps
from django.shortcuts import render, redirect

def thirdpartybanned(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):        
        if not request.user.email:
            return redirect("profile")

        return view_func(request, *args, **kwargs)

    return wrapper