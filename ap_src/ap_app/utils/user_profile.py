# Models
from ..models import (UserProfile)
from django.contrib.auth.models import User

def get_user_id_from_username(selected_username):
    user_matching_username = User.objects.get(username=selected_username)
    user_id_of_user = int(user_matching_username.id)

    return user_id_of_user

def get_userprofile_id_from_user_id(user_id):
    userprofile_matching_user_id = UserProfile.objects.get(user_id=user_id)
    userprofile_id = int(userprofile_matching_user_id.id)

    return userprofile_id
