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

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import Lower
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from collections import namedtuple

from .forms import *
from .models import (Absence, Relationship, Role, Team, Status
                     )

from .absences import *

env = environ.Env()
environ.Env.read_env()


def teams_dashboard(request) -> render:
    rels = Relationship.objects.order_by(Lower("team__name")).filter(
        user=request.user, status=Status.objects.get(status="Active")
    )
    invite_rel_count = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Invited")
    ).count()
    
    try:
        token = (str(request.user) + "AbsencePlanner").encode()
        encryption = hashlib.sha256(token).hexdigest()
        r = requests.get(env("TEAM_DATA_URL") + "api/user/teams/?username={}".format(request.user.username), headers={"TEAMS-TOKEN": encryption})
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

    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        return redirect("/")

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
            "api_enabled": userprofile.external_teams,
            "api_url": env("TEAM_DATA_URL") + "api/teams/"
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
        all_teams_filtered = all_teams

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
        if r != None and r.status_code == 200:
            data = r.json()
            api_enabled = True

    return render(
        request,
        "teams/join_team.html",
        {"all_teams": all_teams_filtered, "joined_teams": user_teams, "api_enabled": api_enabled, "team_data": data},
    )


@login_required
def joining_team_process(request, id, role):
    find_team = Team.objects.get(id=id)
    find_role = Role.objects.get(role=role)
    rels = Relationship.objects.filter(
        user=request.user,
        role=Role.objects.get(role="Member"),
        status=Status.objects.get(status="Active"),
    )
    rels2 = Relationship.objects.filter(
        user=request.user,
        role=Role.objects.get(role="Owner"),
        status=Status.objects.get(status="Active"),
    )
    existing_rels = Relationship.objects.order_by(Lower("team__name")).filter(
        user=request.user, status=Status.objects.get(status="Active")
    )
    invite_rel_count = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Invited")
    ).count()
    
    if (rels or rels2) and role == "Member":
        return render(
        request,
        "teams/dashboard.html",
        {"rels": existing_rels, "invite_count": invite_rel_count, "teamspage_active": True, "message" : "You are already part of one team", "message_type":"is-danger"},
    )
    new_rel = Relationship.objects.create(
        user=request.user,
        team=find_team,
        role=find_role,
        status=Status.objects.get(status="Pending"),
    )
    if not find_team.private:
        Relationship.objects.filter(id=new_rel.id).update(
            status=Status.objects.get(status="Active")
        )
        #leader = Relationship.objects.get(team=id, role=Role.objects.get(role="Owner"))
        #userprofile = UserProfile.objects.get(user=request.user)
        #userprofile.edit_whitelist.add(leader.user)
        #userprofile.save()
    return redirect("dashboard")


def team_invite(request, team_id, user_id, role):
    find_team = Team.objects.get(id=team_id)
    find_user = User.objects.get(id=user_id)
    find_role = Role.objects.get(role=role)

    test = Relationship.objects.filter(team=find_team)

    # Boolean determines if viewer is in this team trying to invite others
    user_acceptable = False
    for rel in test:
        if rel.user == request.user and str(rel.role) == "Owner":
            user_acceptable = True
            break

    if str(request.user.id) != str(user_id) and user_acceptable:
        Relationship.objects.create(
            user=find_user,
            team=find_team,
            role=find_role,
            status=Status.objects.get(status="Invited"),
        )
        return redirect(f"/teams/calendar/{find_team.id}")
    # Else user is manipulating the URL making non-allowed invites - (Therefore doesn't create a relationship)

    return redirect("dashboard")


@login_required
def view_invites(request):
    all_invites = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Invited")
    )
    return render(request, "teams/invites.html", {"invites": all_invites})


@login_required
def leave_team(request, id):
    find_relationship = Relationship.objects.get(id=id)
    find_relationship.custom_delete()
    team_cleaner(find_relationship)
    return redirect("dashboard")


def team_cleaner(rel):
    """Detects if a team is empty and deletes it if it is."""
    team = Team.objects.get(id=rel.team.id)
    all_team_relationships = Relationship.objects.filter(team=team)
    if all_team_relationships.count() == 0:
        team.delete()

