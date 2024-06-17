# Models
from ..models import (UserProfile)
from django.contrib.auth.models import User

# Utils
from teams_utils import get_users_sharing_teams
from user_profile import get_user_id_from_username
from user_profile import get_userprofile_id_from_user_id

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
    process_userprofile_usernames(username, userprofile_usernames_who_give_permissions, users_sharing_teams)
    
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