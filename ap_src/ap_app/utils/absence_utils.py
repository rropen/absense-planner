import datetime
from datetime import timedelta
from ..models import RecurringException, Absence, RecurringAbsences


def get_absence_data(users, user_type):
    data = {}
    absence_content = []
    total_absence_dates = {}
    total_half_dates = {}
    total_recurring_dates = {}
    all_absences = {}
    delta = datetime.timedelta(days=1)

    for user in users:
        # all the absences for the user
        if user_type == 1:
            user_username = user.user.username
        else:
            user_username = user.username

        absence_info = Absence.objects.filter(Target_User_ID__username=user_username)
        total_absence_dates[user_username] = []
        total_recurring_dates[user_username] = []
        total_half_dates[user_username] = []
        all_absences[user_username] = []

        # if they have any absences
        if absence_info:
            # mapping the absence content to keys in dictionary
            for x in absence_info:
                absence_id = x.ID
                absence_date_start = x.absence_date_start
                absence_date_end = x.absence_date_end
                dates = absence_date_start
                if x.half_day == "NORMAL":
                    while dates <= absence_date_end:
                        total_absence_dates[user_username].append(dates)
                        dates += delta
                else:
                    total_half_dates[user_username].append(
                        {"date": absence_date_start, "type": x.half_day}
                    )

                absence_content.append(
                    {
                        "ID": absence_id,
                        "absence_date_start": absence_date_start,
                        "absence_date_end": absence_date_end,
                        "dates": total_absence_dates[user_username],
                    }
                )

            # for each user it maps the set of dates to a dictionary key labelled as the users name
            all_absences[user_username] = absence_content

        recurring = RecurringAbsences.objects.filter(
            Target_User_ID__username=user_username
        )

        if recurring:
            for recurrence_ in recurring:
                dates = recurrence_.Recurrences.occurrences(
                    dtend=datetime.datetime.strptime(
                        str(datetime.datetime.now().year + 2), "%Y"
                    )
                )

                for x in list(dates)[:-1]:
                    time_const = "23:00:00"
                    time_var = datetime.datetime.strftime(x, "%H:%M:%S")
                    if time_const == time_var:
                        x += timedelta(days=1)

                    # print(RecurringException.objects.filter(Target_User_ID__username=user_username, Exception_Start=x).count())
                    if (
                        RecurringException.objects.filter(
                            Target_User_ID__username=user_username, Exception_Start=x
                        ).count()
                        == 0
                    ):
                        total_recurring_dates[user_username].append(x)
                # TODO: add auto deleting for recurring absences once last date of absences in before now
                # if x < datetime.datetime.now():
                #    pass

    data["recurring_absence_dates"] = total_recurring_dates
    data["all_absences"] = all_absences
    data["absence_dates"] = total_absence_dates
    data["half_days_data"] = total_half_dates
    data["users"] = users
    return data


def text_rules(user):
    recurring_absences = RecurringAbsences.objects.filter(Target_User_ID=user).values(
        "Recurrences", "ID"
    )
    rec_absences = {}

    for x in recurring_absences:
        absence_ = x["Recurrences"]
        if absence_:
            rec_absences[x["ID"]] = []
        if absence_.exdates:
            for y in absence_.exdates:
                rec_absences[x["ID"]].append(
                    "Excluding Date: " + (y + timedelta(days=1)).strftime("%A,%d %B,%Y")
                )
        if absence_.rdates:
            for y in absence_.rdates:
                rec_absences[x["ID"]].append(
                    "Date: " + (y + timedelta(days=1)).strftime("%A,%d %B,%Y")
                )
        if absence_.rrules:
            for y in absence_.rrules:
                rec_absences[x["ID"]].append("Rule: " + str(y.to_text()))

        if absence_.exrules:
            for y in absence_.exrules:
                rec_absences[x["ID"]].append("Excluding Rule: " + str(y.to_text()))

    return rec_absences
