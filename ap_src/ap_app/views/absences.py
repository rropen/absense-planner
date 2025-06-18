from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.urls import reverse
from django.views.generic import UpdateView

from ..forms import SwitchUser, RecurringAbsencesForm, TargetUserForm, AbsenceForm
from ..models import (Absence, RecurringAbsences,
                     UserProfile, User, RecurringException)
from ..utils.absence_utils import text_rules
from datetime import datetime, timedelta

from collections import namedtuple
import json

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
        return redirect("my_absences")
    return redirect("edit_team_member_absence", team_id, user_id)


@login_required
def absence_recurring_delete(
    request, absence_id: int, user_id: int, team_id: int = None
):
    absence = RecurringAbsences.objects.get(pk=absence_id)
    user = request.user
    absence.delete()
    if user == absence.Target_User_ID:
        return redirect("my_absences")
    return redirect("edit_team_member_absence", team_id, user_id)


class EditAbsence(UpdateView):
    template_name = "ap_app/edit_absence.html"
    model = Absence

    # specify the fields
    fields = ["absence_date_start", "absence_date_end"]

    def get_success_url(self) -> str:
        return reverse("my_absences")


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

def manual_add(request:HttpRequest) -> render:
    """
    Add an absence via the form
    """
    if request.method == "POST":
        form = AbsenceForm(
            request.POST, 
            user=request.user,
            initial={
                "start_date": datetime.now(),
                "end_date": datetime.now().date() + timedelta(days=1)
            }
        )
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

        # Create absence
        if form.is_valid():
            NO_ABSENCES = 0
            absence = Absence()
            absence.absence_date_start = form.cleaned_data["start_date"]
            absence.absence_date_end = form.cleaned_data["end_date"]
            absence.User_ID = request.user
            absence.Target_User_ID = form.cleaned_data["user"].user

            # Check if the dates overlap with an existing absence. 
            valid = True # Assume absence is valid
            DateRange = namedtuple('Range', ['start', 'end'])
            absence_period = DateRange(start=absence.absence_date_start, end=absence.absence_date_end)
            existing_absences = Absence.objects.filter(Target_User_ID=form.cleaned_data["user"].user.id)
            for existing_absence in existing_absences:
                existing_absence_period = DateRange(start=existing_absence.absence_date_start, end=existing_absence.absence_date_end)

                # Calculate overlap between new absence and existing absence
                delta = (min(absence_period.end, existing_absence_period.end) -max(absence_period.start, existing_absence_period.start)).days + 1

                overlap = max(0, delta) # Ensure overlap is not negative

                if overlap > NO_ABSENCES:
                    valid = False
                    break
            
            if valid:
                absence.save()
                return redirect("/")
            else:
                return render(request, "ap_app/add_absence.html", {
                    "form": form,
                    "message": "The absence conflicts with an existing absence",
                    "message_type": "is-danger"
                })

    else: # GET request
        form = AbsenceForm(user=request.user)
        # Allow users to edit others absence if they have permission
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
    
    content = {"form": form}
    return render(request, "ap_app/add_absence.html", content)

