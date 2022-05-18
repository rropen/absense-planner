from django import forms
from django.db.models.base import Model
from django.forms import models
from django.contrib.auth.models import User

from .models import Absence

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


class AbsenceForm(forms.ModelForm):
    
    class Meta:
        model = Absence
        fields = ["start_date", "end_date"]

    def clean(self):
        def end_date_valid():
            if start_date > end_date:
                return False
            return True


        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not end_date_valid():
            raise forms.ValidationError(f"End Date must be after start date {start_date}, {end_date}")

    start_date = forms.DateField(label="Starting Date:", required=True, input_formats=['%d/%m/%Y'])
    end_date = forms.DateField(label="Ending Date:", required=True, input_formats=['%d/%m/%Y'])


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []