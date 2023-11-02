# TODO: Review functions and variables names and ensure that they
#   ..  have meaningful names that represent what they do.


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
from django.contrib.auth.models import User

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile, Status)




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

    return render(
        request,
        "teams/join_team.html",
        {"all_teams": all_teams_filtered, "joined_teams": user_teams},
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


@login_required
def add(request) -> render:
    """create new absence record"""
    if request.method == "POST":
        form = AbsenceForm(
            request.POST,
            user=request.user,
            initial={
                "start_date": datetime.datetime.now(),
                "end_date": lambda: datetime.datetime.now().date()
                + datetime.timedelta(days=1),
            },
        )
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

        if form.is_valid():
            obj = Absence()
            obj.absence_date_start = request.POST.get("start_date")
            obj.absence_date_end = request.POST.get("end_date")
            obj.absence_date_start = form.cleaned_data["start_date"]
            obj.absence_date_end = form.cleaned_data["end_date"]
            obj.request_accepted = False  # TODO
            obj.User_ID = request.user
            obj.Target_User_ID = form.cleaned_data["user"].user
            message = "Absence successfully created"
            msg_type = "is-success"
            absence_valid = True
            for x in Absence.objects.filter(User_ID=request.user.id):
                if (obj.absence_date_start >= x.absence_date_start and obj.absence_date_end <= x.absence_date_end) \
                    or x.absence_date_start == obj.absence_date_end or x.absence_date_end == x.absence_date_start:
                        message = "Absence already created"
                        msg_type = "is-danger"
                        absence_valid = False
            if absence_valid:
                obj.save()
            return render(
                request,
                "ap_app/add_absence.html",
                {
                    "form": form,
                    "message": message,
                    "message_type": msg_type,
                    "add_absence_active": True,
                },
            )
            # redirect to success page
    else:
        form = AbsenceForm(user=request.user)
        form.fields["user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

    content = {"form": form, "add_absence_active": True}
    return render(request, "ap_app/add_absence.html", content)

#Add an absence when clicking on the calendar
@login_required
def click_add(request):
    if request.method == "POST":
        json_data=json.loads(request.body)
        if UserProfile.objects.filter(user__username=json_data["username"]).exists():
            perm_list = UserProfile.objects.filter(user__username=json_data["username"])[0].edit_whitelist.all()
        else:
            perm_list = [UserProfile.objects.get(user=request.user)]
        if request.user in perm_list:
            date = datetime.datetime.strptime(json_data["date"], "%Y-%m-%d").date()
            #This will add a half
            if json_data["half_day"] == True:
                absence = Absence()
                absence.absence_date_start = json_data['date']
                absence.absence_date_end = json_data['date']
                absence.Target_User_ID_id = User.objects.get(username=json_data["username"]).id
                absence.User_ID = request.user
                if json_data["half_day_time"] == "M":
                    absence.half_day = "MORNING"
                elif json_data["half_day_time"] == "A":
                    absence.half_day = "AFTERNOON"
                absence.save()
                return JsonResponse({})
            else:
                def non_connected():
                    absence = Absence()
                    absence.absence_date_start = json_data['date']
                    absence.absence_date_end = json_data['date']
                    absence.Target_User_ID_id = User.objects.get(username=json_data["username"]).id
                    absence.User_ID = request.user
                    absence.save()
                    return absence
                date = datetime.datetime.strptime(json_data["date"], "%Y-%m-%d").date()
                absence = None
                if date - timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_end", flat=True) \
                    and date + timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_start", flat=True):
                    ab_1 = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_start=date+timedelta(days=1))[0]
                    ab_2 = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_end=date-timedelta(days=1))[0]
                    if ab_1.half_day == "NORMAL" and ab_2.half_day == "NORMAL":
                        absence = Absence()
                        absence.absence_date_start = ab_2.absence_date_start
                        absence.absence_date_end = ab_1.absence_date_end
                        absence.Target_User_ID_id = User.objects.get(username=json_data["username"]).id
                        absence.User_ID = request.user
                        ab_1.delete()
                        ab_2.delete()
                        absence.save()
                    else:
                        absence = non_connected()
                    
                elif date - timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_start", flat=True):
                    a = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_start=date-timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_end = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date + timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_end", flat=True):
                    a = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_end=date+timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_start = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date - timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_end", flat=True):
                    a =Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_end=date-timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_end = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                elif date + timedelta(days=1) in Absence.objects.filter(Target_User_ID__username=json_data["username"]).values_list("absence_date_start", flat=True):
                    a = Absence.objects.filter(Target_User_ID__username=json_data["username"], absence_date_start=date+timedelta(days=1))[0]
                    if a.half_day == "NORMAL":
                        a.absence_date_start = date
                        a.save()
                        absence = a
                    else:
                        absence = non_connected()
                else:
                    absence = non_connected()

                return JsonResponse({'start_date': absence.absence_date_start, 'end_date': absence.absence_date_end, 'taget_id': absence.Target_User_ID.username, 'user_id': absence.User_ID.username})
        else:
            return JsonResponse({})
    else:
        return HttpResponse('404')
