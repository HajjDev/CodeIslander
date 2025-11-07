from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def map2(request):
    return render(request, 'map2.html')