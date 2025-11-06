from django.shortcuts import render

def vip_funct(request):
    return render(request, 'vip.html')