@login_required
def click_remove(request):
    if request.method == "POST":
        data = json.loads(request.body)
        date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
        if UserProfile.objects.filter(user__username=data["username"]).exists():
            perm_list = UserProfile.objects.filter(user__username=data["username"])[0].edit_whitelist.all()
        else:
            perm_list = [UserProfile.objects.get(user=request.user)]

        if request.user in perm_list:
            #Remove absence if start date and end date is the same
            if date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_start", flat=True) \
                and date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_end", flat=True):
                absence = Absence.objects.filter(Target_User_ID__username=data["username"], absence_date_start=date, absence_date_end=date)[0]
                absence.delete()
            #Change absence start date if current start date removed
            elif date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_start", flat=True):
                absence = Absence.objects.filter(Target_User_ID__username=data["username"], absence_date_start=date)[0]
                absence.absence_date_start = date + timedelta(days=1)
                absence.save()
            #Change absence end date if current end date removed
            elif date in Absence.objects.filter(Target_User_ID__username=data["username"]).values_list("absence_date_end", flat=True):
                absence = Absence.objects.filter(Target_User_ID__username=data["username"], absence_date_end=date)[0]
                absence.absence_date_end = date - timedelta(days=1)
                absence.save()
            else:
                for absence in Absence.objects.filter(Target_User_ID__username=data["username"]):
                    start_date = absence.absence_date_start
                    end_date = absence.absence_date_end
                    if date > start_date and date < end_date:
                        ab_1 = Absence()
                        ab_1.absence_date_start = start_date
                        ab_1.absence_date_end = date - timedelta(days=1)
                        ab_1.Target_User_ID_id = User.objects.get(username=data["username"]).id
                        ab_1.User_ID = request.user

                        ab_2 = Absence()
                        ab_2.absence_date_start = date + timedelta(days=1)
                        ab_2.absence_date_end = end_date
                        ab_2.Target_User_ID_id = User.objects.get(username=data["username"]).id
                        ab_2.User_ID = request.user

                        absence.delete()
                        ab_1.save()
                        ab_2.save()

        return JsonResponse({"start_date": data["date"]})
    else:
        return HttpResponse("404")

@login_required
def add_recurring(request) -> render:
    if request.method == "POST":
        form = RecurringAbsencesForm(request.POST)
        form2 = TargetUserForm(request.POST, target_user=request.user)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
        rule = str(form["Recurrences"].value())


        if not ("DAILY" in rule or "BY" in rule):
            content = {
                "form": form,
                "form2": form2,
                "message": "Must select a day/month",
            }
            return render(request, "ap_app/add_recurring_absence.html", content)

        if form2.is_valid():
            RecurringAbsences.objects.create(
                Recurrences=form["Recurrences"].value(),
                Target_User_ID=form2.cleaned_data["target_user"].user,
                User_ID=request.user,
            )
            return redirect("index")
    else:
        form = RecurringAbsencesForm()
        form2 = TargetUserForm(target_user=request.user)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )

    content = {"form": form, "form2": form2}
    return render(request, "ap_app/add_recurring_absence.html", content)


@login_required
def details_page(request) -> render:
    """returns details web page"""
    # TODO: get employee details and add them to context
    context = {"employee_dicts": ""}
    return render(request, "ap_app/Details.html", context)















@login_required
def set_calendar_month(request):
    if request.method == "POST":
        month = request.POST.get('month_names')
        
        split = month.split()

        month = split[0]

        year = split[1]

        print(month)

    return redirect('all_calendar', month=month, year=year)


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
def absence_delete(request, absence_id: int, user_id: int, team_id: int = 1):
    try:
        absence = Absence.objects.get(pk=absence_id)
        absence.delete()
    except Absence.DoesNotExist: 
        pass
    if request.user == User.objects.get(id = user_id):
        return redirect("profile")
    return redirect("edit_team_member_absence", team_id, user_id)


@login_required
def absence_recurring_delete(
    request, absence_id: int, user_id: int, team_id: int = None
):
    absence = RecurringAbsences.objects.get(pk=absence_id)
    user = request.user
    absence.delete()
    if user == absence.Target_User_ID:
        return redirect("profile")
    return redirect("edit_team_member_absence", team_id, user_id)


class EditAbsence(UpdateView):
    template_name = "ap_app/edit_absence.html"
    model = Absence

    # specify the fields
    fields = ["absence_date_start", "absence_date_end"]

    def get_success_url(self) -> str:
        return reverse("profile")


