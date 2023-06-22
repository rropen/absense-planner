from django import template
from ap_app.models import UserProfile

register = template.Library()


@register.filter(name="check_permissions")
def check_permissions(user, active_user):
    try:
        userprofile: UserProfile = UserProfile.objects.filter(user=active_user)[0]
    except IndexError:
        print("Error")
    
    if len(userprofile.edit_whitelist.values_list().filter(id=user.id)) > 0:
        return True
    else:
        return False