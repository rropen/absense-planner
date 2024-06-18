from ..models import UserProfile
from django.contrib.auth.models import User

from .teams_utils import get_users_sharing_teams
from .user_profile import get_user_id_from_username, get_userprofile_id_from_user_id

def check_for_lingering_switch_perms(username, action):
    """
    Check that discovers lingering switch permissions in the database and determines what to do with them.

    Mainly used to stop users from having switch perms when they don't share any teams.

    This check should be activated when the user leaves a team.

    Args:
    - `username` (`str`): Username of the user who left the team.
    - `action`: Function that is executed when redundant permissions (lingering switch perms) are discovered.
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
    
    process_user_usernames(username, usernames_given_permissions, users_sharing_teams, action)
    process_userprofile_usernames(username, userprofile_usernames_who_give_permissions, users_sharing_teams, action)

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

def process_user_usernames(selected_username, usernames_given_permissions, users_sharing_teams, action):
    """
    Looks through a list of usernames given permissions and users sharing teams and determines if they are redundant.

    Args:
    - `selected_username`: Username that is used to get the User ID and UserProfile ID of the user who triggered this function (the selected user).
    - `usernames_given_permissions`: List of usernames who have been given permission to switch with the selected user.
    - `users_sharing_teams`: List of unique usernames sharing teams with the user.
    - `action`: Function that is executed when redundant permissions are found in the list.
    """
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
        elif username not in users_sharing_teams:
            action(selected_userprofile_id, user_id)

def process_userprofile_usernames(selected_username, userprofile_usernames_who_give_permissions, users_sharing_teams, action):
    """
    Looks through a list of usernames who have given permissions and users sharing teams and determines if they are redundant.

    Args:
    - `selected_username`: Username that is used to get the User ID of the user who triggered this function (the selected user).
    - `userprofile_usernames_who_give_permissions`: List of usernames who have given permission for the selected user to switch with them.
    - `users_sharing_teams`: List of unique usernames sharing teams with the user.
    - `action`: Function that is executed when redundant permissions are found in the list.
    """
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
        elif username not in users_sharing_teams:
            action(userprofile_id, selected_user_id)

def remove_switch_permissions(userprofile_id, user_id):
    """
    Removes the switch permissions of a user from a user's profile settings.

    Args:
    - `userprofile_id`: The ID of the user who has given permissions.
    - `user_id`: The ID of the user whose permissions will be removed.
    """

    # Get instance of UserProfile that matches given ID
    try:
        userprofile = UserProfile.objects.get(id=userprofile_id)
    except:
        print("UserProfile not found in absence planner database using given ID")
        return

    # Get instance of User that matches given ID
    try:
        selected_user = User.objects.get(id=user_id)
    except:
        print("User not found in absence planner database using given ID")
        return

    userprofile.edit_whitelist.remove(selected_user)