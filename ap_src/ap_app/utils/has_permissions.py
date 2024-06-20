# from ap_app.models import UserProfile

# def has_permissions(user,active_user):
#     perm_list = UserProfile.objects.filter(user__username=user["user"]["username"])
#     if perm_list.exists():
#         if active_user in perm_list[0].edit_whitelist.all():
#             return True
#         else:
#             return False
    
#     return False
