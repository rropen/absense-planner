from django import template
from ap_app.models import UserProfile

register = template.Library()


@register.filter(name="check_permissions")
def check_permissions(user, active_user):
    perm_list = UserProfile.objects.filter(user=user)[0].edit_whitelist.all()
    if active_user in perm_list:
        return True
    else:
        return False