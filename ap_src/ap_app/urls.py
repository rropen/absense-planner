from django.urls import path
from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog
from . import views

js_info_dict = {
    'packages' : ('recurrence', ),
}

urlpatterns = [
    path("", views.index, name="index"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path("calendar/", views.all_calendar, name="all_Calendar"),
    path("calendar/<str:month>/<int:year>", views.all_calendar, name="all_calendar"),
    path("teams/", views.teams_dashboard, name="dashboard"),
    path("teams/create", views.create_team, name="create_team"),
    path("teams/invite/", views.view_invites, name="view_invites"),
    path("teams/invite/<int:team_id>/<int:user_id>/<str:role>", views.team_invite, name="team_invite"),
    path("teams/join", views.join_team, name="join_team"),
    path("teams/join/<int:id>/<str:role>", views.joining_team_process, name="join_team_2"),
    path("teams/join/apply/<int:id>/<str:response>", views.joining_team_request, name="joining_team_request"),
    path("teams/leave/<int:id>", views.leave_team, name="leave_team"),
    path("teams/settings/<int:id>", views.team_settings, name="team_settings"),
    path("teams/calendar/<int:id>", views.team_calendar, name="Calendar"),
    path("teams/calendar/<int:id>/<str:month>/<int:year>", views.team_calendar, name="calendar"),
    path("absence/add", views.add, name="add"),
    path("absence/add_recurring", views.add_recurring, name="add_recurring"),
    path("profile/", views.profile_page, name="profile"),
    path("details/", views.details_page, name="details"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("ap_accounts/delete_user", views.deleteuser, name="delete_user"),
    path("absence/delete/<int:absence_id>", views.absence_delete, name="Absence Delete"),
    path("absence/edit/<int:pk>", views.EditAbsence.as_view(), name="absence_edit"),
    path("profile/settings", views.profile_settings, name="profile settings"),
    path("profile/settings/add-user", views.add_user, name="add-user"),
    url(r'^jsil18n', JavaScriptCatalog.as_view(), js_info_dict)
    # path("absence/edit/<int:id>", views.absence_edit, name="Absence Edit")
]
