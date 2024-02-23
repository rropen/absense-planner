import pandas as pd
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

from .forms import *
from .models import (
                     UserProfile)

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