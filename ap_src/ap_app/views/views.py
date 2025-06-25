"""
A module for generic views that do not make up specific functionality.

Usually these views are for pages that would be found across lots of websites, such as:

- Privacy Policy Page
- User Settings Page
- Error Pages
"""

import json
import holidays
import pycountry

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from requests import HTTPError, ConnectionError, RequestException

from ..utils.objects import obj_exists, find_user_obj
from .calendarview import main_calendar

from ..forms import AcceptPolicyForm, DeleteUserForm, AbsencePlannerUserCreationForm
from ..models import UserProfile, ColourScheme, ColorData

from ..utils.switch_permissions import (
    check_for_lingering_switch_perms,
    remove_switch_permissions,
)
from ..utils.teams_utils import (
    get_user_token_from_request,
    edit_user_details,
    fetch_user_details,
)
from ..utils.errors import derive_http_error_message, print_messages

User = get_user_model()

@login_required(login_url="/accounts/login")
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
    form_class = AbsencePlannerUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


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
def profile_settings(request: HttpRequest) -> render:
    """
    View that returns the settings page and handles changes to the user's settings.

    This uses the Team App API
    """

    # TODO: Reimplement this validation in a Django form class instead of a view
    # if len(request.POST) > 0:
    #     if request.POST.get("firstName") != "" and request.POST.get("firstName") != request.user.first_name:
    #         request.user.first_name = request.POST.get("firstName")
    #         request.user.save()
    #     if request.POST.get("lastName") != "" and request.POST.get("lastName") != request.user.last_name:
    #         request.user.last_name = request.POST.get("lastName")
    #         request.user.save()
    #     if request.POST.get("email") != request.user.email:
    #         request.user.email = request.POST.get("email")
    #         request.user.save()

    user_token = get_user_token_from_request(request)

    if request.method == "POST":
        error, debug, success = None, None, None
        try:
            edit_user_details(
                user_token=user_token,
                first_name=request.POST.get("firstName"),
                last_name=request.POST.get("lastName"),
                email=request.POST.get("email"),
            )
        except HTTPError as exception:
            error = "Error in editing your details - " + derive_http_error_message(
                exception
            )
        except ConnectionError as exception:
            error = "Error - could not edit your details due to a connection error."
            debug = (
                "Error: Could not connect to the API to edit a user's details. Exception: "
                + str(exception)
            )
        except RequestException as exception:
            error = "Error - could not edit your details due to an unknown error."
            debug = (
                "Error: Could not send a request to the API to edit a user's details. Exception: "
                + str(exception)
            )
        else:
            success = "Edited details successfully."
        finally:
            print_messages(request, success=success, error=error, debug=debug)

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
        if request.POST.get("privacy") is None:
            userprofile.privacy = False
        elif request.POST.get("privacy") == "on":
            userprofile.privacy = True

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

    warning, debug, success = None, None, None
    try:
        user_details = fetch_user_details(user_token)
    except HTTPError as exception:
        warning = (
            "Warning - could not read your details - "
            + derive_http_error_message(exception)
        )
    except ConnectionError as exception:
        warning = "Warning - could not read your details due to a connection error."
        debug = (
            "Error: Could not connect to the API to read a user's details. Exception: "
            + str(exception)
        )
    except RequestException as exception:
        warning = "Warning - could not read your details due to an unknown error."
        debug = (
            "Error: Could not send a request to the API to read a user's details. Exception: "
            + str(exception)
        )
    finally:
        print_messages(request, success=success, warning=warning, debug=debug)
        if warning:
            user_details = False

    context = {
        "user_details": user_details,
        "userprofile": userprofile,
        "data_privacy_mode": privacy_status,
        "current_country": country_name,
        **country_data,
        "colours": colour_data,
    }

    return render(request, "ap_app/settings.html", context)


def update_colour(request: HttpRequest):
    if request.method == "POST":
        default = ColourScheme.objects.get(name=request.POST["name"])
        data = ColorData.objects.filter(
            user=request.user, scheme__name=request.POST["name"]
        )
        if data.exists():
            update_data = ColorData.objects.get(id=data[0].id)
            if request.POST["enabled"] == "True":
                update_data.enabled = True
            else:
                update_data.enabled = False
            update_data.color = request.POST["colour"]
            update_data.save()
        else:
            if (
                request.POST["colour"] != default.default
                or request.POST["enabled"] != "True"
            ):
                newData = ColorData()
                if request.POST["enabled"] == "True":
                    newData.enabled = True
                else:
                    newData.enabled = False
                newData.scheme = default
                newData.color = request.POST["colour"]
                newData.user = request.user
                newData.save()

    return redirect("profile_settings")


@login_required
def add_user(request) -> render:
    data = json.loads(request.body)
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")

    if request.method == "POST":
        username = data["username"]

        try:
            user = User.objects.get(username=username)
        except Exception as exception:
            # TODO Create error page
            print(exception)
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
        except Exception as exception:
            print(exception)
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
        if region_code != userporfile.region:
            userporfile.region = region_code
            userporfile.save()

    return redirect("/profile/settings")


@login_required
def remove_lingering_perms(request):
    """
    Removes lingering switch permissions associated with the user who made the `request`.

    Generally ran when a user leaves a team and we wish to remove any lingering permissions.
    """
    if request.method == "POST":
        username = request.user.username
        user_token = get_user_token_from_request(request)

        result = check_for_lingering_switch_perms(
            username, remove_switch_permissions, user_token
        )
        if result is not None:
            return JsonResponse({"status": "success"})
    # Something failed in the logic for checking and removing switch permissions
    return HttpResponse(status=500)


def Custom404View(request):
    return render(request, "404.html")


def Custom500View(request):
    return render(request, "500.html")


def Custom400View(request):
    return render(request, "400.html")
