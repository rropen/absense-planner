import environ
from django.http import HttpResponse, HttpRequest
from .utils.teams_utils import is_team_app_running
from django.template import loader


env = environ.Env()
environ.Env.read_env()
DEBUG = env("DEBUG") == "True" # environment variables are read as strings so we compare to "True"

def status_check_middleware(get_response):
    """
    Checks to see if the Team App is running, otherwise it should raise a 503 error.
    """

    def middleware(request):
        team_app_running = is_team_app_running()
        asset_request = is_asset_request(request)

        if (not asset_request):
            if (not team_app_running):
                print("Team App is not running. 503 error will persist until it is.")
        
                if (DEBUG):
                    # Send to developer-specific error page. Do not throw a Django error to get 503 error.
                    content = loader.render_to_string("team-app-not-running.html")
                    return HttpResponse(content, status=503)
                else:
                    context = {"error_message": "The Absence Planner relies on the Team App API which is currently unavailable, and so you should contact the developers with this information."}
                    content = loader.render_to_string("503.html", context=context)
                    return HttpResponse(content, status=503)


        response = get_response(request)

        return response

    return middleware

def is_asset_request(request:HttpRequest):
    """
    Checks the file extension of the request and compares it to a list of file formats used for assets.
    This is used when throwing a 503 error for requests as it should still allow the loading of asset
    requests for a user-friendly 503 page.
    """

    is_asset_request = False
    if "." in request.path:
        file_extension = request.path.split(".")[-1]

        asset_file_formats = ["js", "css", "mp3", "ico"]
        is_asset_request = file_extension in asset_file_formats

    return is_asset_request