# Create your views here.
from django.shortcuts import render, redirect
import requests
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from ..forms import authenticate_email
from django.contrib import messages
from django.conf import settings


def user_login(request):
    if request.method == 'POST':
        # Verify reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if not result.get('success'):
            # reCAPTCHA failed
            context = {'error': 'Invalid reCAPTCHA. Please try again.'}
            messages.error(request, context['error'])
            return render(request, 'login.html')

        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            user = authenticate_email(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')