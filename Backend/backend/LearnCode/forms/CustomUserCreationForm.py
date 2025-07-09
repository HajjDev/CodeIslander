from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from LearnCode.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    emailChangeRequest = forms.CharField(required=False, widget=forms.HiddenInput())
    class Meta:
        model = CustomUser
        fields = ("username","first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.emailChangeRequest = ""
        if commit:
            user.save()
        return user

    def clean_email(self):
        User = get_user_model()
        email = self.cleaned_data["email"]
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError("Email already exists")

        return email