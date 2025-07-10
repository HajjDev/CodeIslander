from django.shortcuts import render
from LearnCode.utils import logout_required

@logout_required
def welcome(request):
    return render(request, 'welcome.html')