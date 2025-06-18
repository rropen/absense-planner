"""
Utility functions that are reused to retrieve data from the Team App API.

Request errors are thrown and not handled here on purpose so they can be handled further up the stack (i.e., in views).
"""

import hashlib

import environ

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest

from requests import Session

env = environ.Env()
environ.Env.read_env()

TEAM_APP_API_URL = env("TEAM_APP_API_URL")
TEAM_APP_API_KEY = env("TEAM_APP_API_KEY")
TEAM_APP_API_TIMEOUT = float(env("TEAM_APP_API_TIMEOUT"))

# Use the session object from the Python requests library to send requests and pool the connection resources.
# Without this, the requests sent to the API are EXTREMELY SLOW.
session = Session()


def sort_global_absences_by_logged_in_user(data, username):
    """
    On the main calendar showing the absences for every team, ensure that the
    logged-in user and their absences are always at the top of each team's calendar.
    """

    for teamIndex in range(len(data)):

        def fetch_username_from_json(userIndex):
            username = data[teamIndex]["team"]["members"][userIndex]["user"]["username"]
            return username

        for userIndex in range(len(data[teamIndex]["team"]["members"])):
            if username == fetch_username_from_json(userIndex):
                saved_user = data[teamIndex]["team"]["members"][userIndex]
                data[teamIndex]["team"]["members"].pop(userIndex)
                data[teamIndex]["team"]["members"].insert(0, saved_user)
                break


def get_users_teams(sort_value, user_token):
    """
    Retrieves data about all the teams a user is already in.
    """

    api_response = None

    # Prepare request parameters
    url = TEAM_APP_API_URL + "user/teams/"
    params = {"sort": sort_value}
    headers = {"User-Token": user_token, "Authorization": TEAM_APP_API_KEY}

    # Send request to Team App API and store in response object
    api_response = session.get(
        url=url, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT
    )
    # Caller should handle the API error

    api_response.raise_for_status()
    api_response = api_response.json()

    return api_response


def get_users_sharing_teams(username, user_model, user_token):
    """
    This creates a unique list of users that are in the same teams.

    Used when looking for redundant switch permissions.
    """

    # Caller should handle the API error
    teams = get_users_teams(None, user_token)
    users_sharing_teams = set()

    if teams is None:
        return  # Caller should handle the API error
        # Avoid error from iterating through None type
    elif teams == []:  # The current_user is not in any teams
        return users_sharing_teams  # Avoid error from iterating
        # through empty set

    for team in teams:
        team = team["team"]
        for member in team["members"]:
            member_username = member["user"]["username"]
            users_sharing_teams.add(member_username)

    users_sharing_teams.remove(username)

    return users_sharing_teams


def check_user_exists(username):
    """
    Looks for a user (from the Absence Planner) on the Team App database.
    """

    user_exists = False  # Assume the user does not exist until proved otherwise

    url = TEAM_APP_API_URL + "user_exists/"
    params = {"username": username}
    headers = {
        "Authorization": TEAM_APP_API_KEY,
    }

    api_response = session.get(
        url=url, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT
    )
    # Caller should handle the API error

    api_response.raise_for_status()
    user_exists = api_response.json()  # API returns True or False

    return user_exists


def is_team_app_running():
    """
    Checks if the Team App is running by pinging the Team App API and
    responding to a simple HTTP 200.

    Errors are handled here, unlike other utilities, so that a simple
    True or False can be returned.
    """

    team_app_running = False

    try:
        url = TEAM_APP_API_URL + "status_check/"
        # We do not need an API key because it is a simple status check

        api_response = session.get(url=url, timeout=TEAM_APP_API_TIMEOUT)
    except Exception as exception:
        print(exception)
        return team_app_running  # Caller should handle the API error

    if api_response is not None and api_response.status_code == 200:
        team_app_running = True

    return team_app_running


def retrieve_team_member_data(id, user_token):
    """
    Gets the data about team members of a particular team.

    This is needed for the edit team page and specific team calendar
    ("view team") page.
    """

    api_response = None

    url = TEAM_APP_API_URL + "members/"
    params = {"id": id}
    headers = {"Authorization": TEAM_APP_API_KEY, "User-Token": user_token}

    api_response = session.get(
        url=url, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT
    )
    # Caller should handle API error

    api_response.raise_for_status()
    api_response = api_response.json()

    return api_response


def favourite_team(user_token, team_id):
    """
    Favourites a team on the Team App.
    """

    url = TEAM_APP_API_URL + "manage/"
    data = {"team": team_id}
    params = {"method": "favourite"}
    headers = {"Authorization": TEAM_APP_API_KEY, "User-Token": user_token}

    api_response = session.post(
        url=url, data=data, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT
    )
    api_response.raise_for_status()

    return api_response


@login_required
def get_user_token_from_request(request: HttpRequest):
    """
    Looks for the username of the user who sent the request so that they have to be authenticated.

    If they are authenticated, their username is transformed into a User Token by hashing it, which
    is then used in the headers of a request to the private Team App API to validate their identity.
    """

    username = str(
        request.user.username
    ).encode()  # Get the raw username string from request
    user_token = hashlib.sha256(username).hexdigest()  # Encrypt and get digest value

    return user_token


def edit_user_details(user_token, first_name=None, last_name=None, email=None):
    """
    Edits the user's details using the Team App API:

    - First Name
    - Last Name
    - Email Address
    """

    url = TEAM_APP_API_URL + "user/"
    data = {"first_name": first_name, "last_name": last_name, "email": email}
    headers = {"Authorization": TEAM_APP_API_KEY, "User-Token": user_token}

    api_response = session.post(
        url=url, data=data, headers=headers, timeout=TEAM_APP_API_TIMEOUT
    )
    api_response.raise_for_status()

    return api_response


def fetch_user_details(user_token):
    """
    Fetches details about the user using the Team App API:

    - First Name
    - Last Name
    - Email Address
    """

    url = TEAM_APP_API_URL + "user/"
    headers = {"Authorization": TEAM_APP_API_KEY, "User-Token": user_token}

    api_response = session.get(url=url, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
    api_response.raise_for_status()

    user_details = api_response.json()[0]

    return user_details
