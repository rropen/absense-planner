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

from .teams import *
from .objects import *
from .teams import *
from .clicks import *

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile)

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