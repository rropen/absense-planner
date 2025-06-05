import hashlib

import environ

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest

from requests import Session

env = environ.Env()
environ.Env.read_env()

TEAM_APP_API_URL = env("TEAM_APP_API_URL")
TEAM_APP_API_KEY = env("TEAM_APP_API_KEY")

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
            username = data[teamIndex]['team']['members'][userIndex]['user']['username']
            return username
        for userIndex in range(len(data[teamIndex]['team']['members'])):
            if username == fetch_username_from_json(userIndex):
                saved_user = data[teamIndex]['team']['members'][userIndex]
                data[teamIndex]['team']['members'].pop(userIndex)
                data[teamIndex]['team']['members'].insert(0,saved_user)
                break

def retrieve_calendar_data(user, sort_value, user_token):
    api_response = None

    try:
        url = TEAM_APP_API_URL + "user/teams/"
        params = {
            "sort": sort_value
        }
        headers = {
            "User-Token": user_token,
            "Authorization": TEAM_APP_API_KEY
        }

        api_response = session.get(url=url, params=params, headers=headers)
    except:
        print("API Failed to connect")
        return # Caller should handle the API error
    
    if api_response is not None and api_response.status_code == 200:
        api_response = api_response.json()
    return api_response

def get_users_sharing_teams(username, user_model, user_token):
    teams = retrieve_calendar_data(user_model, None, user_token)
    users_sharing_teams = set()

    if teams is None:
        return # Caller should handle the API error
        # Avoid error from iterating through None type
    elif teams == []: # The current_user is not in any teams
        return users_sharing_teams # Avoid error from iterating
                                   # through empty set

    for team in teams:
        team = team["team"]
        for member in team["members"]:
            member_username = member["user"]["username"]
            users_sharing_teams.add(member_username)

    try:
        users_sharing_teams.remove(username)
    except:
        print("User does not exist in team app database")
        return # Caller should handle error
    # ^^^ Remove the user whos teams are being queried
    # as this will avoid conflicts.

    return users_sharing_teams

def check_user_exists(username):
    user_exists = None
    api_response = None

    try:
        url = TEAM_APP_API_URL + "user_exists/"
        params = {"username": username}
        headers = {
            "Authorization": TEAM_APP_API_KEY,
        }

        api_response = session.get(url=url, params=params, headers=headers)
    except:
        print("API Failed to connect")
        return # Caller should handle the API error
    
    if api_response is not None and api_response.status_code == 200:
        user_exists = api_response.json()

    return user_exists

def is_team_app_running():
    team_app_running = False

    try:
        url = TEAM_APP_API_URL + "status_check/"
        # We do not need an API key because it is a simple status check

        api_response = session.get(url=url)
    except:
        print("API Failed to connect")
        return team_app_running # Caller should handle the API error
    
    if api_response is not None and api_response.status_code == 200:
        team_app_running = True
    
    return team_app_running

def retrieve_team_member_data(id, user_token):
    """
    Gets the data about team members of a particular team.

    This is needed for the edit team page and specific team calendar ("view team") page.
    """
    team_member_data = None
    try:
        url = TEAM_APP_API_URL + "members/"
        params = {"id": id}
        headers = {
            "Authorization": TEAM_APP_API_KEY,
            "User-Token": user_token
        }

        api_response = session.get(url=url, params=params, headers=headers)

        team_member_data = api_response.json()
    except:
        raise NotImplementedError("Could not find API (No error page)")
    
    if api_response.status_code != 200:
        raise NotImplementedError("Invalid team name (No error page)")

    return team_member_data

def favourite_team(user_token, team_id):
    url = TEAM_APP_API_URL + 'manage/'
    data = {
        "team": team_id
    }
    params = {
        "method": "favourite"
    }
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }

    api_response = session.post(url=url, data=data, params=params, headers=headers)

    return api_response

@login_required
def get_user_token_from_request(request:HttpRequest):
    username = str(request.user.username).encode() # Get the raw username string from request
    user_token = hashlib.sha256(username).hexdigest() # Encrypt and get digest value

    return user_token