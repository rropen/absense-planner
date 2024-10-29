from django import template

register = template.Library()

@register.simple_tag
def is_webpage_active(request, url_name):
    current_url_name = request.resolver_match.url_name  # Get the current URL name

    # Define patterns for the absence tab
    absence_patterns = [
        "add", 
        "absence_edit", 
        "absence_delete", 
        "recurring_absence_delete", 
        "absence_click_add", 
        "absence_click_remove",
        "add_recurring",
        "recurring_absence_edit"
    ]

    # Define patterns for the team tab
    team_patterns = [
        "dashboard", 
        "create_team", 
        "join_team", 
        "api_team_calendar", 
        "edit_team"
    ]

    # Define patterns for the home tab
    home_patterns = [
        "index"
    ]

    print(url_name)
    # Check if the current URL name matches any absence patterns
    if current_url_name in absence_patterns and url_name in absence_patterns:
        return "active"
    
    # Check if the current URL name matches any home patterns
    if current_url_name in home_patterns and url_name in home_patterns:
        return "active"
    
    # Check if the current URL name matches any team patterns
    if current_url_name in team_patterns and url_name in team_patterns:
        return "active"

    return ""  # Return an empty string if no patterns match