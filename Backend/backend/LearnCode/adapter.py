# yourapp/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect

class NoFormSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        messages.error(request, "Error occured, session expired. Please sign in again using a 3rd party platform.")
        response = redirect('/LearnCode/register') 
        raise ImmediateHttpResponse(response)