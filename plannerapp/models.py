from urllib import request
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Absence(models.Model):
    ID = models.AutoField(primary_key=True)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="absences")
    absence_date_start = models.DateField(max_length=200)
    absence_date_end = models.DateField(max_length=200)
    request_date = models.DateField(default=timezone.now)
    manager_ID = models.CharField(max_length=200)
    request_accepted = models.BooleanField()
    reason = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.User_ID}, {self.absence_date_start}, {self.reason}"
