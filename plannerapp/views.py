import calendar
import datetime 
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import login, sign_up, DeleteUserForm, AbsenceForm
from .models import Absence

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

current_date = datetime.datetime.now()
YEAR = current_date.year
MONTH = current_date.strftime("%B")
DAY = current_date.day
from django.views.generic import UpdateView

def index(request) -> render:
    """returns the home page"""
    return render(request, "plannerapp/index.html")

def add(request) -> render:
    """create new absence record"""
    if request.method == "POST":
        form = AbsenceForm(request.POST)
        if form.is_valid():
            obj = Absence()
            obj.absence_date_start = form.cleaned_data["start_date"]
            obj.absence_date_end = form.cleaned_data["end_date"]
            obj.request_accepted = False
            obj.User_ID = request.user
            obj.save()

            # redirect to success page
    else:
        form = AbsenceForm()
    content = {"form": form}
    return render(request, "plannerapp/add_absence.html", content)

def details_page(request) -> render:
    """returns details web page"""
    # TODO: get employee details and add them to context
    context = {"employee_dicts": ""}
    return render(request, "plannerapp/Details.html", context)

def calendar_page(request, month=MONTH, year=YEAR):

    month_days = calendar.monthrange(
        year, datetime.datetime.strptime(month, "%B").month
    )[1]
    users = User.objects.all()
    absence_content = []
    total_absence_dates = {}
    all_absences = {}
    delta = datetime.timedelta(days=1)

    for user in users:
        # all the absences for the user
        absence_info = Absence.objects.filter(User_ID=user)
        total_absence_dates[user] = []
        all_absences[user] = []

        # if they have any absences
        if absence_info:
            # mapping the absence content to keys in dictionary
            for x in range(len(absence_info)): # pylint: disable=consider-using-enumerate
                request_date = absence_info[x].request_date

                absence_id = absence_info[x].ID

                absence_date_start = absence_info[x].absence_date_start
                absence_date_end = absence_info[x].absence_date_end
                dates = absence_date_start
                while dates <= absence_date_end:
                    total_absence_dates[user].append(dates)
                    dates += delta

                request_accepted = absence_info[x].request_accepted


                absence_content.append(
                    {
                        "ID": absence_id,
                        "absence_date_start": absence_date_start,
                        "absence_date_end": absence_date_end,
                        "dates": total_absence_dates[user],
                        "request_date": request_date,
                        "request_accepted": request_accepted,
                    }
                )

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            total_absence_dates[user] = total_absence_dates[user]
            all_absences[user] = absence_content


    previous_month = 1
    next_month = 12
    try:

        next_month = datetime.datetime.strptime(
            str((datetime.datetime.strptime(month, "%B")).month + 1), "%m"
        ).strftime("%B")
    except:
        pass
    try:
        previous_month = datetime.datetime.strptime(
            str((datetime.datetime.strptime(month, "%B")).month - 1), "%m"
        ).strftime("%B")
    except:
        pass
    dates = "dates"
    context = {
        "current_date": current_date,
        "day_range": range(1, month_days + 1),
        "absences": all_absences,
        "absence_dates": total_absence_dates,
        "users": list(users),
        "current_day": DAY,
        "current_month": MONTH,
        "current_year": YEAR,
        "month_num": datetime.datetime.strptime(month, "%B").month,
        "month": month,
        "year": year,
        "previous_year": year - 1,
        "next_year": year + 1,
        "previous_month": previous_month,
        "next_month": next_month,
        "date": dates,
    }

    return render(request, "plannerapp/Calendar.html", context)


# Profile page
def profile_page(request):
    absences = Absence.objects.filter(User_ID = request.user.id)
    return render(request, "plannerapp/profile.html", {"absences":absences})


def login_page(request):
    form = login()
    return render(request, "plannerapp/login.html", {"form": form})


def sign_up_page(request):
    form = sign_up()
    return render(request, "plannerapp/sign_up.html", {"form": form})

@login_required
def deleteuser(request):
    """delete a user account"""
    if request.method == 'POST':
        delete_form = DeleteUserForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, "Your account has been deleted.")
        return redirect("index")
    else:
        delete_form = DeleteUserForm(instance=request.user)

    context = {
        'delete_form' : delete_form
    }
    
    return render(request, 'registration/delete_account.html', context)

def absence_delete(request, absence_id:int):
    absence = Absence.objects.get(pk=absence_id)
    user = request.user
    if user == absence.User_ID:
        absence.delete()
        return redirect("profile")
    else:
        raise Exception()

class EditAbsence(UpdateView):
    template_name = "plannerapp/edit_absence.html"
    model = Absence

    # specify the fields
    fields = ["absence_date_start", "absence_date_end"]

    def get_success_url(self) -> str:
        return reverse("profile")

