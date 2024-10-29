from django import template

register = template.Library()

# Define URL patterns for each tab in a dictionary
patterns = {
    "absence": [
        "add", "absence_edit", "absence_delete", "recurring_absence_delete", 
        "absence_click_add", "absence_click_remove", "add_recurring", "recurring_absence_edit"
    ],
    "teams": [
        "dashboard", "create_team", "join_team", "api_team_calendar", "edit_team"
    ],
    "home": ["index"]
}

@register.simple_tag
def is_webpage_active(request, url_name):
    current_url_name = request.resolver_match.url_name  # Get the current URL name

    # Check if current URL name matches any of the patterns
    for pattern in patterns.values():
        if current_url_name in pattern and url_name in pattern:
            return "active"

    return ""  # Return an empty string if no patterns match
