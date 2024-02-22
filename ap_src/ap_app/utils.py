import calendar
import datetime
import json
import holidays
import pycountry
import pandas as pd
import requests
import environ
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
from django.contrib.auth.models import User

from collections import namedtuple

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile, Status)

env = environ.Env()
environ.Env.read_env()


# this check should be activated when the user leaves a team
@login_required
def check_for_lingering_switch_perms(request): # stops users from having switch perms when they don't share any teams
    user_edited = request.user.username
    users_with_perms = grab_users_with_perms(request)
    users_sharing_teams = grab_users_sharing_teams(request)
    print(users_with_perms)
    print(users_sharing_teams)

    for user_with_perms in users_with_perms:
        if user_with_perms not in users_sharing_teams:
            print("Redundant permissions found for", user_with_perms + "!")
    """
    SET user ID whose absences are being edited AS (int) user_ID_edited
    SET user IDs with permission to edit absences AS (list of int) user_IDs_with_perms
    SET user IDs who are in the same team as user_ID_edited AS (list of int) user_IDs_sharing_teams

    IF user_ID_edited_leave_team THEN
    FOR EACH (int) user_ID_with_perms FROM (list) user_IDs_with_perms DO
        IF user_ID_with_perms NOT IN user_IDs_sharing_teams THEN remove_permissions
    END FOREACH
    END IF
    """

@login_required
def grab_users_sharing_teams(request):
    response = requests.get(env("TEAM_DATA_URL") + "api/teams/?username={}".format(request.user.username))
    teams = response.json()

    users_sharing_teams = []
    for team_index in teams:
        for member in team_index["team"]["members"]:
            username = member["user"]["username"]
            #username = "yes"
            users_sharing_teams.append(username)
    users_sharing_teams = set(users_sharing_teams)

    return users_sharing_teams

@login_required
def grab_users_with_perms(request):
    current_username = request.user.username
    user_profiles_with_perms = UserProfile.objects.filter(edit_whitelist__username=current_username)
    user_ids_with_perms = user_profiles_with_perms.values_list("user_id", flat=True)
    user_ids_with_perms = list(user_ids_with_perms)

    usernames_with_perms = []
    for user_id in user_ids_with_perms:
        user_matching_user_id = User.objects.filter(id=user_id)
        username_matching_user_id = user_matching_user_id.values_list("username", flat=True)
        username_matching_user_id = str(username_matching_user_id[0])
        usernames_with_perms.append(username_matching_user_id)
    
    return usernames_with_perms