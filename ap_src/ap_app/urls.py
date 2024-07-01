from django.urls import path
from . import views, teams

from django.conf.urls import handler404, handler500
from django.urls import re_path
from django.views.static import serve
from django.conf import settings

js_info_dict = {
    'packages' : ('recurrence', ),
}

urlpatterns = [
    path("", views.index, name="index"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path("calendar/", views.main_calendar, name="all_Calendar"),
    path("calendar/<str:month>/<int:year>", views.main_calendar, name="all_calendar"),
    path("teams/", views.teams_dashboard, name="dashboard"),
    path("teams/create", views.create_team, name="create_team"),
    #path("teams/invite/", views.view_invites, name="view_invites"),
    #path("teams/invite/<int:team_id>/<int:user_id>/<str:role>", views.team_invite, name="team_invite"),
    path("teams/join", views.join_team, name="join_team"),
    #path("teams/join/apply/<int:id>/<str:response>", views.joining_team_request, name="joining_team_request"),
    path("teams/api-calendar/<int:id>", views.api_team_calendar, name="api_team_calendar"),
    path("teams/api-calendar/<int:id>/<str:month>/<int:year>", views.api_team_calendar, name="api_team_calendar"),
    #path("teams/settings/promote/<int:id>/<int:user_id>", views.promote_team_member, name="promote_team_member"),
    #path("teams/settings/demote/<int:id>/<int:user_id>", views.demote_team_member, name="demote_team_member"),
    #path("teams/settings/remove/<int:id>/<int:user_id>", views.remove_team_member, name="remove_team_member"),
    #path("teams/misc/<int:id>", views.team_misc, name="misc"),
    path("teams/edit/<int:id>", views.edit_team, name="edit_team"),
    path("absence/add", teams.manual_add, name="add"),
    path("absence/add_recurring", views.add_recurring, name="add_recurring"),
    path("profile/", views.profile_page, name="profile"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("ap_accounts/delete_user", views.deleteuser, name="delete_user"),
    path("absence/delete/<int:absence_id>/<int:user_id>/", views.absence_delete, name="Absence Delete"),
    path("absence/delete/<int:absence_id>/<int:user_id>/<int:team_id>/", views.absence_delete, name="Absence Delete"),
    path("absence_recurring/delete/<int:absence_id>/<int:user_id>/", views.absence_recurring_delete, name="Recurring Absence Delete"),
    path("absence_recurring/delete/<int:absence_id>/<int:user_id>/<int:team_id>/", views.absence_recurring_delete, name="Recurring Absence Delete"),
    path("absence/edit/<int:pk>", views.EditAbsence.as_view(), name="absence_edit"),
    path("absence/edit_recurring/<int:pk>", views.edit_recurring_absences, name="recurring_absence_edit"),
    path("absence/click_add", views.click_add, name="absence_click_add"),
    path("absence/click_remove", views.click_remove, name="absence_click_remove"),
    path("profile/settings", views.profile_settings, name="profile_settings"),
    path("profile/settings/add-user", views.add_user, name="add-user"),
    path("profile/settings/set-region", views.set_region, name="set-region"),
    path("profile/settings/update-colour", views.update_colour, name="update-colour"),
    path("calendar/set_month",views.set_calendar_month, name="set_month"),
    path("main_calendar", views.main_calendar, name="main_calendar"),
    path("main_calendar/<str:month>/<int:year>", views.main_calendar, name="main_calendar"),
    path("remove_lingering_perms", views.remove_lingering_perms, name="remove_lingering_perms"),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}) #This lets Django find the CSS files when debug is set to false

] 

handler404 = 'ap_app.errors.handler404'
handler500 = 'ap_app.errors.handler500'
handler400 = 'ap_app.errors.handler400'
