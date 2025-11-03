from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def map1(request):
    return render(request, 'map1.html')