# Models
from ..models import (UserProfile)
from django.contrib.auth.models import User

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
