from django.shortcuts import render


def support_funct(request):
    return render(request, 'support.html')