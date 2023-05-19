from django.conf import \
    settings  # This will import the settings file that django uses.


def production(request): # Function that will return the PRODUCTION_UI value.
    return {'PRODUCTION_UI': settings.PRODUCTION_UI}
    