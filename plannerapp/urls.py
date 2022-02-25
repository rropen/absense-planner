from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("calendar/", views.calendar_page, name="Calendar"),
    path("calendar/<str:month>/<int:year>", views.calendar_page, name="calendar"),
    path("add_absence/", views.add, name="add"),
    path("profile/", views.profile_page, name="profile"),
    path("details/", views.details_page, name="details"),
]
