import calendar
import datetime 
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CreateTeamForm, login, sign_up, DeleteUserForm, AbsenceForm
from .models import Absence, Relationship, Role, Team
from django.db.models.functions import Lower
from django.db.models import ProtectedError
from river.models.fields.state import State


profiles_info = []  # Not too sure how these details are going to be laid out

current_date = datetime.datetime.now()
YEAR = current_date.year
MONTH = current_date.strftime("%B")
DAY = current_date.day
from django.views.generic import UpdateView

def index(request) -> render:
    """returns the home page"""
    return render(request, "plannerapp/index.html")

def privacy_page(request) -> render:
    return render(request, "plannerapp/privacy.html")

@login_required
def teams_dashboard(request) -> render:
    rels = Relationship.objects.order_by(Lower("team__name")).filter(user=request.user, status=State.objects.get(slug="approved"))
    
    return render(request, "teams/dashboard.html", {"rels": rels})

@login_required
def create_team(request) -> render:
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            form.save()
            # Gets the created team and "Owner" Role and creates a Link between the user and their team
            created_team = Team.objects.get(name=form.cleaned_data['name'])
            assign_role = Role.objects.get(role="Owner")
            new_rel = Relationship.objects.create(
                user = request.user,
                team = created_team,
                role = assign_role,
            )
            new_rel.river.status.approve(as_user=request.user, next_state=State.objects.get(slug='approved'))
            return redirect("/teams/")
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
            "private" : team.private, 
            "count" : Relationship.objects.filter(team=team).count()
            })
    return render(request, "teams/join_team.html", {"all_teams": all_teams_count})

@login_required
def joining_team_process(request, id, role):
    find_team = Team.objects.get(id=id)
    find_role = Role.objects.get(role=role)
    new_rel = Relationship.objects.create(
        user = request.user,
        team = find_team,
        role = find_role,
    )
    if not find_team.private:
        new_rel.river.status.approve(as_user=request.user, next_state=State.objects.get(slug='approved'))


    return redirect("dashboard")

@login_required
def leave_team(request, id):
    find_relationship = Relationship.objects.get(id=id)
    find_relationship.custom_delete()
    team_cleaner(find_relationship)
    return redirect("dashboard")

def team_cleaner(rel):
    team = Team.objects.get(id=rel.team.id)
    all_team_relationships = Relationship.objects.filter(team=team)
    if all_team_relationships.count() == 0:
        team.delete()
    return

@login_required
def team_settings(request, id):
    """ Checks to see if user is the owner and renders the Setting page """
    team = Team.objects.get(id=id)
    user_relation = Relationship.objects.get(team=id, user=request.user)
    if user_relation.role.role == "Owner":
        all_pending_relations = Relationship.objects.filter(team=id, status=State.objects.get(slug="pending"))
        return render(request, "teams/settings.html", {"team" : team, "pending_rels": all_pending_relations})
    else:
        return redirect("dashboard")

def joining_team_request(request, id, response):
    find_rel = Relationship.objects.get(id=id)
    print(response)
    if response == "accepted":
        find_rel.river.status.approve(as_user=request.user, next_state=State.objects.get(slug='approved'))
    elif response == "declined":
        find_rel.river.status.approve(as_user=request.user, next_state=State.objects.get(slug='declined'))
    return redirect("dashboard")

@login_required
def add(request) -> render:
    """create new absence record"""
    if request.method == "POST":
        form = AbsenceForm(request.POST)
        if form.is_valid():
            obj = Absence()
            obj.absence_date_start = form.cleaned_data["start_date"]
            obj.absence_date_end = form.cleaned_data["end_date"]
            obj.request_accepted = False
            obj.User_ID = request.user
            obj.save()

            # redirect to success page
    else:
        form = AbsenceForm()
    content = {"form": form}
    return render(request, "plannerapp/add_absence.html", content)

@login_required
def details_page(request) -> render:
    """returns details web page"""
    # TODO: get employee details and add them to context
    context = {"employee_dicts": ""}
    return render(request, "plannerapp/Details.html", context)

