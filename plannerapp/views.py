from django.shortcuts import render, redirect
from .forms import login, sign_up
from .models import absence
from django.contrib.auth.models import User
import calendar, datetime


# Temp

details_info = [  # Sent over to html code
    [
        {"name": "Jai", "attendence": "absent"},
        {"name": "Mark", "attendence": "late"},
        {"name": "Trevor", "attendence": "here"},
    ]
]


profiles_info = []  # Not too sure how these details are going to be laid out


profiles_info = []  # Not too sure how these details are going to be laid out

selected_date = "29/10/21"

selected_name = "bob"
job_role = "Software Developer"  # Not sure if this is neccessary
project_id = "AB12341"
todays_attendance = False


def index(response):
    return render(response, "plannerapp/index.html")


def add(response):
    return render(response, "plannerapp/add_absence.html")


def nameForm(request):
    form = names(request.POST or None)
    if form.is_valid():
        form.save()

    context = {"form": form}

    return render(request, "plannerapp/form.html", context)


def details_page(request):
    context = {
        "employee_dicts": details_info,
    }
    return render(request, "plannerapp/Details.html", context)


def calendar_page(request):

    current_date = datetime.datetime.now()
    YEAR = current_date.year
    MONTH = current_date.month
    current_month = calendar.monthrange(YEAR, MONTH)[1]
    month_name = current_date.strftime("%b")

    users = User.objects.all()
    absence_content = []
    total_absence_dates = {}

    for user in users:
        # all the absences for the user
        absence_info = absence.objects.filter(User_ID=user)
        # if they have any absences
        print("-------------------------------------------------------------------")

        if absence_info:
            # set for all the absences of a user
            absence_dates = {1, 2, 3}
            absence_dates.clear()
            # mapping the absence content to keys in dictionary
            for x in range(len(absence_info)):

                request_date = absence_info[x].request_date

                absence_id = absence_info[x].ID

                absence_date = absence_info[x].absence_date
                # adding dates to set
                absence_dates.add(absence_date.day)

                request_accepted = absence_info[x].request_accepted

                reason = absence_info[x].reason

                absence_content.append(
                    {
                        "name": user,
                        "ID": absence_id,
                        "absence_date": absence_date,
                        "request_date": request_date,
                        "request_accepted": request_accepted,
                        "reason": reason,
                    }
                )
            # for each user it maps the set of dates to a dictionary key labelled as the users name
            total_absence_dates[user] = absence_dates
    user_range = range(len(users))
    context = {
        "current_month": month_name,
        "day_range": range(1, current_month + 1),
        "absences": absence_content,
        "absence_dates": total_absence_dates,
        "users": list(users),
        "user_range": user_range,
    }
    print(list(users))

    return render(request, "plannerapp/Calendar.html", context)


# Profile page
def profile_page(request):
    selected_profile_context = {
        "name": selected_name,
        "job_role": job_role,
        "project_id": project_id,
        "attending": todays_attendance,
    }

    return render(request, "plannerapp/Profile.html", selected_profile_context)


def login_page(response):
    form = login()
    return render(response, "plannerapp/login.html", {"form": form})


def sign_up_page(response):
    form = sign_up()
    return render(response, "plannerapp/sign_up.html", {"form": form})
