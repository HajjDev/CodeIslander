from functools import wraps
from django.shortcuts import render, redirect

def logout_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper
