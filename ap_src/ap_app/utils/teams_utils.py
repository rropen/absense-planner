import hashlib
import requests

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
        return # Caller should handle the API error
    
    if r is not None and r.status_code == 200:
        data = r.json()
        for teamA in range(len(data)):
            def fetch_User(userIndex):
                usersZ = data[teamA]['team']['members'][userIndex]['user']['id']
                return usersZ
            for userA in range(len(data[teamA]['team']['members'])):
                if user.id == fetch_User(int(userA)):
                    saved_user = data[teamA]['team']['members'][userA]
                    data[teamA]['team']['members'].pop(userA)
                    data[teamA]['team']['members'].insert(0,saved_user)
                    break
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