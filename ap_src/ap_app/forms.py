import datetime
from difflib import SequenceMatcher

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.forms import models
from django.utils.timezone import now

from .models import Absence, RecurringAbsences, Team, UserProfile

User = get_user_model()
from recurrence.forms import RecurrenceField, RecurrenceWidget


#The form for creating a team
class CreateTeamForm(forms.ModelForm):
    #details the model the form uses as well as the field names
    class Meta:
        model = Team
        fields = ["name", "description", "private"]

    #The name of the team. Has to be between 3 and 64 characters, and is required.
    name = forms.CharField(
        min_length=3,
        max_length=64,
        required=True,
        widget=forms.TextInput(attrs={"class": "", "placeholder": "Team Name", "id":"nameInput"}),
    )

    #The description of the team. Can be up to 512 characters long. Is optional.
    description = forms.CharField(
        max_length=512,
        required=False,
        widget=forms.Textarea(attrs={"class": "", "placeholder": "Team Description","rows":4, "cols":15}),
    )

    #Whether or not the team is private
    private = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": ""})
    )

    def name_similarity(self) -> float:
        """Returns float between 0 and 1 depending on the similarity
        of the current name compared to existing team names. Returns
        NoneType if there are no similarities."""

        teams = Team.objects.all()
        for team in teams:
            similarity = SequenceMatcher(None, self["name"].value(), team.name).ratio()
            if similarity >= 0.9:
                return similarity


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

# maybe add name field
class RecurringAbsencesForm(forms.ModelForm):
    class Meta:
        model = RecurringAbsences
        fields = ['ID','Recurrences']
    def clean(self):
        cleaned_data = super().clean()
    
    class Media:
        js = ('/admin/jsi18n', '/admin/js/core.js',)
    
    
class TargetUserForm(forms.ModelForm):
    class Meta:
        model = RecurringAbsences
        fields = ['target_user']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("target_user")
        super().__init__(*args, **kwargs)
        self.fields["target_user"].initial = UserProfile.objects.get(user=self.user)


    target_user = forms.ModelChoiceField(
        label="User:", required=True, queryset=User.objects.all(), initial=None, 
    )
    

    
class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ["start_date", "end_date", "user"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["user"].initial = UserProfile.objects.get(user=self.user)

    def clean(self):
        def end_date_valid():
            if start_date > end_date:
                return False
            return True

        
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not end_date_valid():
            raise forms.ValidationError(
                f"End Date must be after start date {start_date}, {end_date}"
            )

    start_date = forms.DateField(
        label="Starting Date:",
        required=True,
        input_formats=['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(attrs={"type": "date"},format='%d-%m-%Y'),
    )
    
    end_date = forms.DateField(
        label="Ending Date:",
        required=True,
        input_formats=['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'],
        widget=forms.DateInput(attrs={"type": "date"},format='%d-%m-%Y'),
        initial=lambda: now().date() + datetime.timedelta(days=1),
    )
    user = forms.ModelChoiceField(
        label="User:", required=True, queryset=User.objects.all(), initial=None, 
    )

class SwitchUser(forms.Form):
    class Meta:
        fields = ["user"]
    
    user = forms.ModelChoiceField(
        label="", required = True, queryset=User.objects.all(), initial=None
    )
    

class DeleteUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []


class AcceptPolicyForm(forms.Form):
    check = forms.CheckboxInput()
