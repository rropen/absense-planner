from django import template

register = template.Library()

@register.simple_tag
def get_user_id(all_absences, user, current_user, year, month_num, day):
    # for absence in all_absences:
    #     print(absence)
    # return None
    for absence in all_absences:
        #print(absence)
        dates = absence["dates"]
        print(absence["dates"])
        for the_date in absence["dates"]:
            print(the_date)
            print("")
            if the_date.year == year and the_date.month == month_num and the_date.day == day:
                
                # print(f"absence {date.year}/{date.month}/{date.day} - target: {absence["target_user_id"]} // user: {absence["User_ID"]}")
                # print(absence)
                if absence["target_user_id"] != absence["User_ID"]:
                    return absence["User_ID"]
                    # print(absence["target_user_id"])
                    # return absence["User_ID"]
                else:
                    return None

            return None
        
            


