from django.contrib import admin

from .models import Absence, Relationship, Role, Team, UserProfile

admin.site.register(Absence)
admin.site.register(Team)
admin.site.register(Relationship)
admin.site.register(Role)
admin.site.register(UserProfile)