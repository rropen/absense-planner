"""
Contains views that handle team-related logic, connecting to the API whilst utilising team utility functions.

Errors are handled here by passing Django messages up through views to templates so API errors can be displayed to the user.
"""

import environ
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from ..forms import CreateTeamForm
from ..models import Role
from ..utils.teams_utils import retrieve_team_member_data, favourite_team, get_user_token_from_request, get_users_teams
from ..utils.switch_permissions import check_for_lingering_switch_perms, remove_switch_permissions
from ..utils.errors import print_messages, derive_http_error_message
from requests import Session
from requests import HTTPError, ConnectionError, RequestException
env = environ.Env()
environ.Env.read_env()
TEAM_APP_API_URL = env("TEAM_APP_API_URL")
TEAM_APP_API_KEY = env("TEAM_APP_API_KEY")
TEAM_APP_API_TIMEOUT = float(env("TEAM_APP_API_TIMEOUT"))
# Use the session object from the Python requests library to send requests and pool the connection resources.
# Without this, the requests sent to the API are EXTREMELY SLOW.
session = Session()
@login_required
def teams_dashboard(request) -> render:
    """
    Renders the view that shows the user a selection of teams they are in with
    the associated options.

    Also handles favouriting of teams through POST requests.
    """
    user_token = get_user_token_from_request(request)

    api_specific_method = request.POST.get("method") # Using .get will not raise an error
    if (api_specific_method == "favourite"):
        try:
            team_id = request.POST["team"]
        except KeyError:
            error = "Error - a team was not provided so it could not be favourited."
            debug = "Error: Team ID was not found in request so it cannot be favourited."
            print_messages(request, error=error, debug=debug)
        except Exception as exception:
            error = "Error - could not obtain the team you requested due to an unknown error" \
                    "so it could not be favourited."
            debug = "Error: Cannot obtain Team ID from request for favouriting. Exception: " + str(exception)
            print_messages(request, error=error, debug=debug)
        else:
            try:
                error, debug, success = None, None, None
                favourite_team(user_token, team_id)
            except HTTPError as exception:
                error = "Error in favouriting team - " + derive_http_error_message(exception)
            except ConnectionError as exception:
                error = "Error - could not favourite the team you requested due to a connection error."
                debug = "Error: Could not connect to the API to favourite a team. Exception: " + str(exception)
            except RequestException as exception:
                error = "Error - could not favourite the team you requested due to an unknown error."
                debug = "Error: Could not send a request to the API to favourite a team. Exception: " + str(exception)
            else:
                success = "Favourited team successfully."
            finally:
                print_messages(request, success=success, error=error, debug=debug)

    try:
        error, debug, success = None, None, None
        users_teams = get_users_teams(None, user_token)
    except HTTPError as exception:
        error = "Error in fetching your joined teams - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        error = "Error - could not fetch the teams you are in due to a connection error."
        debug = "Error: Could not connect to the API to fetch a user's joined teams. Exception: " + str(exception)
    except RequestException as exception:
        error = "Error - could not fetch the teams you are in due to an unknown error."
        debug = "Error: Could not send a request to the API to fetch a user's joined teams. Exception: " + str(exception)
    finally:
        print_messages(request, success=success, error=error, debug=debug)

    if (error):
        users_teams = False
    elif (len(users_teams) == 0):
        users_teams = False

    return render(
        request,
        "teams/dashboard.html",
        {"teams": users_teams},
    )
