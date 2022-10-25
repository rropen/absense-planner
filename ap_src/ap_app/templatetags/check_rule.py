from django import template

register = template.Library()


@register.filter(name="check_rule")
def check_rule(rule):
    if "daily" in rule or "on" in rule or "each" in rule or "Date":
        return True
    return False
