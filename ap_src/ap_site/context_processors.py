from django.conf import \
    settings  # This will import the settings file that django uses.

import environ

env = environ.Env()
environ.Env.read_env()

# Environment Variables

def production(request):
    """
    Returns the PRODUCTION_UI environment variable's value.
    """
    return {'PRODUCTION_UI': settings.PRODUCTION_UI}

def info(request):
    """
    Returns the VERSION environment variable's value.
    """
    return {'VERSION': settings.VERSION}

def team_api_data(request):
    """
    Returns the TEAM_DATA_URL environment variable's value.
    """
    return {'TEAM_DATA_URL': env("TEAM_DATA_URL")}

def debug(request):
    """
    Returns the DEBUG environment variable's value.
    """
    return {'DEBUG': env("DEBUG")}

def url_splitter(request):
    """
    Utility that splits URL for use in the header bar.
    """
    url_parts = request.path.split("/")
    return {"subdirectory_name": url_parts[1]}