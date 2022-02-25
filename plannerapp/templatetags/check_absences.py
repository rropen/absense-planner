from django import template

register = template.Library()


@register.filter(name="check_absences")
def check_absences(list_, month, day):
    for x in list_:
        if x.month == month and x.day == day:
          return True
    return False