#index
#privacy_page
#add
#details_page
#deleteuser
#profile_settings
#add_user
#get_region_data
#set_region
#click_add
#click_remove

import calendar
import datetime
import json
import holidays
import pycountry
import pandas as pd
import requests
import environ
import hashlib
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import Lower
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from .teams import *
from .objects import *
from .teams import *
from .calendarview import *

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile, ColourScheme, ColorData)

from .switch_permissions_utils import check_for_lingering_switch_perms

User = get_user_model()


def index(request) -> render:
    """Branched view.                       \n
    IF NOT Logged in: returns the home page \n
    ELSE: returns the calendar page"""

    # If its the first time a user is logging in, will create an object of UserProfile model for that user.
    if not request.user.is_anonymous:
        if not obj_exists(request.user):
            user = find_user_obj(request.user)
            user.edit_whitelist.add(request.user)
        else:
            user = UserProfile.objects.filter(user=request.user)[0]
            user.edit_whitelist.add(request.user)
        # Until the accepted_policy field is checked, the user will keep being redirected to the policy page to accept
        if not user.accepted_policy:
            return privacy_page(request, to_accept=True)

    # Change: If user is logged in, will be redirected to the calendar
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user=request.user)
        user.edit_whitelist.add(request.user)
        return main_calendar(request)
    return render(request, "ap_app/index.html")


def privacy_page(request, to_accept=False) -> render:
    # If true, the user accepted the policy
    if request.method == "POST":
        user = find_user_obj(request.user)
        user.accepted_policy = True
        user.save()

    # If the user has been redirected from home page to accepted policy
    elif to_accept:
        return render(
            request, "registration/accept_policy.html", {"form": AcceptPolicyForm()}
        )
    else:
        # Viewing general policy page - (Without the acceptancy form)
        return render(request, "ap_app/privacy.html")
    return main_calendar(request)

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def example(request):
    if request.method == "POST":
        form = AbsenceForm(
            request.POST,
            user=request.user,
            initial={
                "start_date": datetime.datetime.now(),
                "end_date": lambda: datetime.datetime.now().date()
                + datetime.timedelta(days=1),
            },
        )
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

        if form.is_valid():
            obj = Absence()
            obj.absence_date_start = request.POST.get("start_date")
            obj.absence_date_end = request.POST.get("end_date")
            obj.absence_date_start = form.cleaned_data["start_date"]
            obj.absence_date_end = form.cleaned_data["end_date"]
            obj.request_accepted = False  # TODO
            obj.User_ID = request.user
            obj.Target_User_ID = form.cleaned_data["user"].user
            message = "Absence successfully created"
            msg_type = "is-success"
            absence_valid = True
            for x in Absence.objects.filter(User_ID=request.user.id):
                if (obj.absence_date_start >= x.absence_date_start and obj.absence_date_end <= x.absence_date_end) \
                    or x.absence_date_start == obj.absence_date_end or x.absence_date_end == x.absence_date_start:
                        message = "Absence already created"
                        msg_type = "is-danger"
                        absence_valid = False
            if absence_valid:
                obj.save()
            return render(
                request,
                "ap_app/add_absence.html",
                {
                    "form": form,
                    "message": message,
                    "message_type": msg_type,
                    "add_absence_active": True,
                },
            )
            # redirect to success page
    else:
        form = AbsenceForm(user=request.user)
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

    content = {"form": form, "add_absence_active": True}
    return render(request, "ap_app/add_absence.html", content)

@login_required
def details_page(request) -> render:
    """returns details web page"""
    # TODO: get employee details and add them to context
    context = {"employee_dicts": ""}
    return render(request, "ap_app/Details.html", context)

@login_required
def deleteuser(request):
    """delete a user account"""
    if request.method == "POST":
        delete_form = DeleteUserForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("index")
    else:
        delete_form = DeleteUserForm(instance=request.user)

    context = {"delete_form": delete_form}

    return render(request, "registration/delete_account.html", context)

