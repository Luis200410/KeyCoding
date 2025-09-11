from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
        }


class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "avatar", "bio", "company", "job_title", "location", "website",
            "github", "linkedin", "primary_language", "interests"
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "interests": forms.Textarea(attrs={"rows": 3}),
        }
