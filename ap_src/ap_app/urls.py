from django.urls import path

from .views import calendarview, views, absences, teams

from django.conf.urls import handler404, handler500
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from django.views.i18n import JavaScriptCatalog

js_info_dict = {
    'packages' : ('recurrence', ),
}

urlpatterns = [
    path("", views.index, name="index"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path("calendar/", views.main_calendar, name="all_Calendar"),
    path("calendar/<str:month>/<int:year>", views.main_calendar, name="all_calendar"),
    path("teams/", teams.teams_dashboard, name="dashboard"),
    path("teams/create", teams.create_team, name="create_team"),
    path("teams/join", teams.join_team, name="join_team"),
    path("teams/api-calendar/<int:id>", calendarview.api_team_calendar, name="api_team_calendar"),
    path("teams/api-calendar/<int:id>/<str:month>/<int:year>", calendarview.api_team_calendar, name="api_team_calendar"),
    path("teams/edit/<int:id>", teams.edit_team, name="edit_team"),
    path("absence/add", absences.manual_add, name="add"),
    path("absence/add_recurring", absences.add_recurring, name="add_recurring"),
    path("profile/", absences.profile_page, name="profile"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("ap_accounts/delete_user", views.deleteuser, name="delete_user"),
    path("absence/delete/<int:absence_id>/<int:user_id>/", absences.absence_delete, name="absence_delete"),
    path("absence/delete/<int:absence_id>/<int:user_id>/<int:team_id>/", absences.absence_delete, name="absence_delete"),
    path("absence_recurring/delete/<int:absence_id>/<int:user_id>/", absences.absence_recurring_delete, name="recurring_absence_delete"),
    path("absence_recurring/delete/<int:absence_id>/<int:user_id>/<int:team_id>/", absences.absence_recurring_delete, name="recurring_absence_delete"),
    path("absence/edit/<int:pk>", absences.EditAbsence.as_view(), name="absence_edit"),
    path("absence/edit_recurring/<int:pk>", absences.edit_recurring_absences, name="recurring_absence_edit"),
    path("absence/click_add", views.click_add, name="absence_click_add"),
    path("absence/click_remove", views.click_remove, name="absence_click_remove"),
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
    path("403", views.Custom403View, name="403"),
    path("404", views.Custom404View, name="404"),
    path("500", views.Custom500View, name="500"),
    path("400", views.Custom400View, name="400"),

    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}) #This lets Django find the CSS files when debug is set to false

] 

handler404 = 'ap_app.utils.errors.handler404'
handler500 = 'ap_app.utils.errors.handler500'
handler400 = 'ap_app.utils.errors.handler400'
handler503 = 'ap_app.utils.errors.handler503'