@login_required
def profile_settings(request:HttpRequest) -> render:
    """returns the settings page"""

    if len(request.POST) > 0:
        if request.POST.get("firstName") != "" and request.POST.get("firstName") != request.user.first_name:
            request.user.first_name = request.POST.get("firstName")
            request.user.save()
        if request.POST.get("lastName") != "" and request.POST.get("lastName") != request.user.last_name:
            request.user.last_name = request.POST.get("lastName")
            request.user.save()
        if request.POST.get("email") != request.user.email:
            request.user.email = request.POST.get("email")
            request.user.save()

    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")
    
    if len(request.POST) > 0:
        region = request.POST.get("region")
        region_code = pycountry.countries.get(name=region).alpha_2
        if region_code != userprofile.region:
            userprofile.region = region_code
        if request.POST.get("privacy") == None:
            userprofile.privacy = False
        elif request.POST.get("privacy") == "on":
            userprofile.privacy = True

        if request.POST.get("teams") == None:
            userprofile.external_teams = False
        elif request.POST.get("teams") == "on":
            userprofile.external_teams = True
        
        userprofile.save()
    
    country_data = get_region_data()
    country_name = pycountry.countries.get(alpha_2=userprofile.region).name

    colour_data = []
    for scheme in ColourScheme.objects.all():
        colour = {}
        data = ColorData.objects.filter(user=request.user, scheme=scheme)
        colour["name"] = scheme.name
        if data.exists():
            colour["colour"] = data[0].color
            colour["enabled"] = data[0].enabled
        else:
            colour["colour"] = scheme.default
            colour["enabled"] = True

        colour_data.append(colour)

    privacy_status = userprofile.privacy
    teams_status = userprofile.external_teams
    context = {"userprofile": userprofile, "data_privacy_mode": privacy_status, "external_teams": teams_status,
               "current_country": country_name, **country_data, "colours": colour_data}
    
    # DEBUG CODE #
    print("Bob:")
    check_for_lingering_switch_perms("Bob")
    print("Billy:")
    check_for_lingering_switch_perms("Billy")
    print("Brian:")
    check_for_lingering_switch_perms("Brian")
    # DEBUG CODE #

    return render(request, "ap_app/settings.html", context)

def update_colour(request:HttpRequest):
    if request.method == "POST":
        default = ColourScheme.objects.get(name=request.POST["name"])
        data = ColorData.objects.filter(user=request.user, scheme__name=request.POST["name"])
        if data.exists():
            update_data = ColorData.objects.get(id=data[0].id)
            if request.POST["enabled"] == 'True':
                update_data.enabled = True
            else:
                update_data.enabled = False
            update_data.color = request.POST["colour"]
            update_data.save()
        else:
            print(request.POST)
            if request.POST["colour"] != default.default or request.POST["enabled"] != 'True':
                print("Created colour data")
                newData = ColorData()
                if request.POST["enabled"] == 'True':
                    newData.enabled = True
                else:
                    newData.enabled = False
                newData.scheme = default
                newData.color = request.POST["colour"]
                newData.user = request.user
                newData.save()
    
    return redirect('profile_settings')

@login_required
def add_user(request) -> render:
    data=json.loads(request.body)
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")

    if request.method == "POST":
        username = data["username"]

        try:
            user = User.objects.get(username=username)
        except:
            # TODO Create error page
            return redirect("/")

        userprofile.edit_whitelist.add(user)
        user.save()

    return redirect("/profile/settings")

def get_region_data():
    data = {}
    data["countries"] = []
    for country in list(pycountry.countries):
        try:
            holidays.country_holidays(country.alpha_2)
            data["countries"].append(country.name)
        except:
            pass
    
    data["countries"] = sorted(data["countries"])

    return data

@login_required
def set_region(request):

    try:
        userporfile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")

    if request.method == "POST":
        region = request.POST.get("regions")
        region_code = pycountry.countries.get(name=region).alpha_2
        if (region_code != userporfile.region):
            userporfile.region = region_code
            userporfile.save()

    return redirect("/profile/settings")

#JC - Calendar view using the API

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
            date = datetime.datetime.strptime(json_data["date"], "%Y-%m-%d").date()
            #This will add a half
            if json_data["half_day"] == True:
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
                date = datetime.datetime.strptime(json_data["date"], "%Y-%m-%d").date()
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
        date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
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
