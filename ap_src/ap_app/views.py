# TODO: Review functions and variables names and ensure that they
#   ..  have meaningful names that represent what they do.


import calendar
import datetime
import json
from datetime import timedelta

import holidays
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import Lower
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, UpdateView
from river.models.fields.state import State

from .forms import *
from .models import (Absence, RecurringAbsences, Relationship, Role, Team,
                     UserProfile)

User = get_user_model()


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
        return all_calendar(request)
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
    return all_calendar(request)


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def teams_dashboard(request) -> render:
    rels = Relationship.objects.order_by(Lower("team__name")).filter(
        user=request.user, status=State.objects.get(slug="active")
    )
    invite_rel_count = Relationship.objects.filter(
        user=request.user, status=State.objects.get(slug="invited")
    ).count()
    return render(
        request,
        "teams/dashboard.html",
        {"rels": rels, "invite_count": invite_rel_count, "teamspage_active": True},
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
                status=State.objects.get(slug="active"),
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
        user=request.user, status=State.objects.get(slug="active")
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
        status=State.objects.get(slug="active"),
    )
    rels2 = Relationship.objects.filter(
        user=request.user,
        role=Role.objects.get(role="Owner"),
        status=State.objects.get(slug="active"),
    )
    existing_rels = Relationship.objects.order_by(Lower("team__name")).filter(
        user=request.user, status=State.objects.get(slug="active")
    )
    invite_rel_count = Relationship.objects.filter(
        user=request.user, status=State.objects.get(slug="invited")
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
        status=State.objects.get(slug="pending"),
    )
    if not find_team.private:
        Relationship.objects.filter(id=new_rel.id).update(
            status=State.objects.get(slug="active")
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
            status=State.objects.get(slug="invited"),
        )
        return redirect(f"/teams/calendar/{find_team.id}")
    # Else user is manipulating the URL making non-allowed invites - (Therefore doesn't create a relationship)

    return redirect("dashboard")


