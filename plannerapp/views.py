import calendar
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CreateTeamForm, login, sign_up, DeleteUserForm, CreateAbsence
from .models import Absence, Relationship, Role, Team


def index(request) -> render:
    """returns the home page"""
    return render(request, "plannerapp/index.html")

def get_total_members(team):
    test = Relationship.objects.filter(team=team).count()
    return test

@login_required
def teams_dashboard(request) -> render:
    all_user_teams = Relationship.objects.all().filter(user=request.user)
    return render(request, "teams/dashboard.html", {"teams": all_user_teams})

@login_required
def create_team(request) -> render:
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            form.save()
            # Gets the created team and "Owner" Role and creates a Link between the user and their team
            created_team = Team.objects.get(name=form.cleaned_data['name'])
            assign_role = Role.objects.get(role="Owner")
            Relationship.objects.create(
                user = request.user,
                team = created_team,
                role = assign_role,
            )
    else:
        form = CreateTeamForm()
    return render(request, "teams/create_team.html", {"form": form})
     


@login_required
def join_team(request) -> render:
    """ Renders page with all teams the user is not currently in """
    user_teams = []
    all_user_teams = Relationship.objects.all().filter(user=request.user)
    for teams in all_user_teams:
        user_teams.append(teams.team.name)   
    all_teams = Team.objects.all().exclude(name__in=user_teams)
    all_teams_count = []
    for team in all_teams:
        all_teams_count.append({
            "id" : team.id,
            "name" : team.name,
            "description" : team.description,
            "count" : get_total_members(team)
            })
    return render(request, "teams/join_team.html", {"all_teams": all_teams_count})

@login_required
def joining_team_process(request, id, role):
    find_team = Team.objects.get(id=id)
    find_role = Role.objects.get(role=role)
    Relationship.objects.create(
        user = request.user,
        team = find_team,
        role = find_role,
    )
    return redirect("dashboard")

def leave_team(request, id):
    find_relationship = Relationship.objects.get(id=id)
    find_relationship.delete()
    return redirect("dashboard")


@login_required
def add(request) -> render:
    """create new absence record"""
    if request.method == "POST":
        form = CreateAbsence(request.POST)
        if form.is_valid():
            obj = Absence()
            obj.absence_date_start = form.cleaned_data["start_date"]
            obj.absence_date_end = form.cleaned_data["end_date"]
            obj.reason = form.cleaned_data["reason"]
            obj.request_accepted = False
            obj.User_ID = request.user
            obj.save()
    else:
        form = CreateAbsence()
    content = {"form": form}
    return render(request, "plannerapp/add_absence.html", content)

def details_page(request) -> render:
    """returns details web page"""
    # TODO: get employee details and add them to context
    context = {"employee_dicts": ""}
    return render(request, "plannerapp/Details.html", context)

def calendar_page(request, day:int=None, month:int=None, year:int=None) -> render:
    """returns calander web page with a context full of random junk"""
    # get the current date if no date has been passed
    if None in (day, month, year):
        date = datetime.now()
        year = date.year
        month = date.month
        day = date.day
    _, days_in_month = calendar.monthrange(year, month)
    users = User.objects.all()
    absences = []
    total_absence_dates = {}
    all_absences = {}
    for user in users:
        db_absences = Absence.objects.filter(User_ID=user)
        if not db_absences:
            continue
        # translating absence object to dictionary
        for absence in db_absences:
            start_date = absence.absence_date_start
            end_date = absence.absence_date_end
            # create list of dates that will be absent
            dates = [
                start_date + timedelta(days=n) for n in range(
                    start_date, end_date
                )
            ]
            absence_dict = {
                'id': absence.id,
                'start_date': start_date,
                'end_date': end_date,
                'included_dates': dates,
                'request_date': absence.request.date,
                'request_accepted': absence.request_accepted,
                'reason': absence.reason
            }
            absences.append(absence_dict)

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            total_absence_dates[user] = dates
            all_absences[user] = absences
    
    next_month = month + 1 if month < 12 else 1
    last_month = month - 1 if month > 1 else 12
    context = {
        "current_date": date,
        "day_range": range(1, days_in_month + 1),
        "absences": all_absences,
        "absence_dates": total_absence_dates,
        "users": list(users),
        "current_day": day,  # redundant because we have "current_date"
        "current_month": month, # redundant
        "current_year": year, # redundant
        "month_num": datetime.strptime(month, "%B").month,
        "month": month,
        "year": year,
        "previous_year": year - 1,
        "next_year": year + 1,
        "previous_month": last_month,
        "next_month": next_month,
        "date": dates,
    }
    return render(request, "plannerapp/Calendar.html", context)

# Profile page
def profile_page(request):
    absences = Absence.objects.filter(User_ID = request.user.id)
    return render(request, "plannerapp/profile.html", {"absences":absences})


def login_page(request):
    form = login()
    return render(request, "plannerapp/login.html", {"form": form})


def sign_up_page(request):
    form = sign_up()
    return render(request, "plannerapp/sign_up.html", {"form": form})

@login_required
def deleteuser(request):
    """delete a user account"""
    if request.method == 'POST':
        delete_form = DeleteUserForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("index")
    else:
        delete_form = DeleteUserForm(instance=request.user)

    context = {
        'delete_form' : delete_form
    }
    
    return render(request, 'registration/delete_account.html', context)
