import hashlib
import requests
import environ

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpRequest
from django.shortcuts import redirect, render

from ..forms import CreateTeamForm
from ..models import Role, UserProfile

env = environ.Env()
environ.Env.read_env()


def teams_dashboard(request) -> render:
    try:
        token = (str(request.user) + "AbsencePlanner").encode()
        encryption = hashlib.sha256(token).hexdigest()
        api_request = requests.get(env("TEAM_DATA_URL") + "api/user/teams/?username={}".format(request.user.username), headers={"TEAMS-TOKEN": encryption})
    except:
        return render(
        request,
        "teams/dashboard.html",
        {"teams": False})
    if api_request.status_code == 200:
        if len(api_request.json()) == 0 :
            teams = False
        else:
            teams = api_request.json()
    else:
        teams = False
    return render(
        request,
        "teams/dashboard.html",
        {"teams": teams, "url": env("TEAM_DATA_URL")},
    )


@login_required
def create_team(request:HttpRequest) -> render:
    if request.method == "POST":
        form = CreateTeamForm(request.POST)

        if form.is_valid():
            # # Gets the created team and "Owner" Role and creates a Link between
            # # the user and their team
            response = requests.post(env("TEAM_DATA_URL") + "api/teams/?format=json", data=request.POST)
            if response.status_code == 200:
                return redirect("/teams/api-calendar/" + str(response.json()["id"]))
            elif response.status_code == 400:
                context = {"form": form}
                if response.json()["name"] != None:
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
            "api_url": env("TEAM_DATA_URL") + "api/teams/?format=json",
        },
    )


@login_required
def join_team(request) -> render:
    """Renders page with all teams the user is not currently in"""
    # Filtering by team name
    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        return redirect("/")
    
    teams = None
    if userprofile:
        try:
            api_request = requests.get(env("TEAM_DATA_URL") + "api/teams/?username={}".format(request.user.username))
        except:
            print("Api failed to load")
        if api_request is not None and api_request.status_code == 200:
            teams = api_request.json()

    return render(
        request,
        "teams/join_team.html",
        {
            "teams": teams, "url": env("TEAM_DATA_URL"),
        },
    )


#This page allows owners of a team to modify differnt properties of a team.
#Links to: teams/edit_team.html
@login_required
def edit_team(request: HttpRequest, id):
    if not id:
        return JsonResponse({"Error": "Team name not found"})

    userprofile: UserProfile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        response = requests.post(
            env("TEAM_DATA_URL") + "api/teams/?method=edit&format=json",
            data=request.POST,
        )
        if response.status_code != 200:
            print(response.json())

    api_data = edit_api_data(userprofile, id)
    if api_data is None or not api_data[0].get("members"):
        return JsonResponse({"Error": "Invalid team data returned from API"})

    current_user = request.user.username

    is_owner = any(
        member["user"]["username"] == current_user and
        member["user"].get("role_info", {}).get("role", "").lower() == "owner"
        for member in api_data[0]["members"]
    )

    if not is_owner:
        raise PermissionDenied

    roles = Role.objects.all()
    return render(
        request,
        "teams/edit_team.html",
        {"team": api_data[0], "roles": roles, "url": env("TEAM_DATA_URL")},
    )


def edit_api_data(userprofile, id):
    data = None
    if userprofile:
        try:
            r = requests.get(env("TEAM_DATA_URL") + "api/members/?id={}".format(id))
            data = r.json()
        except:
            raise NotImplementedError("Could not find API (No error page)")
        
        if r.status_code != 200:
            raise NotImplementedError("Invalid team name (No error page)")
    else:
        raise NotImplementedError("The API setting is not enabled in your profile. (No error page)")

    return data