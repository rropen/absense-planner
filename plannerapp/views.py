from django.shortcuts import render, redirect
from .forms import *
from .models import *
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
    form = CreateAbsence()
    if response.method == "POST":
        print(response.POST)
        form = CreateAbsence(response.POST)
        
        
        if form.is_valid():
            print("-=-==-=\n\nForm Acceptable\n\n-=-=-=")
            obj = absence()
            
            obj.absence_date_start = form.cleaned_data["start_date"]
            obj.absence_date_end = form.cleaned_data["end_date"]
            obj.reason = form.cleaned_data["reason"]

            obj.request_accepted = False
            

            # Temporarily getting first user - (while there is no login & signup for basic users)
            obj.User_ID = User.objects.all()[0]

            obj.save()

        

    content = {
        "form": form
    }

    return render(response, "plannerapp/add_absence.html", content)



def details_page(request):
    context = {
        "employee_dicts": details_info,
    }
    return render(request, "plannerapp/Details.html", context)


def calendar_page(request):

    current_date = datetime.datetime.now()
    YEAR = current_date.year
    MONTH = current_date.month
    DAY = current_date.day
    current_month = calendar.monthrange(YEAR, MONTH)[1]
    month_name = current_date.strftime("%F")
    users = User.objects.all()
    absence_content = []
    total_absence_dates = {}

    for user in users:
        # all the absences for the user
        absence_info = absence.objects.filter(User_ID=user)
        # if they have any absences
        print("-------------------------------------------------------------------")
        print(absence_info)
        if absence_info:
            # set for all the absences of a user
            absence_dates = {1, 2, 3}
            absence_dates.clear()
            # mapping the absence content to keys in dictionary
            for x in range(len(absence_info)):

                request_date = absence_info[x].request_date

                absence_id = absence_info[x].ID

                absence_date_start = absence_info[x].absence_date_start
                absence_date_end = absence_info[x].absence_date_end

                # code to start doing more than one month

                if absence_date_start.year == absence_date_end.year:
                    if absence_date_start.month == absence_date_end.month:
                        for y in range(
                            absence_date_start.day, absence_date_end.day + 1
                        ):
                            absence_dates.add(y)
                """    
                    else:
                        for y in range(absence_date_start.day, ):
                                                        days_left_current_month = (
                        calendar.monthrange(
                            absence_date_start.year, absence_date_start.month
                        )[1]
                        - absence_date_start.day
                    )
                    days_left_next_month = absence_date_end.day
                """
                request_accepted = absence_info[x].request_accepted

                reason = absence_info[x].reason

                absence_content.append(
                    {
                        "name": user,
                        "ID": absence_id,
                        "absence_date_start": absence_date_start,
                        "absence_date_end": absence_date_end,
                        "request_date": request_date,
                        "request_accepted": request_accepted,
                        "reason": reason,
                    }
                )

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            total_absence_dates[user] = absence_dates

    context = {
        "current_month": current_date,
        "day_range": range(1, current_month + 1),
        "absences": absence_content,
        "absence_dates": total_absence_dates,
        "users": list(users),
        "current_day": DAY,
    }

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
