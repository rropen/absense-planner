import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import calendar
import holidays
import environ

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpRequest

from ..models import UserProfile, ColorData, ColourScheme, User, Absence

from ..utils.absence_utils import get_absence_data
from ..utils.teams_utils import (
    get_users_teams,
    get_user_token_from_request,
    retrieve_team_member_data,
    sort_global_absences_by_logged_in_user,
)
from ..utils.errors import print_messages, derive_http_error_message

from requests import HTTPError, ConnectionError, RequestException

env = environ.Env()
environ.Env.read_env()


def check_calendar_date(year, month) -> bool:
    date = datetime.datetime(year, datetime.datetime.strptime(month, "%B").month, 1)

    current = datetime.datetime(
        datetime.datetime.now().year, datetime.datetime.now().month, 1
    )

    if date < (current - relativedelta(years=1)) or date > (
        current + relativedelta(years=1)
    ):
        return False

    return True


@login_required
def set_calendar_month(request):
    if request.method == "POST":
        month = request.POST.get("month_names")

        split = month.split()

        month = split[0]

        year = split[1]

    return redirect("all_calendar", month=month, year=year)


def color_variant(hex_color, brightness_offset=1):
    if len(hex_color) != 7:
        raise Exception(
            "Passed %s into color_variant(), needs to be in #87c95f format." % hex_color
        )
    rgb_hex = [hex_color[x : x + 2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [
        min([255, max([0, i])]) for i in new_rgb_int
    ]  # make sure new values are between 0 and 255
    return "rgb" + str(new_rgb_int).replace("[", "(").replace("]", ")")


def get_colour_data(user):
    colour_data = {}
    for scheme in ColourScheme.objects.all():
        scheme_data = {}
        data = ColorData.objects.filter(user=user, scheme=scheme)
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


def sort_team_members_by_logged_in_user(team_absences, request):
    """
    On the specific team calendar, ensure that the logged-in user and their absences
    are always at the top of the calendar.
    """
    user_username = request.user.username

    def fetch_username_from_json(userIndex):
        json_user_id = team_absences["members"][userIndex]["user"]["username"]
        return json_user_id

    for userIndex in range(len(team_absences["members"])):
        if user_username == fetch_username_from_json(userIndex):
            saved_user = team_absences["members"][userIndex]
            team_absences["members"].pop(userIndex)
            team_absences["members"].insert(0, saved_user)
            break


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
        last_year_date = datetime.datetime.strptime(
            f"{last_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day}",
            "%Y-%m-%d",
        ).date()
        next_year_date = datetime.datetime.strptime(
            f"{next_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day}",
            "%Y-%m-%d",
        ).date()
    except ValueError:
        last_year_date = datetime.datetime.strptime(
            f"{last_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day - 1}",
            "%Y-%m-%d",
        ).date()
        next_year_date = datetime.datetime.strptime(
            f"{next_year}-{datetime.datetime.today().month}-{datetime.datetime.today().day - 1}",
            "%Y-%m-%d",
        ).date()

    # YYYY/MM/DD
    start_date, end_date = last_year_date, next_year_date

    data["month_list"] = pd.period_range(start=start_date, end=end_date, freq="M")
    data["month_list"] = [month.strftime("%B %Y") for month in data["month_list"]]

    data["selected_date"] = datetime.date(
        int(data["year"]), datetime.datetime.strptime(month, "%B").month, 1
    ).strftime("%B %Y")

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
        if date == "Sa" or date == "Su":
            data["weekend_list"].append(day)

    data["bank_hol"] = []
    for h in holidays.country_holidays(region, years=year).items():
        if h[0].month == data["month_num"]:
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


def retrieve_all_users(request: HttpRequest, data):
    users = []
    users.append(request.user)
    if data is not None:
        for team in data:
            for member in team["team"]["members"]:
                user = User.objects.filter(username=member["user"]["username"])
                if user.exists() and user not in users:
                    users.append(user[0])

    return users


@login_required
def main_calendar(
    request: HttpRequest,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    """
    Renders main calendar using API data.
    """

    # Retrieve sort value of calendars.
    sortValue = None
    if request.GET.get("sortBy") is not None:
        sortValue = request.GET.get("sortBy")

    user = request.user
    user_token = get_user_token_from_request(request)

    # Get names of teams and members in the team.
    try:
        error, debug, success = None, None, None
        teams_data = get_users_teams(sortValue, user_token)
    except HTTPError as exception:
        error = "Error in fetching your joined teams - " + derive_http_error_message(
            exception
        )
    except ConnectionError as exception:
        error = (
            "Error - could not fetch the teams you are in due to a connection error."
        )
        debug = (
            "Error: Could not connect to the API to fetch a user's joined teams. Exception: "
            + str(exception)
        )
    except RequestException as exception:
        error = "Error - could not fetch the teams you are in due to an unknown error."
        debug = (
            "Error: Could not send a request to the API to fetch a user's joined teams. Exception: "
            + str(exception)
        )
    else:
        sort_global_absences_by_logged_in_user(teams_data, user.username)
        users = retrieve_all_users(request, teams_data)
    finally:
        if error:
            teams_data = None
            users = []

        calendar_data = retrieve_common_calendar_data(
            user, year, month, users, page="main_calendar"
        )
        print_messages(request, success=success, error=error, debug=debug)

    context = {
        **calendar_data,
        "team_data": teams_data,
        "sort_value": sortValue,
        "home_active": True,
    }
    return render(request, "calendars/all_teams_calendar.html", context)


@login_required
def api_team_calendar(
    request: HttpRequest,
    id,
    month=datetime.datetime.now().strftime("%B"),
    year=datetime.datetime.now().year,
):
    """
    Renders the specific team calendar using the API.
    """

    user = request.user

    user_token = get_user_token_from_request(request)
    team_data = retrieve_team_member_data(id, user_token)[0]
    sort_team_members_by_logged_in_user(team_data, request)

    team_data = [{"team": team_data}]

    # Get absence data
    team_users = []
    user_data = None
    for user in team_data[0]["team"]["members"]:
        user_instance = User.objects.filter(username=user["user"]["username"])
        if user_instance.exists() and user_instance not in team_users:
            team_users.append(user_instance[0])

        if user["user"]["username"] == request.user.username:
            user_data = user["user"]

    calendar_data = retrieve_common_calendar_data(
        request.user, year, month, team_users, page="api_team_calendar"
    )

    data = {
        **calendar_data,
        "team_data": team_data,
        "user_data": user_data,
        "id": id,
        "single_team": True,
    }

    return render(request, "calendars/specific_team_calendar.html", data)


def retrieve_common_calendar_data(user, year, month, team_users, page):
    """
    Retrieves common calendar data for use with the reusable calendar_element.html component template.
    """

    # Retrieve user's profile
    try:
        userprofile: UserProfile = UserProfile.objects.get(user=user)
    except:
        # TODO Create an error page if the userprofile is not found.
        raise NotImplementedError("Invalid Userprofile (No error page)")

    # If a month has been selected by the user check if its valid.
    date = check_calendar_date(year, month)
    if not date:
        return redirect(page)

    date_data = get_date_data(userprofile.region, month, year)
    absence_data = get_absence_data(team_users, 2)

    colour_data = get_colour_data(user)

    weekends = {"Sa": "Sa", "Su": "Su"}

    common_calendar_data = {**date_data, **absence_data, **weekends, **colour_data}

    return common_calendar_data
