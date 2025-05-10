from django.conf import settings  # This will import the settings file that django uses.

import environ

env = environ.Env()
environ.Env.read_env()


def production(request):  # Function that will return the PRODUCTION_UI value.
    return {"PRODUCTION_UI": settings.PRODUCTION_UI}


def info(request):
    return {"VERSION": settings.VERSION}


def team_api_data(request):
    return {"TEAM_DATA_URL": env("TEAM_DATA_URL")}


def url_splitter(request):
    url_parts = request.path.split("/")
    return {"subdirectory_name": url_parts[1]}
