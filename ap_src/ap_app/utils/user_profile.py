from ..models import UserProfile
from django.contrib.auth.models import User


def get_user_id_from_username(selected_username):
    try:
        user_matching_username = User.objects.get(username=selected_username)
        user_id_of_user = int(user_matching_username.id)
    except:
        print("Valid User ID does not exist in database")
        return

    return user_id_of_user


def get_userprofile_id_from_user_id(user_id):
    try:
        userprofile_matching_user_id = UserProfile.objects.get(user_id=user_id)
        userprofile_id = int(userprofile_matching_user_id.id)
    except:
        print("Valid UserProfile ID does not exist in database")
        return

    return userprofile_id
