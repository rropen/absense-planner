from ..models import UserProfile
from django.contrib.auth.models import User

from .teams_utils import get_users_sharing_teams
from .user_profile import get_user_id_from_username, get_userprofile_id_from_user_id

def check_for_lingering_switch_perms(username):
    """
    Stops users from having switch perms when they don't share any teams.

    This check should be activated when the user leaves a team.

    Args:
        username (str): The username of the user who left the team.
    """

    user_id = get_user_id_from_username(username)
    userprofile_id = get_userprofile_id_from_user_id(user_id)
    if (user_id is None) or (userprofile_id is None):
        return

    usernames_given_permissions, userprofile_usernames_who_give_permissions = get_associated_permissions(username, userprofile_id, user_id)
    if (usernames_given_permissions is None) or (userprofile_usernames_who_give_permissions is None):
        return

    user = User.objects.get(id=user_id)
    users_sharing_teams = get_users_sharing_teams(username, user)
    if users_sharing_teams is None:
        return # Caller should handle error
    
    process_user_usernames(username, usernames_given_permissions, users_sharing_teams)
    process_userprofile_usernames(username, userprofile_usernames_who_give_permissions, users_sharing_teams)

def get_associated_permissions(current_user, selected_userprofile_id, selected_user_id):
    usernames_given_permissions = set(User.objects.filter(permissions=selected_userprofile_id).values_list("username", flat=True))
    try:
        usernames_given_permissions.remove(current_user)
    except:
        print("User does not exist in absence planner database")
        return None, None # Caller should handle error

    userprofile_ids_who_give_permissions = UserProfile.objects.filter(edit_whitelist=selected_user_id).values_list(flat=False)
    userprofile_usernames_who_give_permissions = set()
    for userprofile_id in userprofile_ids_who_give_permissions:
        try:
            user = User.objects.get(userprofile=userprofile_id)
        except:
            print("User matching UserProfile ID not found")
            return None, None
        current_username = user.get_username()
        userprofile_usernames_who_give_permissions.add(current_username)

    try:
        userprofile_usernames_who_give_permissions.remove(current_user)
    except:
        print("Current user not found in absence planner database")
        return None, None

    return usernames_given_permissions, userprofile_usernames_who_give_permissions

def process_user_usernames(selected_username, usernames_given_permissions, users_sharing_teams): # User here is referring to the "User Model"
    selected_user_id = get_user_id_from_username(selected_username)
    selected_userprofile_id = get_userprofile_id_from_user_id(selected_user_id)
    if (selected_user_id is None) or (selected_userprofile_id is None):
        print("UserProfile ID does not exist in absence planner database")
        return
    for username in usernames_given_permissions:
        user_id = get_user_id_from_username(username)
        if user_id is None:
            print("Referenced User ID does not exist in absence planner database")
            return
        #elif username not in users_sharing_teams:
            # This has been left here, commented out for when the algorithm is actually implemented
            # for removing permissions using the data printed
            #print("Redundant permissions found from", selected_userprofile_id, "given to", user_id)

def process_userprofile_usernames(selected_username, userprofile_usernames_who_give_permissions, users_sharing_teams): # User here is referring to the "User Model"
    selected_user_id = get_user_id_from_username(selected_username)
    if selected_user_id is None:
        print("User ID does not exist in absence planner database")
        return
    for username in userprofile_usernames_who_give_permissions:
        user_id = get_user_id_from_username(username)
        userprofile_id = get_userprofile_id_from_user_id(user_id)
        if (user_id is None) or (userprofile_id is None):
            print("UserProfile ID does not exist in absence planner database")
            return
        #elif username not in users_sharing_teams:
            # This has been left here, commented out for when the algorithm is actually implemented
            # for removing permissions using the data printed
            #print("Redundant permissions found from", userprofile_id, "given to", selected_user_id)