@login_required
def leave_team(request):
    """
    Leaves a team and removes lingering switch permissions.
    """
    username = request.user.username
    user_token = get_user_token_from_request(request)

    try:
        team_id = request.POST["team_id"]
    except KeyError:
        error = "Error - a team was not provided so it could not be left."
        debug = "Error: Team ID was not found in request so it cannot be left."
        print_messages(request, error=error, debug=debug)

        return redirect(reverse("dashboard")) # Return early because there is no Team ID to use
    except Exception as exception:
        error = "Error - could not obtain the team you requested due to an unknown error" \
                "so it could not be left."
        debug = "Error: Cannot obtain Team ID from request for leaving. Exception: " + str(exception)
        print_messages(request, error=error, debug=debug)

        return redirect(reverse("dashboard")) # Return early because there is no Team ID to use

    url = TEAM_APP_API_URL + "manage/"
    data = {
        "team": team_id
    }
    params = {
        "method": "leave"
    }
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }
    try:
        error, debug, success, warning = None, None, None, None
        session.post(url=url, data=data, params=params, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
    except HTTPError as exception:
        error = "Error in leaving team - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        error = "Error - could not leave the team you requested due to a connection error."
        debug = "Error: Could not connect to the API to leave a team. Exception: " + str(exception)
    except RequestException as exception:
        error = "Error - could not leave the team you requested due to an unknown error."
        debug = "Error: Could not send a request to the API to leave a team. Exception: " + str(exception)
    else:
        success = "Left team successfully."
        # Remove lingering switch permissions upon success
        try:
            check_for_lingering_switch_perms(username, remove_switch_permissions, user_token)
        except Exception as exception:
            warning = "Warning - could not remove unnecessary switch permissions."
            debug = warning + " Exception: " + str(exception)
    finally:
        print_messages(request, success=success, error=error, debug=debug, warning=warning)

    return redirect(reverse("dashboard")) # Redirect back to the list of joined teams
@login_required
def create_team(request:HttpRequest) -> render:
    user_token = get_user_token_from_request(request)
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            # Gets the created team and "Owner" Role and creates a Link between
            # the user and their team.
            # Send a POST request to the API instead of handling the usual model logic,
            # so that the created team is stored on the Team App instead of the Absence Planner.
            url = TEAM_APP_API_URL + "teams/"
            data = request.POST # This is the data sent by the user in the CreateTeamForm
            headers = {
                "Authorization": TEAM_APP_API_KEY,
                "User-Token": user_token
            }

            try:
                error, debug, success = None, None, None
                context = None
                api_response = session.post(url=url, data=data, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
                api_response.raise_for_status()
            except HTTPError as exception:
                error = "Error in creating a team - " + derive_http_error_message(exception)
                if exception.response.status_code == 400:
                    context = {"form": form}
                    if api_response.json()["name"] is not None:
                        context["message"] = "That team name already exists"
            except ConnectionError as exception:
                error = "Error - could not create the team due to a connection error."
                debug = "Error: Could not connect to the API to create a team. Exception: " + str(exception)
            except RequestException as exception:
                error = "Error - could not create the team due to an unknown error."
                debug = "Error: Could not send a request to the API to create a team. Exception: " + str(exception)
            finally:
                print_messages(request, success=success, error=error, debug=debug)

            if not error:
                return redirect("/teams/api-calendar/" + str(api_response.json()["id"]))
            else:
                return render(request, "teams/create_team.html", context=context)
    else:
        form = CreateTeamForm()

    return render(
        request,
        "teams/create_team.html",
        {
            "form": form,
        },
    )
@login_required
def join_team(request) -> render:
    """Renders page with all teams the user is not currently in and handles joining of specific teams."""
    # Filtering by team name
    
    teams = None
    api_response = None
    user_token = get_user_token_from_request(request)

    if (request.method == "POST"):
        warning, debug = None, None
        try:
            method = request.POST["method"]
        except KeyError:
            warning = "Warning - a method was not provided so no team-related action could be carried out."
            debug = "Warning: method was not found in request so no action took place."
            print_messages(request, warning=warning, debug=debug)
        except Exception as exception:
            warning = "Warning - could not obtain the team you requested due to an unknown error" \
                    "so it could not be left."
            debug = "Warning: Cannot obtain Team ID from request for leaving. Exception: " + str(exception)
            print_messages(request, warning=warning, debug=debug)
        else:
            # Pass through data to the Team App API

            warning, debug = None, None
            if (method == "join"):
                try:
                    team_id = request.POST["team_id"]
                except KeyError:
                    error = "Error - a team was not provided so it could not be joined."
                    debug = "Error: Team ID was not found in request so it cannot be joined."
                    print_messages(request, error=error, debug=debug)
                except Exception as exception:
                    error = "Error - could not obtain the team you requested due to an unknown error" \
                            "so it could not be joined."
                    debug = "Error: Cannot obtain Team ID from request for joining. Exception: " + str(exception)
                    print_messages(request, error=error, debug=debug)

                data = {
                    "team": team_id
                }
                url = TEAM_APP_API_URL + "manage/"
                params = {"method": "join"}
                headers = {
                    "Authorization": TEAM_APP_API_KEY,
                    "User-Token": user_token
                }

                error, debug, success = None, None, None
                try:
                    api_response = session.post(
                        url=url,
                        data=data,
                        params=params,
                        headers=headers,
                        timeout=TEAM_APP_API_TIMEOUT
                    )
                    api_response.raise_for_status()
                except HTTPError as exception:
                    error = "Error in joining the team - " + derive_http_error_message(exception)
                except ConnectionError as exception:
                    error = "Error - could not join the team due to a connection error."
                    debug = "Error: Could not connect to the API for a user to join a team. Exception: " + str(exception)
                except RequestException as exception:
                    error = "Error - could not join the team due to an unknown error."
                    debug = "Error: Could not send a request to the API for a user to join a team. Exception: " + str(exception)
                else:
                    success = "Successfully joined team."
                finally:
                    print_messages(request, success=success, error=error, debug=debug)
            else:
                warning = "Warning - the method provided was not valid so no team-related action could be carried out."
                debug = "Error: method found in request was not valid so no action took place."
                print_messages(request, warning=warning, debug=debug)

    url = TEAM_APP_API_URL + "teams/"
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }

    error, debug, success = None, None, None
    teams = None
    try:
        api_response = session.get(url=url, headers=headers, timeout=TEAM_APP_API_TIMEOUT)
        api_response.raise_for_status()
    except HTTPError as exception:
        error = "Error in fetching teams that are available to join - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        error = "Error - could not fetch teams that are available to join due to a connection error."
        debug = "Error: Could not connect to the API to fetch a user's teams that they are not in. Exception: " + str(exception)
    except RequestException as exception:
        error = "Error - could not fetch teams that are available to join due to an unknown error."
        debug = "Error: Could not send a request to the API to fetch a user's teams that they are not in. Exception: " + str(exception)
    else:
        if api_response is not None:
            teams = api_response.json()
    finally:
        print_messages(request, success=success, error=error, debug=debug)

    return render(
        request,
        "teams/join_team.html",
        {
            "teams": teams,
        },
    )

@login_required
def edit_team(request:HttpRequest, id):
    """
    Renders the page that allows owners of a team to modify different properties of that team.

    Also handles editing of a team's name and description.
    """

    form = CreateTeamForm()

    if not id:
        error = "Error - a team was not provided so it could not be edited."
        debug = "Error: Team ID was not found in request so it cannot be edited."
        print_messages(request, error=error, debug=debug)

        return redirect(reverse("dashboard")) # Return early because there is no Team ID to use

    user_token = get_user_token_from_request(request)

    try:
        error, debug = None, None
        users_teams = get_users_teams(None, user_token)
    except HTTPError as exception:
        error = "Error in fetching your joined teams - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        error = "Error - could not fetch the teams you are in due to a connection error, so we could not validate if the selected team exists for editing."
        debug = "Error: Could not connect to the API to fetch a user's joined teams so could not validate a team for editing. Exception: " + str(exception)
    except RequestException as exception:
        error = "Error - could not fetch the teams you are in due to an unknown error, so we could not validate if the selected team exists for editing."
        debug = "Error: Could not send a request to the API to fetch a user's joined teams so could not validate a team for editing.  Exception: " + str(exception)
    finally:
        if (error):
            print_messages(request, error=error, debug=debug)

            return redirect(reverse("dashboard")) # Return early because there is no Team ID to use
    
    team_ids = set()
    team_counter = 0
    for team in users_teams:
        current_team_id = users_teams[team_counter]["team"]["id"]
        team_ids.add(current_team_id)
        team_counter += 1
    if id not in team_ids:
        error = "Error - that team does not exist amongst your joined teams so you cannot edit it."
        debug = "Error: Team ID not among the Team IDs listed in user's joined teams. User's joined teams: " + str(users_teams)

        if (error):
            print_messages(request, error=error, debug=debug)

            return redirect(reverse("dashboard")) # Return early because there is no Team ID to use

    try:
        warning, debug = None, None
        api_data = retrieve_team_member_data(id, user_token)
    except HTTPError as exception:
        warning = "Warning - Error in fetching information about that team - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        warning = "Warning - could not fetch information about that team due to a connection error."
        debug = "Error: Could not connect to the API to fetch the data about a specific team so could not display them during team editing. Exception: " + str(exception)
    except RequestException as exception:
        warning = "Warning - could not fetch information about that team due to an unknown error."
        debug = "Error: Could not send a request to the API to fetch the data about a specific team so could not display them during team editing. Exception: " + str(exception)
    finally:
        print_messages(request, warning=warning, debug=debug)

    if (not warning):
        team = api_data[0]
        initial_data = {
            "name": team["name"],
            "description": team["description"] 
        }
        form = CreateTeamForm(initial=initial_data) # Reuse the form used for creating a team

        current_user = request.user.username

        is_owner = any(
            member["user"]["username"] == current_user and
            member["user"].get("role_info", {}).get("role", "").lower() == "owner"
            for member in api_data[0]["members"]
        )

        if not is_owner:
            raise PermissionDenied
    else:
        initial_data = {
            "name": None,
            "description": None
        }

    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            url = TEAM_APP_API_URL + "teams/"
            params = {"method": "edit"}
            data = {
                **request.POST,
                "id": id
            }
            headers = {
                "Authorization": TEAM_APP_API_KEY,
                "User-Token": user_token
            }

            error, debug, success = None, None, None
            try:
                api_response = session.post(
                    url=url,
                    params=params,
                    data=data,
                    headers=headers,
                    timeout=TEAM_APP_API_TIMEOUT
                )
                api_response.raise_for_status()
            except HTTPError as exception:
                error = "Warning - Error in editing the team - " + derive_http_error_message(exception)
            except ConnectionError as exception:
                error = "Warning - could not edit the team due to a connection error."
                debug = "Error: Could not connect to the API to edit a team. Exception: " + str(exception)
            except RequestException as exception:
                error = "Warning - could not edit the team due to an unknown error."
                debug = "Error: Could not send a request to the API to edit a team. Exception: " + str(exception)
            else:
                success = "Edited team successfully."
            finally:
                print_messages(request, error=error, debug=debug, success=success)

            # Get the updated API data again after authorising the user and editing the team
            try:
                warning, debug = None, None
                api_data = retrieve_team_member_data(id, user_token)
            except HTTPError as exception:
                warning = "Warning - Error in fetching members of that team - " + derive_http_error_message(exception)
            except ConnectionError as exception:
                warning = "Warning - could not fetch the members of that team due to a connection error."
                debug = "Error: Could not connect to the API to fetch the members of a specific team so could not display them during team editing. Exception: " + str(exception)
            except RequestException as exception:
                warning = "Warning - could not fetch the members of that team due to an unknown error."
                debug = "Error: Could not send a request to the API to fetch the members of a specific team so could not display them during team editing. Exception: " + str(exception)
            finally:
                print_messages(request, warning=warning, debug=debug)

    roles = Role.objects.all()
    if (not warning):
        team = api_data[0]
    else:
        team = None

    return render(
        request,
        "teams/edit_team.html",
        {
            "team": team,
            "roles": roles,
            "form": form
        }
    )

@login_required
def delete_team(request:HttpRequest):
    """
    Deletes a team and, if successful, checks for lingering switch permissions and deletes them, and
    then redirects back to the list of joined teams.
    """

    user_token = get_user_token_from_request(request)

    error, debug = None, None
    try:
        team_id = request.POST["team_id"]
    except KeyError:
        error = "Error - a team was not provided so it could not be deleted."
        debug = "Error: Team ID was not found in request so it cannot be deleted."
        print_messages(request, error=error, debug=debug)
    except Exception as exception:
        error = "Error - could not obtain the team you requested due to an unknown error" \
                "so it could not be deleted."
        debug = "Error: Cannot obtain Team ID from request for deleting. Exception: " + str(exception)
        print_messages(request, error=error, debug=debug)
    
    if (error):
        return redirect("dashboard") # Redirect back to the list of joined teams

    url = TEAM_APP_API_URL + "teams/"
    data = {
        "id": team_id
    }
    params = {
        "method": "delete"
    }
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }

    error, debug, warning, success = None, None, None, None
    try:
        api_response = session.post(
            url=url,
            data=data,
            params=params,
            headers=headers,
            timeout=TEAM_APP_API_TIMEOUT
        )
        api_response.raise_for_status()
    except HTTPError as exception:
        error = "Warning - Error in deleting the team - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        error = "Warning - could not delete the team due to a connection error."
        debug = "Error: Could not connect to the API to delete a team. Exception: " + str(exception)
    except RequestException as exception:
        error = "Warning - could not delete the team due to an unknown error."
        debug = "Error: Could not send a request to the API to delete a team. Exception: " + str(exception)
    else:
        success = "Deleted team successfully."
        # Remove lingering switch permissions upon success
        try:
            check_for_lingering_switch_perms(request.user.username, remove_switch_permissions, user_token)
        except Exception as exception:
            warning = "Warning - could not remove unnecessary switch permissions."
            debug = warning + " Exception: " + str(exception)
    finally:
        print_messages(request, error=error, debug=debug, success=success, warning=warning)
        if (error):
            return redirect("edit_team", id=team_id)
        else:
            return redirect("dashboard") # Redirect back to the list of joined teams

