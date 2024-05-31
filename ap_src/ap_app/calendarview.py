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

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import *
from .models import ( Relationship, Role, Team,
                     UserProfile, Status, ColorData, ColourScheme)

from .absences import *
from .teams import *

def check_calendar_date(year, month) -> datetime.datetime:
    """ This function will determine if the requested date is acceptable - (NOT before current date - 12 months) """
    # Current year * 12     + current month as num      = amount of months been  
    # requested year * 12   + requested month as num    = 
    
    # If requested date is before "current date - 12 months" than will not accept date
    todays_date = datetime.datetime.now()
    requested_months_amount = (int(year) * 12) + datetime.datetime.strptime(month, "%B").month
    current_months_amount   = (todays_date.year * 12) + todays_date.month 
    months_difference = current_months_amount - requested_months_amount


 #   if months_difference > 12:
  #      # Return the most earliest date acceptable - (now - 12 months)
   #     return datetime.datetime(todays_date.year - 1, todays_date.month, 1)  
    #else:
     #   return None
    

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
    #return "#" + "".join([hex(i)[2:] for i in new_rgb_int])

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
    
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
    except IndexError:
        return redirect("/")
    
    if userprofile.external_teams:
        try:
            token = (str(request.user) + "AbsencePlanner").encode()
            encryption = hashlib.sha256(token).hexdigest()
            if requests.get(env("TEAM_DATA_URL") + "api/user/teams/?format=json&username={}".format(request.user.username), headers={"TEAMS-TOKEN": encryption}).status_code == 200:
                return redirect("/calendar/1")
        except:
            print("Failed to load api")


    data_1 = get_date_data(userprofile.region, month, year)
    
    current_month = data_1["current_month"]
    current_year = data_1["current_year"]
    current_day = datetime.datetime.now().day
    date = f"{current_day} {current_month} {current_year}"
    date = datetime.datetime.strptime(date, "%d %B %Y")


    all_users = []
    all_users.append(request.user)

    user_relations = Relationship.objects.filter(
        user=request.user, status=Status.objects.get(status="Active")
    )
    hiding_users = False


    for index, relation in enumerate(user_relations):
        rels = Relationship.objects.filter(
            team=relation.team, status=Status.objects.get(status="Active")
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

        try:
            userprofile: UserProfile = UserProfile.objects.filter(user=request.user)[0]
        except IndexError:
            return redirect("/")

        data_1 = get_date_data(userprofile.region, month, year)

        users = Relationship.objects.all().filter(
            team=id, status=Status.objects.get(status="Active")
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
                team=team.id, status=Status.objects.get(status="Active")
            ).count(),
        }

        context = {**data_1, **data_2, **data_3}

        return render(request, "teams/calendar.html", context)

    return redirect("dashboard")

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
    if date:
        month = date.strftime("%B")
        year = date.year

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


#JC - Calendar view using the API
@login_required
def api_calendar_view(
    request:HttpRequest,
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
    sortValue = None
    if request.method == "GET":
        if request.GET.get("sortBy") is not None:
            sortValue = request.GET.get("sortBy")
        try:
            token = (str(request.user) + "AbsencePlanner").encode()
            encryption = hashlib.sha256(token).hexdigest()
            r = requests.get(env("TEAM_DATA_URL") + "api/user/teams/?format=json&username={}&sort={}".format(request.user.username, sortValue), headers={"TEAMS-TOKEN": encryption})
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

    colour_data = get_colour_data(request)

    context = {
        **data_1,
        **data_2,
        **data_3,
        **colour_data,
        "home_active": True,
        "sort_value": sortValue,
        "api_data": api_data,
    }

    return render(request, "api_pages/calendar.html", context)
                    
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