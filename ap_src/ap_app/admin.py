from django.contrib import admin

from .models import Absence, Role, UserProfile, RecurringAbsences

admin.site.register(Absence)
admin.site.register(Role)
admin.site.register(UserProfile)
admin.site.register(RecurringAbsences)