@login_required
def team_calendar(request, id, month=MONTH, year=YEAR):

    month_days = calendar.monthrange(
        year, datetime.datetime.strptime(month, "%B").month
    )[1]

    users = Relationship.objects.all().filter(team=id, status=State.objects.get(slug="approved"))

    absence_content = []
    total_absence_dates = {}
    all_absences = {}
    delta = datetime.timedelta(days=1)

    for user in users:
        # all the absences for the user
        absence_info = Absence.objects.filter(User_ID=user.user.id)
        total_absence_dates[user] = []
        all_absences[user] = []

        # if they have any absences
        if absence_info:
            # mapping the absence content to keys in dictionary
            for x in range(len(absence_info)): # pylint: disable=consider-using-enumerate

                absence_id = absence_info[x].ID

                absence_date_start = absence_info[x].absence_date_start
                absence_date_end = absence_info[x].absence_date_end
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
            total_absence_dates[user] = total_absence_dates[user]
            all_absences[user] = absence_content


    previous_month = 1
    next_month = 12
    try:

        next_month = datetime.datetime.strptime(
            str((datetime.datetime.strptime(month, "%B")).month + 1), "%m"
        ).strftime("%B")
    except:
        pass
    try:
        previous_month = datetime.datetime.strptime(
            str((datetime.datetime.strptime(month, "%B")).month - 1), "%m"
        ).strftime("%B")
    except:
        pass
    dates = "dates"
    team = Team.objects.get(id=id)
    context = {
        "current_date": current_date,
        "day_range": range(1, month_days + 1),
        "absences": all_absences,
        "absence_dates": total_absence_dates,
        "users": users,
        "current_day": DAY,
        "current_month": MONTH,
        "current_year": YEAR,
        "month_num": datetime.datetime.strptime(month, "%B").month,
        "month": month,
        "year": year,
        "previous_year": year - 1,
        "next_year": year + 1,
        "previous_month": previous_month,
        "next_month": next_month,
        "date": dates,
        "team": team,
        "team_count": Relationship.objects.filter(team=team.id, status=State.objects.get(slug="approved")).count()
    }

    return render(request, "teams/calendar.html", context)


@login_required
def all_calendar(request, month=MONTH, year=YEAR):
    month_days = calendar.monthrange(
        year, datetime.datetime.strptime(month, "%B").month
    )[1]


    all_users = []
    all_users.append(request.user)
    user_relations = Relationship.objects.filter(user=request.user)
    for relation in user_relations:
        rels = Relationship.objects.filter(team=relation.team, status=State.objects.get(slug="approved"))
        for rel in rels:
            if rel.user in all_users:
                pass
            else:
                all_users.append(rel.user)
    
    absence_content = []
    total_absence_dates = {}
    all_absences = {}
    delta = datetime.timedelta(days=1)

    for user in all_users:
        # all the absences for the user
        absence_info = Absence.objects.filter(User_ID=user.id)
        total_absence_dates[user] = []
        all_absences[user] = []

        # if they have any absences
        if absence_info:
            # mapping the absence content to keys in dictionary
            for x in range(len(absence_info)): # pylint: disable=consider-using-enumerate
                absence_id = absence_info[x].ID
                absence_date_start = absence_info[x].absence_date_start
                absence_date_end = absence_info[x].absence_date_end
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
            total_absence_dates[user] = total_absence_dates[user]
            all_absences[user] = absence_content

        else: 
            total_absence_dates[user] = []
            all_absences[user] = []
       

    previous_month = 1
    next_month = 12
    try:

        next_month = datetime.datetime.strptime(
            str((datetime.datetime.strptime(month, "%B")).month + 1), "%m"
        ).strftime("%B")
    except:
        pass
    try:
        previous_month = datetime.datetime.strptime(
            str((datetime.datetime.strptime(month, "%B")).month - 1), "%m"
        ).strftime("%B")
    except:
        pass
    dates = "dates"
    
    dates = "dates"
    context = {
        "current_date": current_date,
        "day_range": range(1, month_days + 1),
        "absences": all_absences,
        "absence_dates": total_absence_dates,
        "users": all_users,
        "current_day": DAY,
        "current_month": MONTH,
        "current_year": YEAR,
        "month_num": datetime.datetime.strptime(month, "%B").month,
        "month": month,
        "year": year,
        "previous_year": year - 1,
        "next_year": year + 1,
        "previous_month": previous_month,
        "next_month": next_month,
        "date": dates,
    }

    return render(request, "plannerapp/calendar.html", context)

# Profile page
@login_required
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

@login_required
def absence_delete(request, absence_id:int):
    absence = Absence.objects.get(pk=absence_id)
    user = request.user
    if user == absence.User_ID:
        absence.delete()
        return redirect("profile")
    else:
        raise Exception()

class EditAbsence(UpdateView):
    template_name = "plannerapp/edit_absence.html"
    model = Absence

    # specify the fields
    fields = ["absence_date_start", "absence_date_end"]

    def get_success_url(self) -> str:
        return reverse("profile")

@login_required
def profile_settings(request) -> render:
    """returns the settings page"""
    absences = Absence.objects.filter(User_ID=request.user.id)
    context = {"absences": absences}
    return render(request, "plannerapp/settings.html", context)

@login_required
def add_user(request) -> render:
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            absence:Absence = Absence.objects.filter(User_ID=request.user.id)[0]
        except IndexError:
            #TODO Create error page
            return redirect('/')

        try:
            user = User.objects.filter(username=username)[0]
        except IndexError:
            #TODO Create error page
            return redirect('/')
        
        absence.edit_whitelist.add(user)
        absence.save()
    return redirect('/profile/settings')