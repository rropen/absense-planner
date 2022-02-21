from django.db import models


class employees(models.Model):
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)

    def __str__(self):
        return self.firstName


class absences(models.Model):
    absenceID = models.AutoField(primary_key=True)
    date = models.CharField(max_length=200)
    
    def __str__(self):
        return self.date