def is_member(user, team_id) -> bool:
    """ Determines if the user is a member of the team before accessing its contents """

    team = Relationship.objects.filter(team=Team.objects.get(id=team_id))

    # Boolean determines if viewer is in this team
    for rel in team:
        if rel.user == user:
            return True


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
    from absences import text_rules
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
def promote_team_member(request, id, user_id):
    """Checks to see if user is the owner and renders the Setting page"""
    team = Team.objects.get(id=id)
    user_relation = Relationship.objects.get(team=id, user=request.user)
    if user_relation.role.role != "Owner":
        return redirect("dashboard")
    target_user = User.objects.get(id=user_id)
    all_pending_relations = Relationship.objects.filter(
        team=id, status=Status.objects.get(status="Pending")
    )
    current_relationship = Relationship.objects.get(team=team, user=target_user)
    if current_relationship.role == Role.objects.get(role="Member"):
        current_relationship.role = Role.objects.get(role="Co-Owner")
        current_relationship.save()

    return redirect(team_settings, team.id)


@login_required
def demote_team_member(request, id, user_id):
    """Checks to see if user is the owner and renders the Setting page"""
    team = Team.objects.get(id=id)
    user_relation = Relationship.objects.get(team=id, user=request.user)
    if user_relation.role.role != "Owner":
        return redirect("dashboard")
    target_user = User.objects.get(id=user_id)
    all_pending_relations = Relationship.objects.filter(
        team=id, status=Status.objects.get(status="Pending")
    )
    current_relationship = Relationship.objects.get(team=team, user=target_user)
    if current_relationship.role == Role.objects.get(role="Co-Owner"):
        current_relationship.role = Role.objects.get(role="Member")
        current_relationship.save()

    return redirect(team_settings, team.id)

@login_required
def remove_team_member(request, id, user_id):
    """Removes a member from a team."""
    team = Team.objects.get(id=id)
    user_relation = Relationship.objects.get(team=id, user=request.user)
    if user_relation.role.role != "Owner":
        return redirect("dashboard") #Checks if the user is the owner and redirects to the dashboard if they aren't
    target_user = User.objects.get(id=user_id) #Gets the user to be removed
    target_relation = Relationship.objects.get(team=team, user=target_user) #Gets the target's relationship to the team
    target_relation.custom_delete() #Deletes the relationship from the team, removing the user

    return redirect(team_settings, team.id) #Redirects user back to the settings page


def joining_team_request(request, id, response):

    find_rel = Relationship.objects.get(id=id)
    

    if response == "accepted":
        state_response = Status.objects.get(status="Active")
        Relationship.objects.filter(id=find_rel.id).update(status=state_response)
        return redirect("team_settings", find_rel.team.id)
    elif response == "nonactive":
        return redirect("leave_team", id)
    return redirect("dashboard")

#JC - Add an absence via the form
def manual_add(request:HttpRequest) -> render:
    #JC - POST request
    if request.method == "POST":
        form = AbsenceForm(
            request.POST, 
            user=request.user,
            initial={
                "start_date": datetime.datetime.now(),
                "end_date": lambda: datetime.datetime.now().date() + datetime.timedelta(days=1)
            }
        )
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

        #JC - Create absence
        if form.is_valid():
            absence = Absence()
            absence.absence_date_start = form.cleaned_data["start_date"]
            absence.absence_date_end = form.cleaned_data["end_date"]
            absence.User_ID = request.user
            absence.Target_User_ID = form.cleaned_data["user"].user

            #JC - Check if the dates overlap with an existing absence. 
            valid = True
            Range = namedtuple('Range', ['start', 'end'])
            r1 = Range(start=absence.absence_date_start, end=absence.absence_date_end)
            for x in Absence.objects.filter(Target_User_ID=form.cleaned_data["user"].user.id):
                r2 = Range(start=x.absence_date_start, end=x.absence_date_end)
                delta = (min(r1.end, r2.end) -max(r1.start, r2.start)).days + 1
                overlapp = max(0, delta)
                if overlapp == 1:
                    valid = False
            
            if valid:
                absence.save()
                return redirect("/")
            else:
                return render(request, "ap_app/add_absence.html", {
                    "form": form,
                    "message": "The absence conflicts with an existing absence",
                    "message_type": "is-danger"
                })

    #JC - GET request
    else:
        form = AbsenceForm(user=request.user)
        #JC - Allow users to edit others absence if they have permission
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
    
    content = {"form": form}
    return render(request, "ap_app/add_absence.html", content)

def is_owner(user, team_id) -> bool:
    """ Determines if the user is an owner of the team """
    
    user_relation = Relationship.objects.get(team=team_id, user=user)
    return (user_relation.role.role == "Owner")