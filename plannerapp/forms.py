from django import forms
from django.db.models.base import Model
from django.forms import models

from plannerapp.models import employees


class names(forms.ModelForm):
    class Meta:
        model = employees
        fields = ["firstName", "lastName"]


class login(forms.Form):
    name = forms.CharField(
        label="Name:",
        max_length=200,
    )
    password = forms.CharField(
        label="Password:",
        max_length=200,
    )


class sign_up(forms.Form):
    name = forms.CharField(
        label="Name:",
        max_length=200,
    )
    create_password = forms.CharField(
        label="Create a Password:",
        max_length=200,
    )
    verify_password = forms.CharField(
        label="Re-enter Password:",
        max_length=200,
    )


class register(forms.Form):
    check = forms.BooleanField()
