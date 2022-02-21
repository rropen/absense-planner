from django.shortcuts import render


# Temp

details_info = [  # Sent over to html code
    [
        {"name": "Jai", "attendence": "absent"},
        {"name": "Mark", "attendence": "late"},
        {"name": "Trevor", "attendence": "here"},
    ]
]

calendar_info = []


profiles_info = []  # Not too sure how these details are going to be laid out


selected_date = "29/10/21"


def details_page(request):
    context = {
        "employee_dicts": details_info,
    }
    return render(request, "plannerapp/Details.html", context)


def calendar_page(request):
    context = {
        "dates": calendar_info
    }  # Needs to take the list which contains that dates information

    print("test")

    return render(request, "plannerapp/Calendar.html", context)


# Profile page

selected_name = "bob"
job_role = "Software Developer"  # Not sure if this is neccessary
project_id = "AB12341"
todays_attendance = False


def profile_page(request):
    selected_profile_context = {
        "name": selected_name,
        "job_role": job_role,
        "project_id": project_id,
        "attending": todays_attendance,
    }

    return render(request, "plannerapp/Profile.html", selected_profile_context)


from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import names, login, sign_up


def index(response):
    return render(response, "plannerapp/index.html")


def add(response):
    return render(response, "plannerapp/add_absence.html")


def login_page(response):
    form = login()
    return render(response, "plannerapp/login.html", {"form": form})


def sign_up_page(response):
    form = sign_up()
    return render(response, "plannerapp/sign_up.html", {"form": form})


def calendar(response):
    return render(response, "plannerapp/Calendar.html")


def nameForm(request):
    form = names(request.POST or None)
    if form.is_valid():
        form.save()

    context = {"form": form}

    return render(request, "plannerapp/form.html", context)
