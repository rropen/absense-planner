import requests
import environ

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (UserProfile)

from .calendarview import retrieve_calendar_data

env = environ.Env()
environ.Env.read_env()


# this check should be activated when the user leaves a team
@login_required
def check_for_lingering_switch_perms(request): # stops users from having switch perms when they don't share any teams
    user_edited = request.user.username
    users_with_perms = grab_users_with_perms(request)
    users_sharing_teams = grab_users_sharing_teams(request)
    # DEBUG CODE #
    print("DEBUG: Users with permissions:", users_with_perms)
    print("DEBUG: Users sharing teams:", users_sharing_teams)
    # DEBUG CODE #

    for user_with_perms in users_with_perms:
        if user_with_perms not in users_sharing_teams:
            print("Redundant permissions found for", user_with_perms + "!")
            #remove_switch_permissions(request, user_with_perms)

    # Example pseudocode implementation
    """
    SET user ID whose absences are being edited AS (int) user_ID_edited
    SET user IDs with permission to edit absences AS (list of int) user_IDs_with_perms
    SET user IDs who are in the same team as user_ID_edited AS (list of int) user_IDs_sharing_teams

    IF user_ID_edited_leave_team THEN
    FOR EACH (int) user_ID_with_perms FROM (list) user_IDs_with_perms DO
        IF user_ID_with_perms NOT IN user_IDs_sharing_teams THEN remove_permissions
    END FOREACH
    END IF
    """

# this check should be activated when giving switch permissions to a member in the profile settings
@login_required
def check_for_teams_in_common(request, user_being_given_perms): # this stops users from giving switch permissions to members not in a team
    users_sharing_teams = grab_users_sharing_teams(request)
    if user_being_given_perms not in users_sharing_teams:
        return False

    return True

@login_required
def grab_users_sharing_teams(request):
    teams = retrieve_calendar_data(request, None)
    print(teams)

    users_sharing_teams = []
    for team in teams:
        team = team["team"]
        print("Team name:", team["name"])
        print("Team members:", team["members"])
        for member in team["members"]:
            username = member["user"]["username"]
            print(member)
            users_sharing_teams.append(username)
    print(users_sharing_teams)

    return users_sharing_teams

@login_required
def grab_users_with_perms(request):
    current_username = request.user.username
    user_profiles_with_perms = UserProfile.objects.filter(edit_whitelist__username=current_username)
    user_ids_with_perms = user_profiles_with_perms.values_list("user_id", flat=True)
    user_ids_with_perms = list(user_ids_with_perms)

    usernames_with_perms = []
    for user_id in user_ids_with_perms:
        user_matching_user_id = User.objects.filter(id=user_id)
        username_matching_user_id = user_matching_user_id.values_list("username", flat=True)
        username_matching_user_id = str(username_matching_user_id[0])
        usernames_with_perms.append(username_matching_user_id)
    
    usernames_with_perms = set(usernames_with_perms)
    
    return usernames_with_perms

@login_required
def remove_switch_permissions(request, selected_username): # selected here meaning the user we want to remove perms from, current meaning the one sending the request
    current_username = request.user.username
    current_user_id = get_user_id_from_username(current_username)
    # DEBUG CODE #
    print("DEBUG: This is the username of the current user: ", current_username)
    print("DEBUG: This is the user id of the current user: ", current_user_id)
    # DEBUG CODE #
    current_userprofile = UserProfile.objects.get(user_id=current_user_id)

    # selected_username
    selected_user = User.objects.get(username=selected_username)

    current_userprofile.edit_whitelist.remove(selected_user)

def get_user_id_from_username(selected_username):
    user_matching_user_id = User.objects.filter(username=selected_username)
    user_id_matching_username = user_matching_user_id.values_list("id", flat=True)
    user_id_matching_username = int(user_id_matching_username[0])

    return user_id_matching_username