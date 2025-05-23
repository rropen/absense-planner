import environ
from django.http import HttpResponse, HttpRequest
from .utils.teams_utils import is_team_app_running
from django.template import loader
from django.template import Template, Context


env = environ.Env()
environ.Env.read_env()

def status_check_middleware(get_response):
    """
    Checks to see if the Team App is running, otherwise it should raise a 503 error.
    """

    def middleware(request):
        team_app_running = is_team_app_running()
        asset_request = is_asset_request(request)

        if ((not team_app_running) and (not asset_request)):
            print("Team App is not running. 503 error will persist until it is.")
            context = {"error_message": "The Absence Planner relies on the Team App API which is currently unavailable, and so you should contact the developers with this information."}
            content = loader.render_to_string("503.html", context=context)
            return HttpResponse(content, status=503)

        response = get_response(request)

        return response

    return middleware

def is_asset_request(request:HttpRequest):
    is_asset_request = False
    if "." in request.path:
        file_extension = request.path.split(".")[-1]
        print(file_extension)

        asset_file_formats = ["js", "css", "mp3"]
        is_asset_request = file_extension in asset_file_formats

    return is_asset_request