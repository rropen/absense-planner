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

User = get_user_model()



def index(request):
    """Branched view.
    IF NOT Logged in: returns the home page
    ELSE: returns the calendar page"""

    # If its the first time a user is logging in, will create an object of UserProfile model for that user.
    if not request.user.is_anonymous:
        if not obj_exists(request.user):
            user = find_user_obj(request.user)
            user.edit_whitelist.add(request.user)
        else:
            user = UserProfile.objects.filter(user=request.user)[0]
            user.edit_whitelist.add(request.user)

        if not user.accepted_policy:
            return privacy_page(request, to_accept=True)

    # Change: If user is logged in, will be redirected to the calendar
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user=request.user)
        user.edit_whitelist.add(request.user)
        return all_calendar(request)
    return render(request, "ap_app/index.html")


def privacy_page(request, to_accept=False):
    if request.method == "POST":
        user = find_user_obj(request.user)
        user.accepted_policy = True
        user.save()

    # If the user has been redirected from home page to accepted policy
    elif to_accept:
        return render(request, "registration/accept_policy.html", {"form": AcceptPolicyForm()})
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
    
    try:
        r = requests.get("http://localhost:8000/api/teams/?username={}".format(request.user.username))
    except:
        return render(
        request,
        "teams/dashboard.html",
        {"rels": rels, "invite_count": invite_rel_count, "external_teams": False, "teamspage_active": True})
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


@login_required
def create_team(request) -> render:
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.name_similarity():
            # TODO: write code to tell the user that their team name is similar and to give them
            # options to change the team name.
            return HttpResponse(
                "Debug: Did not create form because the name is too similar to another team name"
            )

        if form.is_valid():
            form.save()
            # Gets the created team and "Owner" Role and creates a Link between
            # the user and their team
            created_team = Team.objects.get(name=form.cleaned_data["name"])
            assign_role = Role.objects.get(role="Owner")
            Relationship.objects.create(
                user=request.user,
                team=created_team,
                role=assign_role,
                status=Status.objects.get(status="Active"),
            )
            return redirect("/teams/", {"message": "Team successfully created."})
    else:
        form = CreateTeamForm()
    teams = Team.objects.all()
    existing_teams = ""
    existing_teams_ids = ""
    for i, team in enumerate(teams):
        existing_teams += team.name
        existing_teams_ids += str(team.id)
        if i != len(teams) - 1:
            existing_teams += ","
            existing_teams_ids += ","

    return render(
        request,
        "teams/create_team.html",
        {
            "form": form,
            "existing_teams": existing_teams,
            "existing_teams_ids": existing_teams_ids,
        },
    )


@login_required
def join_team(request) -> render:
    """Renders page with all teams the user is not currently in"""
    user_teams = []
    all_user_teams = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Active")
    )
    for teams in all_user_teams:
        user_teams.append(teams.team)
    all_teams = Team.objects.all().exclude(relationship__user=request.user.id)
    all_teams_filtered = []

    # Filtering by team name
    if "teamName" in request.GET:
        for team in all_teams:
            if request.GET["teamName"].lower() in team.name.lower():
                all_teams_filtered.append(team)
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
def team_misc(request, id):
    """Teams Miscellaneous/Notes page"""
    if is_member(user=request.user, team_id=id):
        team = Team.objects.get(id=id)

        notes = CreateTeamForm(instance=team)

        # TODO: Add a field to each team with a notes section - (for now it's just the teams description)

        if "value" in request.GET:
            team.notes = request.GET["value"]
            team.save()

        desc = team.description
        notes = team.notes

        return render(
            request, "teams/misc.html", {"team": team, "desc": desc, "notes": notes}
        )
    return redirect("dashboard")


@login_required
def team_settings(request, id):
    """Checks to see if user is the owner and renders the Setting page"""
    team = Team.objects.get(id=id)
    
    if is_owner(user=request.user, team_id=id): 
        all_pending_relations = Relationship.objects.filter(
            team=id, status=Status.objects.get(status="Pending")
        )
        return render(
            request,
            "teams/settings.html",
            {
                "user": request.user,
                "team": team,
                "pending_rels": all_pending_relations,
                "Team_users": team.users,
                "member": Role.objects.get(role="Member"),
                "coowner": Role.objects.get(role="Co-Owner"),
                "follower": Role.objects.get(role="Follower"),
                "owner": Role.objects.get(role="Owner"),
            },
        )
    return redirect("dashboard")

def edit_team_member_absence(request, id, user_id) -> render:
    """Checks to see if user is the owner and renders the Edit absences page for that user"""
    team = Team.objects.get(id=id)
        
    if is_owner(user=request.user, team_id=id):    
        all_pending_relations = Relationship.objects.filter(
            team=id, status=Status.objects.get(status="Pending")
        )
        target_user = User.objects.get(id=user_id)
        absences = Absence.objects.filter(Target_User_ID=target_user.id)
        rec_absences = text_rules(target_user)
        return render(
            request,
            "teams/edit_absences.html",
            {
                "team": team,
                "user": target_user,
                "absences": absences,
                "recurring_absences": rec_absences,
            },
        )
    return redirect("dashboard")


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
