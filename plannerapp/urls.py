from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("calendar/", views.all_calendar, name="all_Calendar"),
    path("calendar/<str:month>/<int:year>", views.all_calendar, name="all_calendar"),
    path("teams/", views.teams_dashboard, name="dashboard"),
    path("teams/create", views.create_team, name="create_team"),
    path("teams/join", views.join_team, name="join_team"),
    path("teams/join/<int:id>/<str:role>", views.joining_team_process, name="join_team_2"),
    path("teams/leave/<int:id>", views.leave_team, name="leave_team"),
    path("teams/calendar/<int:id>", views.team_calendar, name="Calendar"),
    path("teams/calendar/<int:id>/<str:month>/<int:year>", views.team_calendar, name="calendar"),
    path("absence/add", views.add, name="add"),
    path("profile/", views.profile_page, name="profile"),
    path("details/", views.details_page, name="details"),
    path("privacy/", views.privacy_page, name="privacy"),
    path("accounts/delete_user", views.deleteuser, name="delete_user"),
    path("absence/delete/<int:absence_id>", views.absence_delete, name="Absence Delete"),
    path("absence/edit/<int:pk>", views.EditAbsence.as_view(), name="absence_edit"),
    path("profile/settings", views.profile_settings, name="profile settings"),
    path("profile/settings/add-user", views.add_user, name="add-user")

    # path("absence/edit/<int:id>", views.absence_edit, name="Absence Edit")
]
