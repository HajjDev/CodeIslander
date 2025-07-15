from django import forms
from ..models.customUser import CustomUser

class EmailResetForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = []
