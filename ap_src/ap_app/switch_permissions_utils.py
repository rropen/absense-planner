import requests
import environ

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (UserProfile)

from .calendarview import retrieve_calendar_data

env = environ.Env()
environ.Env.read_env()


# this check should be activated when the user leaves a team
def check_for_lingering_switch_perms(username): # stops users from having switch perms when they don't share any teams
    user_id = get_user_id_from_username(username)
    print("user_id:", user_id)
    userprofile_id = get_userprofile_id_from_user_id(user_id)
    print("userprofile_id:", userprofile_id)

    usernames_given_permissions, userprofile_usernames_who_give_permissions = get_associated_permissions(username, userprofile_id, user_id)

    user = User.objects.get(id=user_id)
    users_sharing_teams = get_users_sharing_teams(username, user)
    print("users_sharing_teams:", users_sharing_teams)
    
    process_user_usernames(username, usernames_given_permissions, users_sharing_teams)
    
    #current_username = username
    #users_with_perms = grab_users_with_perms(current_username)
    #users_sharing_teams = grab_users_sharing_teams(current_username)
    ## DEBUG CODE #
    #print("DEBUG: Users with permissions:", users_with_perms)
    #print("DEBUG: Users sharing teams:", users_sharing_teams)
    ## DEBUG CODE #
    #
    #for user_with_perms in users_with_perms:
    #    if user_with_perms not in users_sharing_teams:
    #        print("Redundant permissions found for", user_with_perms + "!")
    #        #remove_switch_permissions(request, user_with_perms)

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

## this check should be activated when giving switch permissions to a member in the profile settings
#def check_for_teams_in_common(current_user, user_being_given_perms): # this stops users from giving switch permissions to members not in a team
#    users_sharing_teams = grab_users_sharing_teams(current_user)
#    if user_being_given_perms not in users_sharing_teams:
#        return False
#
#    return True
#
def get_users_sharing_teams(current_user, user_model):
    teams = retrieve_calendar_data(user_model, None)
    if teams is None or teams == []: # The current_user is not in any teams
        return {} # Avoid error from iterating through None type

    users_sharing_teams = []
    for team in teams:
        team = team["team"]
        #print("Team name:", team["name"])
        #print("Team members:", team["members"])
        for member in team["members"]:
            username = member["user"]["username"]
            users_sharing_teams.append(username)
    users_sharing_teams = set(users_sharing_teams)
    users_sharing_teams.remove(current_user)
    # ^^^ Remove the user whos teams are being queried
    # as this will avoid conflicts.

    return users_sharing_teams

#def grab_users_with_perms(username):
#    user_profiles_with_perms = UserProfile.objects.filter(edit_whitelist__username=username)
#    user_ids_with_perms = user_profiles_with_perms.values_list("user_id", flat=True)
#    user_ids_with_perms = list(user_ids_with_perms)
#
#    usernames_with_perms = []
#    for user_id in user_ids_with_perms:
#        user_matching_user_id = User.objects.filter(id=user_id)
#        username_matching_user_id = user_matching_user_id.values_list("username", flat=True)
#        username_matching_user_id = str(username_matching_user_id[0])
#        usernames_with_perms.append(username_matching_user_id)
#    
#    usernames_with_perms = set(usernames_with_perms)
#    
#    return usernames_with_perms
#
#@login_required
#def remove_switch_permissions(request, selected_username): # selected here meaning the user we want to remove perms from, current meaning the one sending the request
#    current_username = request.user.username
#    current_user_id = get_user_id_from_username(current_username)
#    # DEBUG CODE #
#    print("DEBUG: This is the username of the current user: ", current_username)
#    print("DEBUG: This is the user id of the current user: ", current_user_id)
#    # DEBUG CODE #
#    current_userprofile = UserProfile.objects.get(user_id=current_user_id)
#
#    # selected_username
#    selected_user = User.objects.get(username=selected_username)
#
#    current_userprofile.edit_whitelist.remove(selected_user)
#
def get_user_id_from_username(selected_username):
    user_matching_user_id = User.objects.filter(username=selected_username)
    user_id_matching_username = user_matching_user_id.values_list("id", flat=True)
    user_id_matching_username = int(user_id_matching_username[0])

    return user_id_matching_username

def get_userprofile_id_from_user_id(user_id):
    userprofile_matching_user_id = UserProfile.objects.filter(user_id=user_id)
    userprofile_id_matching_user_id = userprofile_matching_user_id.values_list("id", flat=True)
    userprofile_id_matching_user_id = int(userprofile_id_matching_user_id[0])

    return userprofile_id_matching_user_id

def get_associated_permissions(current_user, selected_userprofile_id, selected_user_id):
    usernames_given_permissions = set(User.objects.filter(permissions=selected_userprofile_id).values_list("username", flat=True))
    usernames_given_permissions.remove(current_user)
    print("User usernames given permissions:", usernames_given_permissions)

    userprofile_ids_who_give_permissions = UserProfile.objects.filter(edit_whitelist=selected_user_id).values_list(flat=False)
    userprofile_usernames_who_give_permissions = []
    for userprofile_id in userprofile_ids_who_give_permissions:
        user = User.objects.get(userprofile=userprofile_id)
        current_username = user.get_username()
        userprofile_usernames_who_give_permissions.append(current_username)
    userprofile_usernames_who_give_permissions = set(userprofile_usernames_who_give_permissions)
    userprofile_usernames_who_give_permissions.remove(current_user)
    print("UserProfile usernames who give permissions:", userprofile_usernames_who_give_permissions)

    return usernames_given_permissions, userprofile_usernames_who_give_permissions

def process_user_usernames(selected_username, usernames_given_permissions, users_sharing_teams): # User here is referring to the "User Model"
    selected_user_id = get_user_id_from_username(selected_username)
    selected_userprofile_id = get_userprofile_id_from_user_id(selected_user_id)
    for username in usernames_given_permissions:
        user_id = get_user_id_from_username(username)
        if username not in users_sharing_teams:
            print("Redundant permissions found from", selected_userprofile_id, "given to", user_id)

def process_userprofile_usernames(selected_username, userprofile_usernames_who_give_permissions, users_sharing_teams): # User here is referring to the "User Model"
    selected_user_id = get_user_id_from_username(selected_username)
    for username in userprofile_usernames_who_give_permissions:
        user_id = get_user_id_from_username(username)
        userprofile_id = get_userprofile_id_from_user_id(user_id)
        if username not in users_sharing_teams:
            print("Redundant permissions found from", userprofile_id, "given to", selected_user_id)