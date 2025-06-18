from django.urls import include, path

from .views import calendarview, views, absences, teams

from django.conf.urls import handler404, handler500
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from django.views.i18n import JavaScriptCatalog

from os import getenv

PROFILING_ENV = getenv("PROFILING")
PROFILING = PROFILING_ENV is not None and PROFILING_ENV.lower() == "true"

js_info_dict = {
    'packages' : ('recurrence', ),
}

urlpatterns = [
    path("", views.index, name="index"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path("calendar/", views.main_calendar, name="all_Calendar"),
    path("calendar/<str:month>/<int:year>", views.main_calendar, name="all_calendar"),
    path("teams/", teams.teams_dashboard, name="dashboard"),
    path("teams/leave", teams.leave_team, name="leave_team"),
    path("teams/create", teams.create_team, name="create_team"),
    path("teams/join", teams.join_team, name="join_team"),
    path("teams/api-calendar/<int:id>", calendarview.api_team_calendar, name="api_team_calendar"),
    path("teams/api-calendar/<int:id>/<str:month>/<int:year>", calendarview.api_team_calendar, name="api_team_calendar"),
    path("teams/edit/<int:id>", teams.edit_team, name="edit_team"),
    path("teams/delete", teams.delete_team, name="delete_team"),
    path("absence/add", absences.manual_add, name="add"),
    path("absence/add_recurring", absences.add_recurring, name="add_recurring"),
    path("absences/my_absences", absences.profile_page, name="my_absences"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("ap_accounts/delete_user", views.deleteuser, name="delete_user"),
    path("absence/delete/<int:absence_id>/<int:user_id>/", absences.absence_delete, name="absence_delete"),
    path("absence/delete/<int:absence_id>/<int:user_id>/<int:team_id>/", absences.absence_delete, name="absence_delete"),
    path("absence_recurring/delete/<int:absence_id>/<int:user_id>/", absences.absence_recurring_delete, name="recurring_absence_delete"),
    path("absence_recurring/delete/<int:absence_id>/<int:user_id>/<int:team_id>/", absences.absence_recurring_delete, name="recurring_absence_delete"),
    path("absence/edit/<int:pk>", absences.EditAbsence.as_view(), name="absence_edit"),
    path("absence/edit_recurring/<int:pk>", absences.edit_recurring_absences, name="recurring_absence_edit"),
    path("absence/click_add", absences.click_add, name="absence_click_add"),
    path("absence/click_remove", absences.click_remove, name="absence_click_remove"),
    path("profile/settings", views.profile_settings, name="profile_settings"),
    path("profile/settings/add-user", views.add_user, name="add-user"),
    path("profile/settings/set-region", views.set_region, name="set-region"),
    path("profile/settings/update-colour", views.update_colour, name="update-colour"),
    path("calendar/set_month",calendarview.set_calendar_month, name="set_month"),
    path("main_calendar", views.main_calendar, name="main_calendar"),
    path("main_calendar/<str:month>/<int:year>", views.main_calendar, name="main_calendar"),
    path("remove_lingering_perms", views.remove_lingering_perms, name="remove_lingering_perms"),
    path("jsi18n", JavaScriptCatalog.as_view(packages=['recurrence']), name="javascript-catalog"),
    #Errors
    path("404", views.Custom404View, name="404"),
    path("500", views.Custom500View, name="500"),
    path("400", views.Custom400View, name="400"),

    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), #This lets Django find the CSS files when debug is set to false

]

# This allows the django-debug-toolbar to be used to analyse performance of the web server
# The 4.2.0 version has to be used as it is the latest one compatible with Django version 4.2.6
# This is not the same method of importing the URLs as in the documentation because the helper function, debug_toolbar_urls, is only available
# since version 4.4.3
if PROFILING:
    urlpatterns += path("__debug__/", include("debug_toolbar.urls")),

handler404 = 'ap_app.utils.errors.handler404'
handler500 = 'ap_app.utils.errors.handler500'
handler400 = 'ap_app.utils.errors.handler400'
handler503 = 'ap_app.utils.errors.handler503'
handler403 = 'ap_app.utils.errors.handler403'
