import calendar
from datetime import datetime, timedelta
from logging import exception
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import login, sign_up, DeleteUserForm, AbsenceForm
from .models import Absence
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

def calendar_page(request, day:int=None, month:int=None, year:int=None) -> render:
    """returns calander web page with a context full of random junk"""
    # get the current date if no date has been passed
    if None in (day, month, year):
        date = datetime.now()
        year = date.year
        month = date.month
        day = date.day
    _, days_in_month = calendar.monthrange(year, month)
    users = User.objects.all()
    absences = []
    total_absence_dates = {}
    all_absences = {}
    for user in users:
        db_absences = Absence.objects.filter(User_ID=user)
        if not db_absences:
            continue
        # translating absence object to dictionary
        for absence in db_absences:
            start_date = absence.absence_date_start
            end_date = absence.absence_date_end
            # create list of dates that will be absent
            dates = [
                start_date + timedelta(days=n) for n in range(
                    start_date, end_date
                )
            ]
            absence_dict = {
                'id': absence.id,
                'start_date': start_date,
                'end_date': end_date,
                'included_dates': dates,
                'request_date': absence.request.date,
                'request_accepted': absence.request_accepted,
            }
            absences.append(absence_dict)

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            total_absence_dates[user] = dates
            all_absences[user] = absences
    
    next_month = month + 1 if month < 12 else 1
    last_month = month - 1 if month > 1 else 12
    context = {
        "current_date": date,
        "day_range": range(1, days_in_month + 1),
        "absences": all_absences,
        "absence_dates": total_absence_dates,
        "users": list(users),
        "current_day": day,  # redundant because we have "current_date"
        "current_month": month, # redundant
        "current_year": year, # redundant
        "month_num": datetime.strptime(month, "%B").month,
        "month": month,
        "year": year,
        "previous_year": year - 1,
        "next_year": year + 1,
        "previous_month": last_month,
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

