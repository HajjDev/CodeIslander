from django.shortcuts import render

def update_funct(request):
    return render(request, 'updates.html')