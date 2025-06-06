"""
Contains views that handle team-related logic, connecting to the API whilst utilising team utility functions.

Errors are handled here by passing Django messages up through views to templates so API errors can be displayed to the user.
"""

import environ

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from ..forms import CreateTeamForm
from ..models import Role, UserProfile
from ..utils.teams_utils import retrieve_team_member_data, favourite_team, get_user_token_from_request
from ..utils.switch_permissions import check_for_lingering_switch_perms, remove_switch_permissions

from requests import Session

env = environ.Env()
environ.Env.read_env()
TEAM_APP_API_URL = env("TEAM_APP_API_URL")
TEAM_APP_API_KEY = env("TEAM_APP_API_KEY")
TEAM_APP_API_TIMEOUT = float(env("TEAM_APP_API_TIMEOUT"))

# Use the session object from the Python requests library to send requests and pool the connection resources.
# Without this, the requests sent to the API are EXTREMELY SLOW.
session = Session()

@login_required
def teams_dashboard(request) -> render:
    """
    Renders the view that shows the user a selection of teams they are in with the associated options.
    """
    user_token = get_user_token_from_request(request)

    api_specific_method = request.POST.get("method") # Using .get will not raise an error
    if (api_specific_method == "favourite"):
        try:
            team_id = request.POST["team"]
        except KeyError:
            print("Error: Team ID was not found in request.")
        except Exception as exception:
            print("Error: Cannot obtain Team ID from request. Exception:", exception)
        else:
            favourite_team(user_token, team_id)

    try:
        # Prepare request parameters
        headers = {
            "Authorization": TEAM_APP_API_KEY,
            "User-Token": user_token
        }
        url = TEAM_APP_API_URL + "user/teams/"

        # Send request to Team App API and store in response object
        api_response = session.get(url=url, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
    except:
        return render(
        request,
        "teams/dashboard.html",
        {"teams": False})
    if api_response.status_code == 200:
        if len(api_response.json()) == 0 :
            teams = False
        else:
            teams = api_response.json()
    else:
        teams = False
    return render(
        request,
        "teams/dashboard.html",
        {"teams": teams},
    )

@login_required
def leave_team(request):
    """
    Leaves a team and removes lingering switch permissions.
    """

    username = request.user.username
    user_token = get_user_token_from_request(request)

    url = TEAM_APP_API_URL + "manage/"
    data = {
        "team": request.POST.get("team_id")
    }
    params = {
        "method": "leave"
    }
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }

    api_response = session.post(url=url, data=data, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
    if (api_response.status_code == 200):
        # Remove lingering switch permissions upon success
        check_for_lingering_switch_perms(username, remove_switch_permissions, user_token)

    return redirect(reverse("dashboard")) # Redirect back to the list of joined teams

@login_required
def create_team(request:HttpRequest) -> render:
    if request.method == "POST":
        form = CreateTeamForm(request.POST)

        if form.is_valid():
            # Gets the created team and "Owner" Role and creates a Link between
            # the user and their team.

            # Send a POST request to the API instead of handling the usual model logic,
            # so that the created team is stored on the Team App instead of the Absence Planner.

            user_token = get_user_token_from_request(request)
            
            url = TEAM_APP_API_URL + "teams/"
            data = request.POST # This is the data sent by the user in the CreateTeamForm
            headers = {
                "Authorization": TEAM_APP_API_KEY,
                "User-Token": user_token
            }

            api_response = session.post(url=url, data=data, headers=headers, timeout=TEAM_APP_API_TIMEOUT)

            if api_response.status_code == 200:
                return redirect("/teams/api-calendar/" + str(api_response.json()["id"]))
            elif api_response.status_code == 400:
                context = {"form": form}
                if api_response.json()["name"] != None:
                    context["message"] = "That team name already exists"
                return render(request, "teams/create_team.html", context=context)
    else:
        form = CreateTeamForm()

    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        return redirect("/")

    return render(
        request,
        "teams/create_team.html",
        {
            "form": form,
        },
    )

@login_required
def join_team(request) -> render:
    """Renders page with all teams the user is not currently in and handles joining of specific teams."""
    # Filtering by team name
    
    teams = None
    api_response = None
    user_token = get_user_token_from_request(request)

    try:
        if (request.method == "POST"):
            # Pass through data to the Team App API
            method = request.POST.get("method")

            if (method == "join"):
                data = {
                    "team": request.POST.get("team_id")
                }
                url = TEAM_APP_API_URL + "manage/"
                params = {"method": "join"}
                headers = {
                    "Authorization": TEAM_APP_API_KEY,
                    "User-Token": user_token
                }

                api_response = session.post(
                    url=url,
                    data=data,
                    params=params,
                    headers=headers,
                    timeout=TEAM_APP_API_TIMEOUT
                )

        url = TEAM_APP_API_URL + "teams/"
        headers = {
            "Authorization": TEAM_APP_API_KEY,
            "User-Token": user_token
        }

        api_response = session.get(url=url, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
    except:
        print("Api failed to load")
    if api_response is not None and api_response.status_code == 200:
        teams = api_response.json()

    return render(
        request,
        "teams/join_team.html",
        {
            "teams": teams,
        },
    )

@login_required
def edit_team(request:HttpRequest, id):
    """
    Renders the page that allows owners of a team to modify different properties of that team.

    Also handles editing of a team's name and description.
    """

    if not id:
        return JsonResponse({"Error": "Team name not found"})

    userprofile: UserProfile = UserProfile.objects.get(user=request.user)

    user_token = get_user_token_from_request(request)

    api_data = retrieve_team_member_data(id, user_token)
    if api_data is None or not api_data[0].get("members"):
        return JsonResponse({"Error": "Invalid team data returned from API"})

    team = api_data[0]
    initial_data = {
        "name": team["name"],
        "description": team["description"] 
    }

    form = CreateTeamForm(initial=initial_data) # Reuse the form used for creating a team

    current_user = request.user.username

    is_owner = any(
        member["user"]["username"] == current_user and
        member["user"].get("role_info", {}).get("role", "").lower() == "owner"
        for member in api_data[0]["members"]
    )

    if not is_owner:
        raise PermissionDenied

    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            url = TEAM_APP_API_URL + "teams/"
            params = {"method": "edit"}
            data = request.POST
            headers = {
                "Authorization": TEAM_APP_API_KEY,
                "User-Token": user_token
            }

            api_response = session.post(url=url, params=params, data=data, headers=headers, timeout=TEAM_APP_API_TIMEOUT)

            if api_response.status_code != 200:
                print("Error in Team API")

            # Get the updated API data again after authorising the user and editing the team
            api_data = retrieve_team_member_data(id, user_token)
            if api_data is None or not api_data[0].get("members"):
                return JsonResponse({"Error": "Invalid team data returned from API"})
            

    roles = Role.objects.all()
    return render(
        request,
        "teams/edit_team.html",
        {
            "team": api_data[0],
            "roles": roles,
            "form": form
        }
    )

@login_required
def delete_team(request:HttpRequest):
    """
    Deletes a team and, if successful, checks for lingering switch permissions and deletes them, and
    then redirects back to the list of joined teams.
    """

    user_token = get_user_token_from_request(request)

    url = TEAM_APP_API_URL + "teams/"
    data = {"id": request.POST.get("team_id")}
    params = {"method": "delete"}
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }

    api_response = session.post(url=url, data=data, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT)

    if (api_response.status_code == 200):
        # Remove lingering switch permissions upon success
        check_for_lingering_switch_perms(request.user.username, remove_switch_permissions, user_token)

    return redirect(reverse("dashboard")) # Redirect back to the list of joined teams