@login_required
def edit_recurring_absences(request, pk):
    absence = RecurringAbsences.objects.get(ID=pk)

    if request.method == "POST":
        form = RecurringAbsencesForm(request.POST, instance=absence)
        form2 = TargetUserForm(request.POST, target_user=request.user)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[request.user]
        )
        rule = str(form["Recurrences"].value())

        if not ("DAILY" in rule or "BY" in rule):
            content = {
                "form": form,
                "form2": form2,
                "message": "Must select a day/month",
            }
            return render(request, "ap_app/edit_recurring_absence.html", content)

        if form2.is_valid():
            absence.Target_User_ID = form2.cleaned_data["target_user"].user
            absence.recurrences = form["Recurrences"].value()
            absence.save()
            return redirect("index")
    else:
        form = RecurringAbsencesForm(instance=absence)
        
        form2 = TargetUserForm(target_user=absence.Target_User_ID)
        form2.fields["target_user"].queryset = UserProfile.objects.filter(
            edit_whitelist__in=[absence.User_ID]
        )

    return render(
        request, "ap_app/edit_recurring_absence.html", {"form": form, "form2": form2}
    )


@login_required
def profile_settings(request) -> render:
    """returns the settings page"""

    if len(request.POST) > 0:
        if request.POST.get("firstName") != "" and request.POST.get("firstName") != request.user.first_name:
            request.user.first_name = request.POST.get("firstName")
            request.user.save()
        if request.POST.get("lastName") != "" and request.POST.get("lastName") != request.user.last_name:
            request.user.last_name = request.POST.get("lastName")
            request.user.save()
        if request.POST.get("email") != request.user.email:
            request.user.email = request.POST.get("email")
            request.user.save()

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
        if request.POST.get("privacy") == None:
            userprofile.privacy = False
        elif request.POST.get("privacy") == "on":
            userprofile.privacy = True
        if request.POST.get("teams") == None:
            userprofile.external_teams = False
        elif request.POST.get("teams") == "on":
            userprofile.external_teams = True
        userprofile.save()
    
    country_data = get_region_data()
    country_name = pycountry.countries.get(alpha_2=userprofile.region).name

    privacy_status = userprofile.privacy
    teams_status = userprofile.external_teams
    context = {"userprofile": userprofile, "data_privacy_mode": privacy_status, "external_teams": teams_status,"current_country": country_name, **country_data}
    return render(request, "ap_app/settings.html", context)


@login_required
def add_user(request) -> render:
    data=json.loads(request.body)
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")

    if request.method == "POST":
        username = data["username"]

        try:
            user = User.objects.get(username=username)
        except:
            # TODO Create error page
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
        except:
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
        if (region_code != userporfile.region):
            userporfile.region = region_code
            userporfile.save()

    return redirect("/profile/settings")

def is_owner(user, team_id) -> bool:
    """ Determines if the user is an owner of the team """
    
    user_relation = Relationship.objects.get(team=team_id, user=user)
    return (user_relation.role.role == "Owner")




from django.shortcuts import render

def my_view(request):
    return render(request, "base.html")


def handler404(request, exception):
    context = {}
    response = render(request, "404.html", context=context)
    response.status_code = 404
    return response

def handler500(request):
    context = {}
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response

def handler400(request, exception):
    context = {}
    response = render(request, "400.html", context=context)
    response.status_code = 400
    return response


#JC - Calendar view using the API
@login_required
def api_calendar_view(
    request,
    #JC - These are the default values for the calendar.
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year
):
    
    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        return redirect("/")
    
    if not userprofile.external_teams:
        return redirect("/calendar/0")
    
    #JC - Get API data
    api_data = None
    if request.method == "GET":
        try:
            r = requests.get("http://localhost:8000/api/teams/?username={}".format(request.user.username))
        except:
            print("API failed to connect")
            return redirect("/")
        if r.status_code == 200:
            api_data = r.json()
        else:
            if r:
                result = r.json()
                if result["code"] == "I":
                    print("Username not found in Team App database.")
                elif result["code"] == "N":
                    print("A username was not provided with the request.")
            else:
                print("Fatal Error")

    date = check_calendar_date(year, month)
    if date:
        month = date.strftime("%B")
        year = date.year

    data_1 = get_date_data(userprofile.region, month, year)
    
    current_month = data_1["current_month"]
    current_year = data_1["current_year"]
    current_day = datetime.datetime.now().day
    date = f"{current_day} {current_month} {current_year}"
    date = datetime.datetime.strptime(date, "%d %B %Y")


    all_users = []
    all_users.append(request.user)

    if api_data:
        for team in api_data:
            for member in team["team"]["members"]:
                retrieved_user = User.objects.filter(username=member["user"]["username"])
                if retrieved_user.exists() and retrieved_user not in all_users:
                    all_users.append(retrieved_user[0])

    data_2 = get_absence_data(all_users, 2)

    data_3 = {"Sa": "Sa", "Su": "Su"}

    grid_calendar_month_values = list(data_1["day_range"])
    # NOTE: This will select which value to use to fill in how many blank cells where previous month overrides prevailing months days. 
    # This is done by finding the weekday value for the 1st day of the month. Example: "Tu" will require 1 blank space/cell.
    for i in range({"Mo":0, "Tu":1, "We":2, "Th":3, "Fr":4, "Sa":5, "Su":6}[data_1["days_name"][0]]):
        grid_calendar_month_values.insert(0, -1)


    context = {
        **data_1,
        **data_2,
        **data_3,
        "home_active": True,
        "api_data": api_data,
    }

    return render(request, "api_pages/calendar.html", context)
