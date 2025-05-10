from django import template

register = template.Library()


@register.simple_tag
def check_half_day(all_absences, year, month, day):
    if len(all_absences) > 0:
        for x in all_absences:
            date = x["date"]
            if date.year == year and date.month == month and date.day == day:
                if x["type"] == "MORNING":
                    return "M"
                elif x["type"] == "AFTERNOON":
                    return "A"
                else:
                    return "N"