#Add an absence when clicking on the calendar
@login_required
def click_add(request):
    if request.method == "POST":
        json_data=json.loads(request.body)
        if UserProfile.objects.filter(user__username=json_data["username"]).exists():
            perm_list = UserProfile.objects.filter(user__username=json_data["username"])[0].edit_whitelist.all()
        else:
            perm_list = [UserProfile.objects.get(user=request.user)]
        if request.user in perm_list:
            date = datetime.strptime(json_data["date"], "%Y-%m-%d").date()
            #This will add a half
            if json_data["half_day"]:
                absence = Absence()
                absence.absence_date_start = json_data['date']
                absence.absence_date_end = json_data['date']
                absence.Target_User_ID_id = User.objects.get(username=json_data["username"]).id
                absence.User_ID = request.user
                if json_data["half_day_time"] == "M":
                    absence.half_day = "MORNING"
                elif json_data["half_day_time"] == "A":
                    absence.half_day = "AFTERNOON"
                absence.save()
                return JsonResponse({})
            else:
                def non_connected():
                    absence = Absence()
                    absence.absence_date_start = json_data['date']
                    absence.absence_date_end = json_data['date']
                    absence.Target_User_ID_id = User.objects.get(username=json_data["username"]).id
                    absence.User_ID = request.user
                    absence.save()
                    return absence
                date = datetime.strptime(json_data["date"], "%Y-%m-%d").date()
                absence = None
                if date - timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_end", flat=True) \
                    and date + timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_start", flat=True):
                    ab_1 = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_start=date+timedelta(days=1))[0]
                    ab_2 = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_end=date-timedelta(days=1))[0]
                    if ab_1.half_day == "NORMAL" and ab_2.half_day == "NORMAL":
                        absence = Absence()
                        absence.absence_date_start = ab_2.absence_date_start
                        absence.absence_date_end = ab_1.absence_date_end
                        absence.Target_User_ID_id = User.objects.get(username=json_data["username"]).id
                        absence.User_ID = request.user
                        ab_1.delete()
                        ab_2.delete()
                        absence.save()
                    else:
                        absence = non_connected()

                elif date - timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_start", flat=True):
                    a = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_start=date-timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_end = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date + timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_end", flat=True):
                    a = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_end=date+timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_start = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date - timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_end", flat=True):
                    a =Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_end=date-timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_end = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date + timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_start", flat=True):
                    a = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_start=date+timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_start = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                else:
                    absence = non_connected()

                return JsonResponse({'start_date': absence.absence_date_start, 'end_date': absence.absence_date_end, 'taget_id': absence.Target_User_ID.username, 'user_id': absence.User_ID.username})
        else:
            return JsonResponse({})
    else:
        return HttpResponse('404')

@login_required
def click_remove(request):
    if request.method == "POST":
        data = json.loads(request.body)
        date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        if UserProfile.objects.filter(user__username=data["username"]).exists():
            perm_list = UserProfile.objects.filter(user__username=data["username"])[0].edit_whitelist.all()
        else:
            perm_list = [UserProfile.objects.get(user=request.user)]

        if request.user in perm_list:
            #Add an exception for recurring absence
            if data["absence_type"] == "R":
                exception = RecurringException()
                exception.Target_User_ID = User.objects.get(username=data["username"])
                exception.User_ID = request.user
                exception.Exception_Start = data["date"]
                exception.Exception_End = data["date"]
                exception.save()
            else:
                #Remove absence if start date and end date is the same
                if date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_start", flat=True) \
                    and date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_end", flat=True):
                    absence = Absence.objects.filter(Target_User_ID__username=data["username"], absence_date_start=date, absence_date_end=date)[0]
                    absence.delete()
                #Change absence start date if current start date removed
                elif date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_start", flat=True):
                    absence = Absence.objects.filter(Target_User_ID__username=data["username"], absence_date_start=date)[0]
                    absence.absence_date_start = date + timedelta(days=1)
                    absence.save()
                #Change absence end date if current end date removed
                elif date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_end", flat=True):
                    absence = Absence.objects.filter(Target_User_ID__username=data["username"], absence_date_end=date)[0]
                    absence.absence_date_end = date - timedelta(days=1)
                    absence.save()
                else:
                    for absence in Absence.objects.filter(Target_User_ID__username=data["username"]):
                        start_date = absence.absence_date_start
                        end_date = absence.absence_date_end
                        if date > start_date and date < end_date:
                            ab_1 = Absence()
                            ab_1.absence_date_start = start_date
                            ab_1.absence_date_end = date - timedelta(days=1)
                            ab_1.Target_User_ID_id = User.objects.get(username=data["username"]).id
                            ab_1.User_ID = request.user

                            ab_2 = Absence()
                            ab_2.absence_date_start = date + timedelta(days=1)
                            ab_2.absence_date_end = end_date
                            ab_2.Target_User_ID_id = User.objects.get(username=data["username"]).id
                            ab_2.User_ID = request.user

                            absence.delete()
                            ab_1.save()
                            ab_2.save()

        return JsonResponse({"start_date": data["date"]})
    else:
        return HttpResponse("404")
