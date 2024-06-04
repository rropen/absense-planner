#check_calendar_date
#set_calendar_month
#all_calendar
#team_calendar
#api_calendar_view
#get_date_data
#get_filter_users

import datetime
import requests
import hashlib
import environ
from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import *
from .models import ( Relationship, Role, Team,
                     UserProfile, Status, ColorData, ColourScheme)

from .absences import *
from .teams import *

def check_calendar_date(year, month) -> bool:
    date = datetime.datetime(year, datetime.datetime.strptime(month, "%B").month, 1)
    current = datetime.datetime.now()
    
    if date < (current - relativedelta(years=1)) or date > (current + relativedelta(years=1)):
        return False
    
    return True

@login_required
def set_calendar_month(request):
    if request.method == "POST":
        month = request.POST.get('month_names')
        
        split = month.split()

        month = split[0]

        year = split[1]

        print(month)

    return redirect('all_calendar', month=month, year=year)

def color_variant(hex_color, brightness_offset=1):
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    return "rgb" + str(new_rgb_int).replace("[", "(").replace("]", ")")

def get_colour_data(request:HttpRequest):
    colour_data = {}
    for scheme in ColourScheme.objects.all():
        scheme_data = {}
        data = ColorData.objects.filter(user=request.user, scheme=scheme)
        if data.exists():
            scheme_data["enabled"] = data[0].enabled
            scheme_data["colour"] = data[0].color
            scheme_data["offset"] = color_variant(data[0].color, -30)
        else:
            scheme_data["enabled"] = True
            scheme_data["colour"] = scheme.default
            scheme_data["offset"] = color_variant(scheme.default, -30)
        
        colour_data[scheme.name.replace(" ", "_").lower()] = scheme_data
    
    return colour_data

def team_calendar_data(id):
    data = None

    try:
        response = requests.get(env("TEAM_DATA_URL") + "api/members/?id={}".format(id))
        data = response.json()
    except:
        # TODO Create error page for API failure
        raise NotImplementedError("Failed to retrieve API data (No error page)")
    
    if response.status_code != 200:
        raise NotImplementedError("Failed to retrieve API data (No error page)")
    
    return data

#JC - Specific team calendar using the API
@login_required
def api_team_calendar(
    request:HttpRequest,
    id,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year
):
    
    date = check_calendar_date(year, month)
    if not date:
        return redirect("api_team_calendar")

    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except IndexError:
        # TODO Create an error page if a userprofile is not found.
        raise NotImplementedError("Invalid User profile (No error page)")
    
    dates = get_date_data(userprofile.region, month, year)

    team_data = team_calendar_data(id)[0]

    #Get absence data
    team_users = []
    user_data = None
    for user in team_data["members"]:
        user_instance = User.objects.filter(username=user["user"]["username"])
        if user_instance.exists() and user_instance not in team_users:
            team_users.append(user_instance[0])

        if user["user"]["username"] == request.user.username:
            user_data = user["user"]

    absence_data = get_absence_data(team_users, 2)
    
    data = {
        **dates,
        **absence_data,
        "team": team_data,
        "user_data": user_data,
        "id": id,
        "url": env("TEAM_DATA_URL")
    }

    return render(request, "api_pages/team_calendar.html", data)
                    
def get_date_data(
    region,
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
    data["next_current_year"] = datetime.datetime.now().year + 1
    data["next_second_year"] = datetime.datetime.now().year + 2

    data["previous_current_year"] = datetime.datetime.now().year - 1

    last_year = datetime.datetime.today().year - 1
    next_year = datetime.datetime.today().year + 1

    try:
        last_year_date = datetime.datetime.strptime(f"{last_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day}",'%Y-%m-%d').date()
        next_year_date = datetime.datetime.strptime(f"{next_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day}",'%Y-%m-%d').date()
    except ValueError: 
        last_year_date = datetime.datetime.strptime(f"{last_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day-1}",'%Y-%m-%d').date()
        next_year_date = datetime.datetime.strptime(f"{next_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day-1}",'%Y-%m-%d').date()


    #YYYY/MM/DD    
    start_date, end_date = last_year_date, next_year_date
 
    data["month_list"] = pd.period_range(start=start_date, end=end_date, freq='M')
    data["month_list"] = [month.strftime("%B %Y") for month in data["month_list"]]

    data["selected_date"] = datetime.date(int(data["year"]), datetime.datetime.strptime(month, "%B").month, 1).strftime("%B %Y")

    data["day_range"] = range(
        1,
        calendar.monthrange(
            data["year"], datetime.datetime.strptime(month, "%B").month
        )[1]
        + 1,
    )
    data["day_range_num"] = len(list(data["day_range"])) + 1
    data["month_num"] = datetime.datetime.strptime(month, "%B").month

    data["previous_month"] = "December"
    data["next_month"] = "January"
    data["previous_year"] = year - 1
    data["next_year"] = year + 1

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
    for h in holidays.country_holidays(region, years=year).items():
        if (h[0].month == data["month_num"]):
            data["bank_hol"].append(h[0].day)
        
    return data

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

def retrieve_calendar_data(request:HttpRequest, sortValue):
    data = None
    r = None

    try:
        token = (str(request.user) + "AbsencePlanner").encode()
        encryption = hashlib.sha256(token).hexdigest()
        r = requests.get(env("TEAM_DATA_URL") + "api/user/teams/?format=json&username={}&sort={}".format(request.user.username, sortValue), headers={"TEAMS-TOKEN": encryption})
    except:
        print("API Failed to connect")
    
    if r is not None and r.status_code == 200:
        data = r.json()
    
    return data

def retrieve_all_users(request:HttpRequest, data):
    users = []
    users.append(request.user)
    if data is not None:
        for team in data:
            for member in team["team"]["members"]:
                user = User.objects.filter(username=member["user"]["username"])
                if user.exists() and user not in users:
                    users.append(user[0])
    
    return users

#JC - Main calendar using API data.
@login_required
def main_calendar(
    request:HttpRequest,
    month = datetime.datetime.now().strftime("%B"),
    year = datetime.datetime.now().year
):

    #JC - Retrieve users profile
    try:
        userprofile: UserProfile = UserProfile.objects.get(user=request.user)
    except:
        # TODO Create an error page if the userprofile is not found.
        raise NotImplementedError("Invalid Userprofile (No error page)")

    #JC - Retrieve sort value of calendars.    
    sortValue = None
    if request.GET.get("sortBy") is not None:
        sortValue = request.GET.get("sortBy")

    #JC - Get names of teams and members in the team.
    teams_data = retrieve_calendar_data(request, sortValue)

    #JC - If a month has been selected by the user check if its valid.
    date = check_calendar_date(year, month)
    if not date:
        return redirect('main_calendar')

    date_data = get_date_data(userprofile.region, month, year)

    users = retrieve_all_users(request, teams_data)

    absence_data = get_absence_data(users, 2)

    colour_data = get_colour_data(request)

    weekends = {"Sa": "Sa", "Su": "Su"}

    context = {
        **date_data,
        **absence_data,
        **weekends,
        **colour_data,
        "team_data": teams_data,
        "sort_value": sortValue
    }

    return render(request, "calendars/calendar.html", context)