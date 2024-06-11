import calendar
import datetime
import json
import holidays
import pycountry
import pandas as pd
import requests
import environ
import pytz  # from the 'timezone' section
import hashlib  # from the 'develop' section
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
from .calendarview import *

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile, Status, ColourScheme, ColorData)  # combined imports

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


@login_required
def details_page(request) -> render:
    """returns details web page"""
    # TODO: get employee details and add them to context
    context = {"employee_dicts": ""}
    return render(request, "ap_app/Details.html", context)


def get_date_data(
    region,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    #  uses a dictionary to get all the data needed for the context
    #  and concatenates it to form the full context with other dictionaries
    data = {}
    data["current_year"] = datetime.datetime.now().year
    data["current_month"] = datetime.datetime.now().strftime("%B")
    data["current_month_num"] = datetime.datetime.now().month
    data["today"] = datetime.datetime.now().day
    data["year"] = year
    data["month"] = month
    data["next_current_year"] = datetime.datetime.now().year + 1
    data["next_second_year"] = datetime.datetime.now().year + 2
    
    start_date, end_date = "2022-07-03", "2024-07-03"
 
    data["month_list"] = pd.period_range(start=start_date, end=end_date, freq='M')
    data["month_list"] = [month.strftime("%B %Y") for month in data["month_list"]]

    data["selected_date"] = datetime.date(int(data["year"]), datetime.datetime.strptime(month, "%B").month, 1).strftime("%B %Y")

    data["day_range"] = range(
        1,
        calendar.monthrange(
            data["year"], datetime.datetime.strptime(month, "%B").month
        )[1]
        + 1,
    )
    data["day_range_num"] = len(list(data["day_range"])) + 1
    data["month_num"] = datetime.datetime.strptime(month, "%B").month

    data["previous_month"] = "December"
    data["next_month"] = "January"
    data["previous_year"] = year - 1
    data["next_year"] = year + 1

    # as the month number resets every year try and except statements
    # have to be used as at the end and start of a year
    # the month cannot be calculated by adding or subtracting 1
    # as 13 and 0 are not datetime month numbers
    try:
        data["next_month"] = datetime.datetime.strptime(
            str((datetime.datetime.strptime(data["month"], "%B")).month + 1), "%m"
        ).strftime("%B")

    except ValueError:
        pass
    try:
        data["previous_month"] = datetime.datetime.strptime(
            str((datetime.datetime.strptime(data["month"], "%B")).month - 1), "%m"
        ).strftime("%B")
    except ValueError:
        pass

    # calculating which days are weekends to mark them easier in the html
    data["days_name"] = []
    for day in data["day_range"]:
        date = f"{day} {month} {year}"
        date = datetime.datetime.strptime(date, "%d %B %Y")
        date = date.strftime("%A")[0:2]
        data["days_name"].append(date)

    data["weekend_list"] = []
    for day in data["day_range"]:
        date = f"{day} {month} {year}"
        date = datetime.datetime.strptime(date, "%d %B %Y")
        date = date.strftime("%A")[0:2]
        if (date == "Sa" or date == "Su"):
            data["weekend_list"].append(day)

    data["bank_hol"] = []
    for h in holidays.country_holidays(region, years=year).items():
        if (h[0].month == data["month_num"]):
            data["bank_hol"].append(h[0].day)
        
    return data




def get_absence_data(users, user_type):
    data = {}
    absence_content = []
    total_absence_dates = {}
    total_half_dates = {}
    total_recurring_dates = {}
    all_absences = {}
    delta = datetime.timedelta(days=1)

    for user in users:
        # all the absences for the user
        if user_type == 1:
            user_username = user.user.username
        else:
            user_username = user.username

        absence_info = Absence.objects.filter(Target_User_ID__username=user_username)
        total_absence_dates[user_username] = []
        total_recurring_dates[user_username] = []
        total_half_dates[user_username] = []
        all_absences[user_username] = []

        # if they have any absences
        if absence_info:
            # mapping the absence content to keys in dictionary
            for x in absence_info:
                absence_id = x.ID
                absence_date_start = x.absence_date_start
                absence_date_end = x.absence_date_end
                dates = absence_date_start
                if x.half_day == "NORMAL":
                    while dates <= absence_date_end:
                        total_absence_dates[user_username].append(dates)
                        dates += delta
                else:
                    total_half_dates[user_username].append(
                        {
                            "date": absence_date_start,
                            "type": x.half_day
                        }
                    )

                absence_content.append(
                    {
                        "ID": absence_id,
                        "absence_date_start": absence_date_start,
                        "absence_date_end": absence_date_end,
                        "dates": total_absence_dates[user_username],
                    }
                )

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            all_absences[user_username] = absence_content

        recurring = RecurringAbsences.objects.filter(Target_User_ID__username=user_username)

        if recurring:
            for recurrence_ in recurring:
                dates = recurrence_.Recurrences.occurrences(
                    dtend=datetime.datetime.strptime(
                        str(datetime.datetime.now().year + 2), "%Y"
                    )
                )

                for x in list(dates)[:-1]:
                    time_const = "23:00:00"
                    time_var = datetime.datetime.strftime(x, "%H:%M:%S")
                    if time_const == time_var:
                        x += timedelta(days=1)
                    total_recurring_dates[user_username].append(x)
                # TODO: add auto deleting for recurring absences once last date of absences in before now
                # if x < datetime.datetime.now():
                #    pass

    data["recurring_absence_dates"] = total_recurring_dates
    data["all_absences"] = all_absences
    data["absence_dates"] = total_absence_dates
    data["half_days_data"] = total_half_dates
    data["users"] = users
    return data


@login_required
def team_calendar(
    request,
    id,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    if is_member(request.user, id):

        # Get acceptable date - (NOTHING BELOW now - 12months)
        date = check_calendar_date(year, month)
        if date:
            month = date.strftime("%B")
            year = date.year

        try:
            userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
        except IndexError:
            return redirect("/")

        data_1 = get_date_data(userprofile.region, month, year)

        users = Relationship.objects.all().filter(
            team=id, status=Status.objects.get(status="Active")
        )

        data_2 = get_absence_data(users, 1)

        team = Team.objects.get(id=id)

        # Filtering users by privacy
        filtered_users = []
        viewer = data_2["users"].get(user=request.user)
        if str(viewer.role) == "Follower":
            # Than hide data of users with privacy on
            for user in data_2["users"]:
                user_profile = UserProfile.objects.get(user=user.user)
                if not user_profile.privacy:
                    filtered_users.append(user)

                else:
                    # For pop-up to inform viewer that there are hidden users
                    data_2.update({"hiding_users": True})

            data_2["users"] = filtered_users

        # Gets filtered users by filtering system on page
        filtered_users = get_filter_users(
            request, [user.user for user in data_2["users"]]
        )

        actual_filtered_users = []
        for user in data_2["users"]:
            if user.user in filtered_users:
                actual_filtered_users.append(user)

        # Reconstructs users list to be in desired form for template - (QuerySet of relationships)
        data_2["users"] = actual_filtered_users

        user_in_teams = []
        for rel in Relationship.objects.filter(team=team):
            user_in_teams.append(rel.user.id)

        data_3 = {
            "owner": Role.objects.all()[0],
            "Sa": "Sa",
            "Su": "Su",
            "current_user": Relationship.objects.get(user=request.user, team=team),
            "team": team,
            "all_users": User.objects.all().exclude(id__in=user_in_teams),
            "team_count": Relationship.objects.filter(
                team=team.id, status=Status.objects.get(status="Active")
            ).count(),
        }

        context = {**data_1, **data_2, **data_3}

        return render(request, "teams/calendar.html", context)

    return redirect("dashboard")


@login_required
def all_calendar(
    request,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    # Get acceptable date - (NOTHING BELOW now - 12months)
    date = check_calendar_date(year, month)
    if date:
        month = date.strftime("%B")
        year = date.year
    
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        return redirect("/")
    
    if userprofile.external_teams:
        try:
            if requests.get(env("TEAM_DATA_URL") + "api/teams/?username={}".format(request.user.username)).status_code == 200:
                return redirect("/calendar/1")
        except:
            print("Failed to load api")


    data_1 = get_date_data(userprofile.region, month, year)
    
    current_month = data_1["current_month"]
    current_year = data_1["current_year"]
    current_day = datetime.datetime.now().day
    date = f"{current_day} {current_month} {current_year}"
    date = datetime.datetime.strptime(date, "%d %B %Y")


    all_users = []
    all_users.append(request.user)

    user_relations = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Active")
    )
    hiding_users = False


    for index, relation in enumerate(user_relations):
        rels = Relationship.objects.filter(
            team=relation.team, status=Status.objects.get(status="Active")
        )

        # Finds the viewers role in the team
        for user in rels:
            if user.user == request.user:
                viewers_role = Role.objects.get(id=user.role_id)

        for rel in rels:
            if rel.user not in all_users:
                if viewers_role.role == "Follower":
                    # Than hide users data who have privacy on

                    user_profile = UserProfile.objects.get(user=rel.user)
                    if not user_profile.privacy:
                        # If user hasn't got their data privacy on
                        all_users.append(rel.user)
                    else:
                        # Used to inform user on calendar page if there are hiden users
                        hiding_users = True

                else:
                    # Only followers cannot view those who have privacy set for their data. - (Members & Owners can see the data)
                    all_users.append(rel.user)

    # Filtering
    filtered_users = get_filter_users(request, all_users)

    data_2 = get_absence_data(all_users, 2)

    data_3 = {"Sa": "Sa", "Su": "Su", "users_filter": filtered_users}

  
    grid_calendar_month_values = list(data_1["day_range"])
    # NOTE: This will select which value to use to fill in how many blank cells where previous month overrides prevailing months days. 
    # This is done by finding the weekday value for the 1st day of the month. Example: "Tu" will require 1 blank space/cell.
    for i in range({"Mo":0, "Tu":1, "We":2, "Th":3, "Fr":4, "Sa":5, "Su":6}[data_1["days_name"][0]]):
        grid_calendar_month_values.insert(0, -1)


    context = {
        **data_1,
        **data_2,
        **data_3,
        "users_hidden": hiding_users,
        "home_active": True,
        
        # Grid-Calendars day values  
        "detailed_calendar_day_range":grid_calendar_month_values,
     
        
    }
   

    return render(request, "ap_app/calendar.html", context)

@login_required
def set_calendar_month(request):
    if request.method == "POST":
        month = request.POST.get('month_names')
        
        split = month.split()

        month = split[0]

        year = split[1]

        print(month)

    return redirect('all_calendar', month=month, year=year)


def text_rules(user):
    recurring_absences = RecurringAbsences.objects.filter(Target_User_ID=user).values(
        "Recurrences", "ID"
    )
    rec_absences = {}

    for x in recurring_absences:
        absence_ = x["Recurrences"]
        if absence_:
            rec_absences[x["ID"]] = []
        if absence_.exdates:
            for y in absence_.exdates:
                rec_absences[x["ID"]].append(
                    "Excluding Date: " + (y + timedelta(days=1)).strftime("%A,%d %B,%Y")
                )
        if absence_.rdates:
            for y in absence_.rdates:
                rec_absences[x["ID"]].append(
                    "Date: " + (y + timedelta(days=1)).strftime("%A,%d %B,%Y")
                )
        if absence_.rrules:
            for y in absence_.rrules:
                rec_absences[x["ID"]].append("Rule: " + str(y.to_text()))

        if absence_.exrules:
            for y in absence_.exrules:
                rec_absences[x["ID"]].append("Excluding Rule: " + str(y.to_text()))

    return rec_absences


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
def profile_settings(request) -> render:
    """Returns the settings page"""

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
            userprofile: UserProfile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            # Create user profile if it doesn't exist
            userprofile = UserProfile.objects.create(user=request.user)

        region = request.POST.get("region")
        region_code = pycountry.countries.get(name=region).alpha_2
        if region_code != userprofile.region:
            userprofile.region = region_code
            userprofile.save()

        # Update user's privacy and teams settings
        userprofile.privacy = request.POST.get("privacy") == "on"
        userprofile.external_teams = request.POST.get("teams") == "on"
        userprofile.save()

        # Handle timezone selection
        user_timezone = request.POST.get("timezone")
        if user_timezone:
            request.session['user_timezone'] = user_timezone
            userprofile.timezone = user_timezone  # Save the timezone in the UserProfile model
            userprofile.save()
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create user profile if it doesn't exist
        userprofile = UserProfile.objects.create(user=request.user)

    country_data = get_region_data()
    country_name = pycountry.countries.get(alpha_2=userprofile.region).name

    # Retrieve user's timezone from session or default to UTC
    user_timezone = request.session.get('user_timezone', 'UTC')
    
    # Get list of timezone options
    timezones = pytz.all_timezones

    privacy_status = userprofile.privacy
    teams_status = userprofile.external_teams
    context = {
        "userprofile": userprofile, 
        "data_privacy_mode": privacy_status, 
        "external_teams": teams_status,
        "current_country": country_name, 
        **country_data,
        'user_timezone': user_timezone,
        'timezones': timezones
    }
    return render(request, "ap_app/settings.html", context)


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

def find_user_obj(user_to_find):
    """Finds & Returns object of 'UserProfile' for a user
    \n-param (type)User user_to_find
    """
    users = UserProfile.objects.filter(user=user_to_find)
    # If cannot find object for a user, than creates on

    if users.count() <= 0:
        UserProfile.objects.create(user=user_to_find, accepted_policy=False)
        user_found = UserProfile.objects.filter(user=user_to_find)[0]
        user_found.edit_whitelist.add(user_to_find)

    # Users object
    user_found = UserProfile.objects.filter(user=user_to_find)[0]

    return user_found


def obj_exists(user):
    """Determines if a user has a 'UserProfile' Object"""
    objs = UserProfile.objects.filter(user=user)
    if objs.count() == 0:
        return False

    return True


def get_filter_users(request, users) -> list:
    """Used for calendar filtering system - (Returns list of filtered users depending on
    search-bar and 'filter by absence' checkbox"""

    filtered_users = []

    # Filtering by both username & absence
    if "username" in request.GET and "absent" in request.GET:
        # Get username input & limits the length to 50
        name_filtered_by = request.GET["username"][:50]
        for absence in Absence.objects.all():
            user = User.objects.get(id=absence.Target_User_ID.id)
            if user in users:
                username = user.username
                if (
                    absence.Target_User_ID not in filtered_users
                    and name_filtered_by.lower() in username.lower()
                ):
                    filtered_users.append(absence.Target_User_ID)

    # ONLY filtering by username
    elif "username" in request.GET:
        # Name limit is 50
        name_filtered_by = request.GET["username"][:50]
        for user in users:
            # same logic as "icontains", searches through users names & finds similarities
            if name_filtered_by.lower() in user.username.lower():
                filtered_users.append(user)

    # ONLY filtering by absences
    elif "absent" in request.GET:
        for absence in Absence.objects.all():
            user = User.objects.get(id=absence.Target_User_ID.id)
            if user in users and absence.Target_User_ID not in filtered_users:
                filtered_users.append(absence.Target_User_ID)

    # Else, no filtering
    else:
        filtered_users = users

    return filtered_users


def is_member(user, team_id) -> bool:
    """ Determines if the user is a member of the team before accessing its contents """

    team = Relationship.objects.filter(team=Team.objects.get(id=team_id))

    # Boolean determines if viewer is in this team
    for rel in team:
        if rel.user == user:
            return True

    # Else user has changed URL & is attempting to view other teams content
    return False


def is_owner(user, team_id) -> bool:
    """ Determines if the user is an owner of the team """
    
    user_relation = Relationship.objects.get(team=team_id, user=user)
    return (user_relation.role.role == "Owner")


def check_calendar_date(year, month) -> datetime.datetime:
    """ This function will determine if the requested date is acceptable - (NOT before current date - 12 months) """
    # Current year * 12     + current month as num      = amount of months been  
    # requested year * 12   + requested month as num    = 
    
    # If requested date is before "current date - 12 months" than will not accept date
    todays_date = datetime.datetime.now()
    requested_months_amount = (int(year) * 12) + datetime.datetime.strptime(month, "%B").month
    current_months_amount   = (todays_date.year * 12) + todays_date.month 
    months_difference = current_months_amount - requested_months_amount


    if months_difference > 12:
        # Return the most earliest date acceptable - (now - 12 months)
        return datetime.datetime(todays_date.year - 1, todays_date.month, 1)  
    else:
        return None

from django.shortcuts import render

def my_view(request):
    return render(request, "base.html")


def handler404(request, exception):
    context = {}
    response = render(request, "404.html", context=context)
    response.status_code = 404
    return response

def handler500(request):
    context = {}
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response

def handler400(request, exception):
    context = {}
    response = render(request, "400.html", context=context)
    response.status_code = 400
    return response


#JC - Calendar view using the API
@login_required
def api_calendar_view(
    request,
    #JC - These are the default values for the calendar.
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year
):
    
    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        return redirect("/")
    
    if not userprofile.external_teams:
        return redirect("/calendar/0")
    
    #JC - Get API data
    api_data = None
    if request.method == "GET":
        try:
            r = requests.get(env("TEAM_DATA_URL") + "api/teams/?username={}".format(request.user.username))
        except:
            print("API failed to connect")
            return redirect("/")
        if r.status_code == 200:
            api_data = r.json()
        else:
            if r:
                result = r.json()
                if result["code"] == "I":
                    print("Username not found in Team App database.")
                elif result["code"] == "N":
                    print("A username was not provided with the request.")
            else:
                print("Fatal Error")

    date = check_calendar_date(year, month)
    if date:
        month = date.strftime("%B")
        year = date.year

    data_1 = get_date_data(userprofile.region, month, year)
    
    current_month = data_1["current_month"]
    current_year = data_1["current_year"]
    current_day = datetime.datetime.now().day
    date = f"{current_day} {current_month} {current_year}"
    date = datetime.datetime.strptime(date, "%d %B %Y")


    all_users = []
    all_users.append(request.user)

    if api_data:
        for team in api_data:
            for member in team["team"]["members"]:
                retrieved_user = User.objects.filter(username=member["user"]["username"])
                if retrieved_user.exists() and retrieved_user not in all_users:
                    all_users.append(retrieved_user[0])

    data_2 = get_absence_data(all_users, 2)

    data_3 = {"Sa": "Sa", "Su": "Su"}

    grid_calendar_month_values = list(data_1["day_range"])
    # NOTE: This will select which value to use to fill in how many blank cells where previous month overrides prevailing months days. 
    # This is done by finding the weekday value for the 1st day of the month. Example: "Tu" will require 1 blank space/cell.
    for i in range({"Mo":0, "Tu":1, "We":2, "Th":3, "Fr":4, "Sa":5, "Su":6}[data_1["days_name"][0]]):
        grid_calendar_month_values.insert(0, -1)


    context = {
        **data_1,
        **data_2,
        **data_3,
        "home_active": True,
        "api_data": api_data,
    }

    return render(request, "api_pages/calendar.html", context)
