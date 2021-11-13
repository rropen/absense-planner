from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_page, name="login"),
    path("sign_up/", views.sign_up_page, name="login"),
    path("calendar/", views.calendar, name="calendar"),
    path("add_absence/", views.add, name="add"),
    path("form/", views.nameForm, name="nameform"),
    path("profile/", views.profile_page, name="profile"),
    path("details", views.details_page, name="details"),

]
