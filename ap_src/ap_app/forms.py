from django import forms
from django.db.models.base import Model
from django.forms import models
from django.contrib.auth.models import User
from .models import Team
from difflib import SequenceMatcher


class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "description", "private"]

    name            = forms.CharField(min_length=3, max_length=64, required=True, widget=forms.TextInput(attrs={"class":"", "placeholder":"Team Name"}))
    description     = forms.CharField(max_length=512, required=False, widget=forms.Textarea(attrs={"class":"", "placeholder":"Team Description"}))
    private         = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class":""}))

    def _name_similarity(self) -> (float | None):
        """Returns float between 0 and 1 depending on the similarity
        of the current name compared to existing team names. Returns
        NoneType if there are no similarities."""

        teams = Team.objects.all()
        for team in teams:
            similarity = SequenceMatcher(self.name, team.name).ratio()
            if similarity >= .5:
                return similarity


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

    start_date = forms.DateField(label="Starting Date:", required=True, input_formats=['%Y-%m-%d'], widget=forms.DateTimeInput(attrs={"type":"date"}))
    end_date = forms.DateField(label="Ending Date:", required=True, input_formats=['%Y-%m-%d'], widget=forms.DateTimeInput(attrs={"type":"date"}))


class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []