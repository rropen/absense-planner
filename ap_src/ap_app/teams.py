#teams_dashboard
#create_team
#join_team
#joining_team_process
#team_invite
#view_invites
#leave_team
#team_cleaner
#team_misc
#team_settings
#edit_team_member_absence
#promote_team_member
#demote_team_member
#remove_team_member
#joining_team_request
#is_member
#is_owner

import hashlib
import requests
import environ

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import redirect, render

from .forms import CreateTeamForm
from .models import Role, UserProfile

env = environ.Env()
environ.Env.read_env()


def teams_dashboard(request) -> render:
    try:
        token = (str(request.user) + "AbsencePlanner").encode()
        encryption = hashlib.sha256(token).hexdigest()
        r = requests.get(env("TEAM_DATA_URL") + "api/user/teams/?username={}".format(request.user.username), headers={"TEAMS-TOKEN": encryption})
    except:
        return render(
        request,
        "teams/dashboard.html",
        {"external_teams": False, "teamspage_active": True})
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
        {"external_teams": external_teams_data, "teamspage_active": True, "url": env("TEAM_DATA_URL")},
    )


@login_required
def create_team(request:HttpRequest) -> render:
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.name_similarity():
            # TODO: write code to tell the user that their team name is similar and to give them
            # options to change the team name.
            return HttpResponse(
                "Debug: Did not create form because the name is too similar to another team name"
            )

        if form.is_valid():
            # form.save()
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
            "api_enabled": userprofile.external_teams,
            "api_url": env("TEAM_DATA_URL") + "api/teams/?format=json"
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
    
    data = None
    api_enabled = False
    if userprofile.external_teams:
        try:
            r = requests.get(env("TEAM_DATA_URL") + "api/teams/?username={}".format(request.user.username))
        except:
            print("Api failed to load")
        if r is not None and r.status_code == 200:
            data = r.json()
            api_enabled = True

    return render(
        request,
        "teams/join_team.html",
        {"api_enabled": api_enabled, "team_data": data, "url": env("TEAM_DATA_URL")},
    )


#This page allows owners of a team to modify differnt properties of a team.
#Links to: teams/edit_team.html
@login_required
def edit_team(request:HttpRequest, id):

    if not id:
        return JsonResponse({"Error": "Team name not found"})

    userprofile: UserProfile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        response = requests.post(env("TEAM_DATA_URL") + "api/teams/?method=edit&format=json", data=request.POST)
        if response.status_code != 200:
            print(response.json())

    api_data = edit_api_data(userprofile, id)
    if api_data is None:
        raise ValueError("Invalid API Data")
    
    roles = Role.objects.all()

    return render(request, "teams/edit_team.html", context={"team": api_data[0], "roles": roles, "url": env("TEAM_DATA_URL")})


def edit_api_data(userprofile, id):
    data = None
    if userprofile.external_teams:
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


#@login_required
#def team_misc(request, id):
#    """Teams Miscellaneous/Notes page"""
#    if is_member(user=request.user, team_id=id):
#        team = Team.objects.get(id=id)
#
#        notes = CreateTeamForm(instance=team)
#
#        # TODO: Add a field to each team with a notes section - (for now it's just the teams description)
#
#        if "value" in request.GET:
#            team.notes = request.GET["value"]
#            team.save()
#
#        desc = team.description
#        notes = team.notes
#
#        return render(
#            request, "teams/misc.html", {"team": team, "desc": desc, "notes": notes}
#        )
#    return redirect("dashboard")


#def team_cleaner(rel):
#    """Detects if a team is empty and deletes it if it is."""
#    team = Team.objects.get(id=rel.team.id)
#    all_team_relationships = Relationship.objects.filter(team=team)
#    if all_team_relationships.count() == 0:
#        team.delete()


#def is_owner(user, team_id) -> bool:
#    """ Determines if the user is an owner of the team """
#    
#    user_relation = Relationship.objects.get(team=team_id, user=user)
#    return (user_relation.role.role == "Owner")
