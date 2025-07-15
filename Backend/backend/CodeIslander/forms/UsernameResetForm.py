from django import forms
from ..models.customUser import CustomUser

class UsernameResetForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username']
