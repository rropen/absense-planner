from django import template

register = template.Library()


@register.simple_tag
def check_absences(list_, year, month, day):
    for x in list_:
        if x.month == month and x.day == day and x.year == year:
            return True
    return False