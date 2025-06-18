from django import template

register = template.Library()

@register.simple_tag
def get_user_id(all_absences, user, current_user, year, month_num, day):

    for absence in all_absences:

        print("l12", absence["dates"][1])
        print("l13", type(absence["dates"]))
        print("l14", len(absence["dates"]))

        for x in range(len(absence["dates"])):

            print("l18", x)

            print("l20", absence["dates"][x])

            if absence["dates"][x].year == year and absence["dates"][x].month == month_num and absence["dates"][x].day == day:
                
                # print(f"absence {the_date.year}/{the_date.month}/{the_date.day} - for user: {absence["target_user_id"]} // by user: {absence["User_ID"]}")

                return absence["User_ID"]

            else: 
                return None

            
        
            


