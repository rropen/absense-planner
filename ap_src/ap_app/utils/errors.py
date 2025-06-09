"""
A collection of utility functions that handle errors.
"""

from django.shortcuts import render
from django.contrib import messages

import environ

env = environ.Env()
environ.Env.read_env()

DEBUG = (env("DEBUG").lower() != "false") and (env("DEBUG").lower() == "true")

def handler404(request, exception):
    context = {}
    response = render(request, "404.html", context=context)
    response.status_code = 404
    return response

def handler500(request):
    context = {}
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response

def handler503(request):
    context = {}
    response = render(request, "503.html", context=context)
    response.status_code = 503
    return response

def handler400(request, exception):
    context = {}
    response = render(request, "400.html", context=context)
    response.status_code = 400
    return response

def handler403(request, exception):
    context = {}
    response = render(request, "403.html", context=context)
    response.status_code = 403
    return response

def my_view(request):
    return render(request, "base.html")

def print_debug(request, message):
    """
    Prints the message as a debug message if `DEBUG` is set to "True".
    Otherwise, do nothing.
    """

    if DEBUG:
        messages.set_level(request, messages.DEBUG)

        print(message)
        messages.debug(
            request,
            message
        )

def print_messages(request, success=None, error=None, debug=None):
    """
    Utility function that has two modes:
        - `success` message - this will only print out a success message
        when an action is completed successfully.
        - `error` message and `debug` message - this will print out a
        user-friendly error message, and if the `DEBUG` environment variable
        is enabled, a debug message for developers too
    """

    if (success):
        messages.success(request, success)
    elif (error and debug):
        messages.error(request, error)
        print_debug(request, debug)