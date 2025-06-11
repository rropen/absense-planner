from django import template

register = template.Library()


@register.simple_tag
def get_user_id(all_absences):
    if len(all_absences) > 0:   
        for x in all_absences:
            return x["User_ID"]