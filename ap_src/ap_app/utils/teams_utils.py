# Third-party Libraries
import hashlib
import requests

# Environment
import environ

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
    
    if r is not None and r.status_code == 200:
        data = r.json()
    
    return data

def get_users_sharing_teams(current_user, user_model):
    teams = retrieve_calendar_data(user_model, None)
    if teams is None or teams == []: # The current_user is not in any teams
        return {} # Avoid error from iterating through None type

    users_sharing_teams = []
    for team in teams:
        team = team["team"]
        for member in team["members"]:
            username = member["user"]["username"]
            users_sharing_teams.append(username)
    users_sharing_teams = set(users_sharing_teams)
    users_sharing_teams.remove(current_user)
    # ^^^ Remove the user whos teams are being queried
    # as this will avoid conflicts.

    return users_sharing_teams