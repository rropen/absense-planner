import hashlib
import requests
import environ

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from ..forms import CreateTeamForm
from ..models import Role, UserProfile
from ..utils.teams_utils import edit_api_data, favourite_team
from ..utils.switch_permissions import check_for_lingering_switch_perms, remove_switch_permissions

env = environ.Env()
environ.Env.read_env()
TEAM_APP_API_URL = env("TEAM_APP_API_URL")

@login_required
def teams_dashboard(request) -> render:
    if (request.method == "POST"):
        api_specific_method = request.POST.get("method")
        if (api_specific_method == "favourite"):
            favourite_team(request.user.username, request.POST.get("team"))

    try:
        token = (str(request.user) + "AbsencePlanner").encode()
        token = hashlib.sha256(token).hexdigest()

        # Prepare request parameters
        params = {"username": request.user.username}
        headers = {"TEAMS-TOKEN": token}
        url = TEAM_APP_API_URL + "user/teams/"

        # Send request to Team App API and store in response object
        api_response = requests.get(url=url, params=params, headers=headers)
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
        {"teams": teams, "url": TEAM_APP_API_URL},
    )

@login_required
def leave_team(request):
    """
    Leaves a team and removes lingering switch permissions.
    """

    username = request.user.username

    url = TEAM_APP_API_URL + "manage/"
    data = {
        "username": username,
        "team": request.POST.get("team_id")
    }
    params = {
        "method": "leave"
    }

    api_response_leave_team = requests.post(url=url, data=data, params=params)
    if (api_response_leave_team.status_code == 200):
        # Remove lingering switch permissions upon success
        check_for_lingering_switch_perms(username, remove_switch_permissions)

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

            url = TEAM_APP_API_URL + "teams/"
            data = request.POST # This is the data sent by the user in the CreateTeamForm

            api_response = requests.post(url=url, data=data)

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
            "api_url": TEAM_APP_API_URL + "teams/?format=json",
        },
    )

@login_required
def join_team(request) -> render:
    """Renders page with all teams the user is not currently in and handles joining of specific teams."""
    # Filtering by team name
    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        return redirect("/")
    
    teams = None
    if userprofile:
        try:
            if (request.method == "POST"):
                # Pass through data to the Team App API
                method = request.POST.get("method")

                if (method == "join"):
                    data = {
                        "username": request.user.username,
                        "team": request.POST.get("team_id")
                    }
                    url = TEAM_APP_API_URL + "manage/"
                    params = {"method": "join"}

                    api_response = requests.post(url=url, data=data, params=params)

            params = {"username": request.user.username}
            url = TEAM_APP_API_URL + "teams/"

            api_response = requests.get(url=url, params=params)
        except:
            print("Api failed to load")
        if api_response is not None and api_response.status_code == 200:
            teams = api_response.json()

    return render(
        request,
        "teams/join_team.html",
        {
            "teams": teams, "url": TEAM_APP_API_URL,
        },
    )

@login_required
def edit_team(request:HttpRequest, id):
    """
    Renders the page that allows owners of a team to modify different properties of a team.
    """

    if not id:
        return JsonResponse({"Error": "Team name not found"})

    userprofile: UserProfile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        url = TEAM_APP_API_URL + "teams/"
        params = {"method": "edit"}
        data = request.POST

        api_response = requests.post(url=url, params=params, data=data)

        if api_response.status_code != 200:
            print(api_response.json())

    api_data = edit_api_data(userprofile, id)
    if api_data is None:
        raise ValueError("Invalid API Data")
    
    roles = Role.objects.all()

    return render(request, "teams/edit_team.html", context={"team": api_data[0], "roles": roles, "url": TEAM_APP_API_URL})