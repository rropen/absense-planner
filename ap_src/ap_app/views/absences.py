from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.urls import reverse
from django.views.generic import UpdateView

from ..forms import SwitchUser, RecurringAbsencesForm, TargetUserForm, AbsenceForm
from ..models import (Absence, RecurringAbsences,
                     UserProfile, User)
from ..utils.absence_utils import text_rules
from datetime import datetime, timedelta

from collections import namedtuple

# Profile page
@login_required
def profile_page(request):
    if request.method == "POST":
        form = SwitchUser(
            request.POST,
            initial={"user": request.user},
        )
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist=request.user
        )
        users = UserProfile.objects.filter(edit_whitelist=request.user)
        rec_absences = text_rules(request.user)

        if form.is_valid():
            absence_user = form.cleaned_data["user"].user

            absences = Absence.objects.filter(Target_User_ID=absence_user)
            rec_absences = text_rules(absence_user)
            return render(
                request,
                "ap_app/profile.html",
                {
                    "form": form,
                    "message": "Successfully switched user",
                    "absences": absences,
                    "users": users,
                    "recurring_absences": rec_absences,
                },
            )
    else:
        absences = Absence.objects.filter(Target_User_ID=request.user.id)
        rec_absences = text_rules(request.user)

        users = UserProfile.objects.filter(edit_whitelist=request.user)
        form = SwitchUser()
        form.fields["user"].queryset = users
        form.fields["user"].initial = request.user

        return render(
            request,
            "ap_app/profile.html",
            {
                "absences": absences,
                "users": users,
                "form": form,
                "recurring_absences": rec_absences,
            },
        )
    
@login_required
def absence_delete(request, absence_id: int, user_id: int, team_id: int = 1):
    try:
        absence = Absence.objects.get(pk=absence_id)
        absence.delete()
    except Absence.DoesNotExist: 
        pass
    if request.user == User.objects.get(id = user_id):
        return redirect("profile")
    return redirect("edit_team_member_absence", team_id, user_id)


@login_required
def absence_recurring_delete(
    request, absence_id: int, user_id: int, team_id: int = None
):
    absence = RecurringAbsences.objects.get(pk=absence_id)
    user = request.user
    absence.delete()
    if user == absence.Target_User_ID:
        return redirect("profile")
    return redirect("edit_team_member_absence", team_id, user_id)


class EditAbsence(UpdateView):
    template_name = "ap_app/edit_absence.html"
    model = Absence

    # specify the fields
    fields = ["absence_date_start", "absence_date_end"]

    def get_success_url(self) -> str:
        return reverse("profile")


@login_required
def edit_recurring_absences(request, pk):
    absence = RecurringAbsences.objects.get(ID=pk)

    if request.method == "POST":
        form = RecurringAbsencesForm(request.POST, instance=absence)
        form2 = TargetUserForm(request.POST, target_user=request.user)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
        rule = str(form["Recurrences"].value())

        if not ("DAILY" in rule or "BY" in rule):
            content = {
                "form": form,
                "form2": form2,
                "message": "Must select a day/month",
            }
            return render(request, "ap_app/edit_recurring_absence.html", content)

        if form2.is_valid():
            absence.Target_User_ID = form2.cleaned_data["target_user"].user
            absence.recurrences = form["Recurrences"].value()
            absence.save()
            return redirect("index")
    else:
        form = RecurringAbsencesForm(instance=absence)
        
        form2 = TargetUserForm(target_user=absence.Target_User_ID)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[absence.User_ID]
        )

    return render(
        request, "ap_app/edit_recurring_absence.html", {"form": form, "form2": form2}
    )

@login_required
def add_recurring(request) -> render:
    if request.method == "POST":
        form = RecurringAbsencesForm(request.POST)
        form2 = TargetUserForm(request.POST, target_user=request.user)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
        rule = str(form["Recurrences"].value())


        if not ("DAILY" in rule or "BY" in rule):
            content = {
                "form": form,
                "form2": form2,
                "message": "Must select a day/month",
            }
            return render(request, "ap_app/add_recurring_absence.html", content)

        if form2.is_valid():
            RecurringAbsences.objects.create(
                Recurrences=form["Recurrences"].value(),
                Target_User_ID=form2.cleaned_data["target_user"].user,
                User_ID=request.user,
            )
            return redirect("index")
    else:
        form = RecurringAbsencesForm()
        form2 = TargetUserForm(target_user=request.user)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

    content = {"form": form, "form2": form2}
    return render(request, "ap_app/add_recurring_absence.html", content)

#JC - Add an absence via the form
def manual_add(request:HttpRequest) -> render:
    #JC - POST request
    if request.method == "POST":
        form = AbsenceForm(
            request.POST, 
            user=request.user,
            initial={
                "start_date": datetime.now(),
                "end_date": lambda: datetime.now().date() + timedelta(days=1)
            }
        )
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

        #JC - Create absence
        if form.is_valid():
            absence = Absence()
            absence.absence_date_start = form.cleaned_data["start_date"]
            absence.absence_date_end = form.cleaned_data["end_date"]
            absence.User_ID = request.user
            absence.Target_User_ID = form.cleaned_data["user"].user

            #JC - Check if the dates overlap with an existing absence. 
            valid = True
            Range = namedtuple('Range', ['start', 'end'])
            r1 = Range(start=absence.absence_date_start, end=absence.absence_date_end)
            for x in Absence.objects.filter(Target_User_ID=form.cleaned_data["user"].user.id):
                r2 = Range(start=x.absence_date_start, end=x.absence_date_end)
                delta = (min(r1.end, r2.end) -max(r1.start, r2.start)).days + 1
                overlapp = max(0, delta)
                if overlapp == 1:
                    valid = False
            
            if valid:
                absence.save()
                return redirect("/")
            else:
                return render(request, "ap_app/add_absence.html", {
                    "form": form,
                    "message": "The absence conflicts with an existing absence",
                    "message_type": "is-danger"
                })

    #JC - GET request
    else:
        form = AbsenceForm(user=request.user)
        #JC - Allow users to edit others absence if they have permission
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
    
    content = {"form": form}
    return render(request, "ap_app/add_absence.html", content)