@login_required
def transfer_ownership(request):
    """
    Transfers ownership of a team to a new user.
    """
    user_token = get_user_token_from_request(request)

    if request.method != "POST":
        error = "Invalid request method."
        print_messages(request, error=error)
        return redirect("dashboard")

    try:
        team_id = request.POST["team_id"]
        new_owner = request.POST["new_owner"]
    except KeyError:
        error = "Error - required data (team_id or new_owner) not provided."
        debug = "KeyError: team_id or new_owner missing from POST data."
        print_messages(request, error=error, debug=debug)
        return redirect("dashboard")

    url = TEAM_APP_API_URL + "manage/"
    data = {
        "team": team_id,
        "new_owner": new_owner
    }
    params = {
        "method": "transfer_ownership"
    }
    headers = {
        "Authorization": TEAM_APP_API_KEY,
        "User-Token": user_token
    }

    try:
        error, debug, success = None, None, None
        response = session.post(
            url=url,
            data=data,
            params=params,
            headers=headers,
            timeout=TEAM_APP_API_TIMEOUT
        )
        response.raise_for_status()
    except HTTPError as exception:
        error = "Error in transferring ownership - " + derive_http_error_message(exception)
    except ConnectionError as exception:
        error = "Error - could not transfer ownership due to a connection error."
        debug = "ConnectionError: " + str(exception)
    except RequestException as exception:
        error = "Error - could not transfer ownership due to an unknown error."
        debug = "RequestException: " + str(exception)
    else:
        success = "Ownership transferred successfully."
    finally:
        print_messages(request, error=error, debug=debug, success=success)

    return redirect("dashboard")