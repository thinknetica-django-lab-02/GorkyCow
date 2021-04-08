from django import forms
from django.db.models import fields

from .models import Profile, User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone_number",)
        labels = {
            "phone_number": "Телефон",
        }
