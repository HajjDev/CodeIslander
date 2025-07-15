from django.shortcuts import render
from CodeIslander.utils import logout_required

@logout_required
def welcome(request):
    return render(request, 'welcome.html')