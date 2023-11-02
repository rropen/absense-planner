import calendar
import datetime
import json
import holidays
import pycountry
import pandas as pd
import requests
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import Lower
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.models import User

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile, Status)

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
        return all_calendar(request)
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
    return all_calendar(request)


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def teams_dashboard(request) -> render:
    rels = Relationship.objects.order_by(Lower("team__name")).filter(
        user=request.user, status=Status.objects.get(status="Active")
    )
    invite_rel_count = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Invited")
    ).count()

    r = requests.get("http://localhost:8000/api/teams/?username={}".format(request.user.username))
    if r.status_code == 200:
        if len(r.json()) == 0 :
            external_teams_data = False
        else:
            external_teams_data = r.json()
    else:
        external_teams_data = False
    return render(
        request,
        "teams/dashboard.html",
        {"rels": rels, "invite_count": invite_rel_count, "external_teams": external_teams_data, "teamspage_active": True},
    )

def obj_exists(user):
    """Determines if a user has a 'UserProfile' Object"""
    objs = UserProfile.objects.filter(user=user)
    if objs.count() == 0:
        return False

    return True

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
        return redirect("/calendar/1")

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
    
def is_member(user, team_id) -> bool:
    """ Determines if the user is a member of the team before accessing its contents """

    team = Relationship.objects.filter(team=Team.objects.get(id=team_id))

    # Boolean determines if viewer is in this team
    for rel in team:
        if rel.user == user:
            return True

    # Else user has changed URL & is attempting to view other teams content
    return False