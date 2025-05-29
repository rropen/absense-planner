import hashlib
import requests

import environ

def sort_global_absences_by_logged_in_user(data, user):
    for teamIndex in range(len(data)):
        def fetch_username_from_json(userIndex):
            user_username = data[teamIndex]['team']['members'][userIndex]['user']['username']
            return user_username
        for userIndex in range(len(data[teamIndex]['team']['members'])):
            if user.username == fetch_username_from_json(userIndex):
                saved_user = data[teamIndex]['team']['members'][userIndex]
                data[teamIndex]['team']['members'].pop(userIndex)
                data[teamIndex]['team']['members'].insert(0,saved_user)
                break

env = environ.Env()
environ.Env.read_env()

TEAM_APP_API_URL = env("TEAM_APP_API_URL")

def retrieve_calendar_data(user, sort_value):
    calendar_data = None
    api_response = None

    try:
        token = (str(user) + "AbsencePlanner").encode()
        token = hashlib.sha256(token).hexdigest()

        url = TEAM_APP_API_URL + "user/teams/"
        params = {
            "username": user.username,
            "sort": sort_value
        }
        headers = {"TEAMS-TOKEN": token}

        api_response = requests.get(url=url, params=params, headers=headers)
    except:
        print("API Failed to connect")
        return # Caller should handle the API error
    
    if api_response is not None and api_response.status_code == 200:
        calendar_data = api_response.json()
        sort_global_absences_by_logged_in_user(calendar_data, user)
    return calendar_data

def get_users_sharing_teams(username, user_model):
    teams = retrieve_calendar_data(user_model, None)
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
        token = (str(username) + "AbsencePlanner").encode()
        token = hashlib.sha256(token).hexdigest()

        url = TEAM_APP_API_URL + "user_exists/"
        params = {"username": username}
        headers = {"TEAMS-TOKEN": token}

        api_response = requests.get(url=url, params=params, headers=headers)
    except:
        print("API Failed to connect")
        return # Caller should handle the API error
    
    if api_response is not None and api_response.status_code == 200:
        user_exists = api_response.json()

    return user_exists

def is_team_app_running():
    team_app_running = False

    try:
        url = TEAM_APP_API_URL + "status_check"

        api_response = requests.get(url=url)
    except:
        print("API Failed to connect")
        return team_app_running # Caller should handle the API error
    
    if api_response is not None and api_response.status_code == 200:
        team_app_running = True
    
    return team_app_running