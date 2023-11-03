
import datetime
import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import *
from .models import (Absence, RecurringAbsences,
                     UserProfile)


#Add an absence when clicking on the calendar
@login_required
def click_add(request):
    if request.method == "POST":
        json_data=json.loads(request.body)
        perm_list = UserProfile.objects.filter(id=json_data["id"])[0].edit_whitelist.all()
        if request.user in perm_list:
            date = datetime.datetime.strptime(json_data["date"], "%Y-%m-%d").date()
            #This will add a half
            if json_data["half_day"] == True:
                absence = Absence()
                absence.absence_date_start = json_data['date']
                absence.absence_date_end = json_data['date']
                absence.Target_User_ID_id = json_data["id"]
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
                    absence.Target_User_ID_id = json_data["id"]
                    absence.User_ID = request.user
                    absence.save()
                    return absence
                date = datetime.datetime.strptime(json_data["date"], "%Y-%m-%d").date()
                absence = None
                if date - timedelta(days=1) in Absence.objects.filter(Target_User_ID_id=json_data["id"]).values_list("absence_date_end", flat=True) \
                    and date + timedelta(days=1) in Absence.objects.filter(Target_User_ID_id=json_data["id"]).values_list("absence_date_start", flat=True):
                    ab_1 = Absence.objects.filter(Target_User_ID_id=json_data["id"], absence_date_start=date+timedelta(days=1))[0]
                    ab_2 = Absence.objects.filter(Target_User_ID_id=json_data["id"], absence_date_end=date-timedelta(days=1))[0]
                    if ab_1.half_day == "NORMAL" and ab_2.half_day == "NORMAL":
                        absence = Absence()
                        absence.absence_date_start = ab_2.absence_date_start
                        absence.absence_date_end = ab_1.absence_date_end
                        absence.Target_User_ID_id = json_data["id"]
                        absence.User_ID = request.user
                        ab_1.delete()
                        ab_2.delete()
                        absence.save()
                    else:
                        absence = non_connected()
                    
                elif date - timedelta(days=1) in Absence.objects.filter(Target_User_ID_id=json_data["id"]).values_list("absence_date_start", flat=True):
                    a = Absence.objects.filter(Target_User_ID_id=json_data["id"], absence_date_start=date-timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_end = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date + timedelta(days=1) in Absence.objects.filter(Target_User_ID_id=json_data["id"]).values_list("absence_date_end", flat=True):
                    a = Absence.objects.filter(Target_User_ID_id=json_data["id"], absence_date_end=date+timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_start = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date - timedelta(days=1) in Absence.objects.filter(Target_User_ID_id=json_data["id"]).values_list("absence_date_end", flat=True):
                    a =Absence.objects.filter(Target_User_ID_id=json_data["id"], absence_date_end=date-timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_end = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date + timedelta(days=1) in Absence.objects.filter(Target_User_ID_id=json_data["id"]).values_list("absence_date_start", flat=True):
                    a = Absence.objects.filter(Target_User_ID_id=json_data["id"], absence_date_start=date+timedelta(days=1))[0]
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
        date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
        #Remove absence if start date and end date is the same
        if date in Absence.objects.filter(Target_User_ID_id=data["id"]).values_list("absence_date_start", flat=True) \
            and date in Absence.objects.filter(Target_User_ID_id=data["id"]).values_list("absence_date_end", flat=True):
            absence = Absence.objects.filter(Target_User_ID_id=data["id"], absence_date_start=date, absence_date_end=date)[0]
            absence.delete()
        #Change absence start date if current start date removed
        elif date in Absence.objects.filter(Target_User_ID_id=data["id"]).values_list("absence_date_start", flat=True):
            absence = Absence.objects.filter(Target_User_ID_id=data["id"], absence_date_start=date)[0]
            absence.absence_date_start = date + timedelta(days=1)
            absence.save()
        #Change absence end date if current end date removed
        elif date in Absence.objects.filter(Target_User_ID_id=data["id"]).values_list("absence_date_end", flat=True):
            absence = Absence.objects.filter(Target_User_ID_id=data["id"], absence_date_end=date)[0]
            absence.absence_date_end = date - timedelta(days=1)
            absence.save()
        else:
            for absence in Absence.objects.filter(Target_User_ID_id=data["id"]):
                start_date = absence.absence_date_start
                end_date = absence.absence_date_end
                if date > start_date and date < end_date:
                    ab_1 = Absence()
                    ab_1.absence_date_start = start_date
                    ab_1.absence_date_end = date - timedelta(days=1)
                    ab_1.Target_User_ID_id = data["id"]
                    ab_1.User_ID = request.user

                    ab_2 = Absence()
                    ab_2.absence_date_start = date + timedelta(days=1)
                    ab_2.absence_date_end = end_date
                    ab_2.Target_User_ID_id = data["id"]
                    ab_2.User_ID = request.user

                    absence.delete()
                    ab_1.save()
                    ab_2.save()

        return JsonResponse({"start_date": data["date"]})
    else:
        return HttpResponse("404")
    
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