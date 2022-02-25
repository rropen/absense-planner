from django import template

register = template.Library()


@register.filter(name="check_day")
def check_day(list_, day):
    for x in list_:
        if x.day == day:
          return True
    return False