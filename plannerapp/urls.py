from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("teams/", views.teams_dashboard, name="dashboard"),
    path("teams/join", views.join_team, name="join_team"),
    path("teams/join/<int:id>/<str:role>", views.joining_team_process, name="join_team_2"),
    path("teams/leave/<int:id>", views.leave_team, name="leave_team"),
    path("calendar/", views.calendar_page, name="Calendar"),
    path("calendar/<str:month>/<int:year>", views.calendar_page, name="calendar"),
    path("add_absence/", views.add, name="add"),
    path("profile/", views.profile_page, name="profile"),
    path("details/", views.details_page, name="details"),
    path("accounts/delete_user", views.deleteuser, name="delete_user"),
    path("absence/delete/<int:absence_id>", views.absence_delete, name="Absence Delete"),
    path("absence/edit/<int:pk>", views.EditAbsence.as_view(), name="absence_edit"),

    # path("absence/edit/<int:id>", views.absence_edit, name="Absence Edit")
]
