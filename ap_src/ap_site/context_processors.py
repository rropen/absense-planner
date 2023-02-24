from django.conf import settings # import the settings file

def production(request):
    return {'PRODUCTION_UI': settings.PRODUCTION_UI}
    