@login_required
def view_invites(request):
    all_invites = Relationship.objects.filter(
        user=request.user, status=State.objects.get(slug="invited")
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
            team=id, status=State.objects.get(slug="pending")
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
            team=id, status=State.objects.get(slug="pending")
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
        team=id, status=State.objects.get(slug="pending")
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
        team=id, status=State.objects.get(slug="pending")
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
        state_response = State.objects.get(slug="active")
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
            for x in Absence.objects.filter(User_ID=request.user.id):
                result = Absence.is_equivalent(obj, x)
                if result:
                    x.delete()
                    message = "Absence already created"
                    msg_type = "is-danger"
            obj.save()
            return render(
                request,
                "ap_app/add_absence.html",
                {
                    "form": form,
                    "message": message,
                    "message_type":msg_type,
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
        items = Absence()
        items.absence_date_start = json_data['date']
        items.absence_date_end = json_data['date']
        # issue #173
        items.Target_User_ID = request.user
        items.User_ID = request.user
        items.save()
        return JsonResponse({'start_date': items.absence_date_start, 'end_date': items.absence_date_end, 'taget_id': items.Target_User_ID.username, 'user_id': items.User_ID.username})
    else:
        return HttpResponse('404')

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


def get_date_data(
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    #  uses a dictionary to get all the data needed for the context
    #  and concatenates it to form the full context with other dictionaries
    data = {}
    data["current_year"] = datetime.datetime.now().year
    data["current_month"] = datetime.datetime.now().strftime("%B")
    data["current_month_num"] = datetime.datetime.now().month
    data["today"] = datetime.datetime.now().day
    data["year"] = year
    data["month"] = month

    data["day_range"] = range(
        1,
        calendar.monthrange(
            data["year"], datetime.datetime.strptime(month, "%B").month
        )[1]
        + 1,
    )
    data["month_num"] = datetime.datetime.strptime(month, "%B").month

    data["previous_month"] = "December"
    data["next_month"] = "January"
    data["previous_year"] = year - 1
    data["next_year"] = year + 1
    data["next_current_year"] = datetime.datetime.now().year + 1
    data["next_second_year"] = datetime.datetime.now().year + 2

    # as the month number resets every year try and except statements
    # have to be used as at the end and start of a year
    # the month cannot be calculated by adding or subtracting 1
    # as 13 and 0 are not datetime month numbers
    try:
        data["next_month"] = datetime.datetime.strptime(
            str((datetime.datetime.strptime(data["month"], "%B")).month + 1), "%m"
        ).strftime("%B")

    except ValueError:
        pass
    try:
        data["previous_month"] = datetime.datetime.strptime(
            str((datetime.datetime.strptime(data["month"], "%B")).month - 1), "%m"
        ).strftime("%B")
    except ValueError:
        pass

    # calculating which days are weekends to mark them easier in the html
    data["days_name"] = []
    for day in data["day_range"]:
        date = f"{day} {month} {year}"
        date = datetime.datetime.strptime(date, "%d %B %Y")
        date = date.strftime("%A")[0:2]
        data["days_name"].append(date)

    data["weekend_list"] = []
    for day in data["day_range"]:
        date = f"{day} {month} {year}"
        date = datetime.datetime.strptime(date, "%d %B %Y")
        date = date.strftime("%A")[0:2]
        if (date == "Sa" or date == "Su"):
            data["weekend_list"].append(day)
    

    data["bank_hol"] = []
    for h in holidays.GB(years=year).items():
        if (h[0].month == data["month_num"]):
            data["bank_hol"].append(h[0].day)
        
    return data




def get_absence_data(users, user_type):
    data = {}
    absence_content = []
    total_absence_dates = {}
    total_recurring_dates = {}
    all_absences = {}
    delta = datetime.timedelta(days=1)

    for user in users:
        # all the absences for the user
        if user_type == 1:
            user_id = user.user.id
        else:
            user_id = user.id

        absence_info = Absence.objects.filter(Target_User_ID=user_id)
        total_absence_dates[user] = []
        total_recurring_dates[user] = []
        all_absences[user] = []

        # if they have any absences
        if absence_info:
            # mapping the absence content to keys in dictionary
            for i, x in enumerate(absence_info):
                absence_id = x.ID
                absence_date_start = x.absence_date_start
                absence_date_end = x.absence_date_end
                dates = absence_date_start
                while dates <= absence_date_end:
                    total_absence_dates[user].append(dates)
                    dates += delta

                absence_content.append(
                    {
                        "ID": absence_id,
                        "absence_date_start": absence_date_start,
                        "absence_date_end": absence_date_end,
                        "dates": total_absence_dates[user],
                    }
                )

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            all_absences[user] = absence_content

        recurring = RecurringAbsences.objects.filter(Target_User_ID=user_id)

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
                    total_recurring_dates[user].append(x)
                # TODO: add auto deleting for recurring absences once last date of absences in before now
                # if x < datetime.datetime.now():
                #    pass

    data["recurring_absence_dates"] = total_recurring_dates
    data["all_absences"] = all_absences
    data["absence_dates"] = total_absence_dates
    data["users"] = users
    return data


@login_required
def team_calendar(
    request,
    id,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    if is_member(request.user, id):

        # Get acceptable date - (NOTHING BELOW now - 12months)
        date = check_calendar_date(year, month)
        if date:
            month = date.strftime("%B")
            year = date.year

        data_1 = get_date_data(month, year)

        users = Relationship.objects.all().filter(
            team=id, status=State.objects.get(slug="active")
        )

        data_2 = get_absence_data(users, 1)
        
        team = Team.objects.get(id=id)

        # Filtering users by privacy
        filtered_users = []
        viewer = data_2["users"].get(user=request.user)
        if str(viewer.role) == "Follower":
            # Than hide data of users with privacy on
            for user in data_2["users"]:
                user_profile = UserProfile.objects.get(user=user.user)
                if not user_profile.privacy:
                    filtered_users.append(user)

                else:
                    # For pop-up to inform viewer that there are hidden users
                    data_2.update({"hiding_users": True})

            data_2["users"] = filtered_users

        # Gets filtered users by filtering system on page
        filtered_users = get_filter_users(
            request, [user.user for user in data_2["users"]]
        )

        actual_filtered_users = []
        for user in data_2["users"]:
            if user.user in filtered_users:
                actual_filtered_users.append(user)

        # Reconstructs users list to be in desired form for template - (QuerySet of relationships)
        data_2["users"] = actual_filtered_users

        user_in_teams = []
        for rel in Relationship.objects.filter(team=team):
            user_in_teams.append(rel.user.id)

        data_3 = {
            "owner": Role.objects.all()[0],
            "Sa": "Sa",
            "Su": "Su",
            "current_user": Relationship.objects.get(user=request.user, team=team),
            "team": team,
            "all_users": User.objects.all().exclude(id__in=user_in_teams),
            "team_count": Relationship.objects.filter(
                team=team.id, status=State.objects.get(slug="active")
            ).count(),
        }

        context = {**data_1, **data_2, **data_3}

        return render(request, "teams/calendar.html", context)

    return redirect("dashboard")

@login_required
def set_calendar_month(request):
    if request.method == "POST":
        month = request.POST.get('month_names')
        year = request.POST.get('year_names')

    return redirect('all_calendar', month=month, year=year)


@login_required
def all_calendar(
    request,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
  
    # Get acceptable date - (NOTHING BELOW now - 12months)
    date = check_calendar_date(year, month)
    if date:
        month = date.strftime("%B")
        year = date.year

    data_1 = get_date_data(month, year)
    
    current_month = data_1["current_month"]
    current_year = data_1["current_year"]
    current_day = datetime.datetime.now().day
    date = f"{current_day} {current_month} {current_year}"
    date = datetime.datetime.strptime(date, "%d %B %Y")


    all_users = []
    all_users.append(request.user)

    user_relations = Relationship.objects.filter(
        user=request.user, status=State.objects.get(slug="active")
    )
    hiding_users = False


    for index, relation in enumerate(user_relations):
        rels = Relationship.objects.filter(
            team=relation.team, status=State.objects.get(slug="active")
        )

        # Finds the viewers role in the team
        for user in rels:
            if user.user == request.user:
                viewers_role = Role.objects.get(id=user.role_id)

        for rel in rels:
            if rel.user not in all_users:
                if viewers_role.role == "Follower":
                    # Than hide users data who have privacy on

                    user_profile = UserProfile.objects.get(user=rel.user)
                    if not user_profile.privacy:
                        # If user hasn't got their data privacy on
                        all_users.append(rel.user)
                    else:
                        # Used to inform user on calendar page if there are hiden users
                        hiding_users = True

                else:
                    # Only followers cannot view those who have privacy set for their data. - (Members & Owners can see the data)
                    all_users.append(rel.user)

    # Filtering
    filtered_users = get_filter_users(request, all_users)

    data_2 = get_absence_data(all_users, 2)

    data_3 = {"Sa": "Sa", "Su": "Su", "users_filter": filtered_users}

  
    grid_calendar_month_values = list(data_1["day_range"])
    # NOTE: This will select which value to use to fill in how many blank cells where previous month overrides prevailing months days. 
    # This is done by finding the weekday value for the 1st day of the month. Example: "Tu" will require 1 blank space/cell.
    for i in range({"Mo":0, "Tu":1, "We":2, "Th":3, "Fr":4, "Sa":5, "Su":6}[data_1["days_name"][0]]):
        grid_calendar_month_values.insert(0, -1)


    context = {
        **data_1,
        **data_2,
        **data_3,
        "users_hidden": hiding_users,
        "home_active": True,
        
        # Grid-Calendars day values  
        "detailed_calendar_day_range":grid_calendar_month_values,
     
        
    }
   

    return render(request, "ap_app/calendar.html", context)


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
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")

    user_profile = UserProfile.objects.get(user=request.user)
    if "userPrivacy" in request.POST:
        if user_profile.privacy:
            user_profile.privacy = False
        else:
            user_profile.privacy = True

        user_profile.save()

    privacy_status = user_profile.privacy
    context = {"userprofile": userprofile, "data_privacy_mode": privacy_status}
    return render(request, "ap_app/settings.html", context)


@login_required
def add_user(request) -> render:
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        # TODO Create error page
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = User.objects.get(username=username)
        except IndexError:
            # TODO Create error page
            return redirect("/")

        userprofile.edit_whitelist.add(user)
        user.save()

    return redirect("/profile/settings")


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


def get_filter_users(request, users) -> list:
    """Used for calendar filtering system - (Returns list of filtered users depending on
    search-bar and 'filter by absence' checkbox"""

    filtered_users = []

    # Filtering by both username & absence
    if "username" in request.GET and "absent" in request.GET:
        # Get username input & limits the length to 50
        name_filtered_by = request.GET["username"][:50]
        for absence in Absence.objects.all():
            user = User.objects.get(id=absence.Target_User_ID.id)
            if user in users:
                username = user.username
                if (
                    absence.Target_User_ID not in filtered_users
                    and name_filtered_by.lower() in username.lower()
                ):
                    filtered_users.append(absence.Target_User_ID)

    # ONLY filtering by username
    elif "username" in request.GET:
        # Name limit is 50
        name_filtered_by = request.GET["username"][:50]
        for user in users:
            # same logic as "icontains", searches through users names & finds similarities
            if name_filtered_by.lower() in user.username.lower():
                filtered_users.append(user)

    # ONLY filtering by absences
    elif "absent" in request.GET:
        for absence in Absence.objects.all():
            user = User.objects.get(id=absence.Target_User_ID.id)
            if user in users and absence.Target_User_ID not in filtered_users:
                filtered_users.append(absence.Target_User_ID)

    # Else, no filtering
    else:
        filtered_users = users

    return filtered_users


def is_member(user, team_id) -> bool:
    """ Determines if the user is a member of the team before accessing its contents """

    team = Relationship.objects.filter(team=Team.objects.get(id=team_id))

    # Boolean determines if viewer is in this team
    for rel in team:
        if rel.user == user:
            return True

    # Else user has changed URL & is attempting to view other teams content
    return False


def is_owner(user, team_id) -> bool:
    """ Determines if the user is an owner of the team """
    
    user_relation = Relationship.objects.get(team=team_id, user=user)
    return (user_relation.role.role == "Owner")


def check_calendar_date(year, month) -> datetime.datetime:
    """ This function will determine if the requested date is acceptable - (NOT before current date - 12 months) """
    # Current year * 12     + current month as num      = amount of months been  
    # requested year * 12   + requested month as num    = 
    
    # If requested date is before "current date - 12 months" than will not accept date
    todays_date = datetime.datetime.now()
    requested_months_amount = (int(year) * 12) + datetime.datetime.strptime(month, "%B").month
    current_months_amount   = (todays_date.year * 12) + todays_date.month 
    months_difference = current_months_amount - requested_months_amount


    if months_difference > 12:
        # Return the most earliest date acceptable - (now - 12 months)
        return datetime.datetime(todays_date.year - 1, todays_date.month, 1)  
    else:
        return None

from django.shortcuts import render


def my_view(request):
    return render(request, "base.html")