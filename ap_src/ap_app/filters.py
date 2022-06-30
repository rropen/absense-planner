from django.contrib.auth import get_user_model
import django_filters.filterset


User = get_user_model()

class CalendarFilter(django_filters.filterset.FilterSet):
    """ Calendar Filter \nUsed in calendar-page to filter users by 'username' input"""

    # icontains: Allows for a more intuitive search as searches users with similar chars in their username
    username = django_filters.filterset.CharFilter(lookup_expr="icontains")
    class Meta:
        model = User
        fields = ["username"]



