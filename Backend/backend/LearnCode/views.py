# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, authenticate_email

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None: user = authenticate_email(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to your home page
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to your home page

def user_home(request):
    return render(request, 'home.html')