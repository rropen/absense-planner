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