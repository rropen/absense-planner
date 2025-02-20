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

def retrieve_calendar_data(user, sortValue):
    data = None
    r = None

    try:
        token = (str(user) + "AbsencePlanner").encode()
        encryption = hashlib.sha256(token).hexdigest()
        r = requests.get(env("TEAM_DATA_URL") + "api/user/teams/?format=json&username={}&sort={}".format(user.username, sortValue), headers={"TEAMS-TOKEN": encryption})
    except:
        print("API Failed to connect")
        return # Caller should handle the API error
    
    if r is not None and r.status_code == 200:
        data = r.json()
        sort_global_absences_by_logged_in_user(data, user)
    return data

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