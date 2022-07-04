from django.db import models
from django.contrib.auth import get_user_model
from river.models.fields.state import StateField, State
from river.models import TransitionApproval
from django.utils.timezone import now
from django.utils.translation import gettext_lazy

User = get_user_model()

# TODO: is the ID, id field needed. Django has this built in as part of the Model class


class Absence(models.Model):
    ID = models.AutoField(primary_key=True)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="absences")
    absence_date_start = models.DateField(gettext_lazy("Date"), max_length=200, default=now)
    absence_date_end = models.DateField(max_length=200)
    # #issue #11
    edit_whitelist = models.ManyToManyField(to=User)

    def __str__(self):
        return f"{self.User_ID}, {self.absence_date_start} - {self.absence_date_end}"


class Team(models.Model):
    """This includes all the attributes of a Team"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True, null=False)
    description = models.CharField(max_length=512)
    private = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    @property
    def count(self):
        return Relationship.objects.filter(
            team=self, status=State.objects.get(slug="active")
        ).count()


class Role(models.Model):
    """This includes all the attributes of a Role"""

    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=64, null=False, unique=True)

    def __str__(self):
        return f"{self.role}"


class Relationship(models.Model):
    """This includes all the attributes of a Relationship"""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    status = StateField(on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "user",
            "team",
        )

    def __str__(self):
        return f"User: {self.user.username} --> {self.team.name} as {self.role} ({self.status})"

    def custom_delete(self):
        to_delete = TransitionApproval.objects.filter(object_id=self.pk)
        for obj in to_delete:
            obj.delete()
        self.delete()


class UserProfile(models.Model):
    """ Extension of fields for User class """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Extra Fields
    accepted_policy = models.BooleanField()

    def __str__(self):
        return f"{self.user.username}"
    

    def find_user_obj(user_to_find):
        """ Finds & Returns object of 'UserProfile' for a user 
        \n-param (type)User user_to_find 
        """    
        users = UserProfile.objects.filter(user=user_to_find)    
        # If cannot find object for a user, than creates on
        if users.count() <= 0:
            UserProfile.objects.create(
            user = user_to_find,
            accepted_policy = False
            )

        # Users object
        user_found = UserProfile.objects.filter(user=user_to_find)[0]
   
        return user_found


    def obj_exists(user):
        """ Determines if a user has a 'UserProfile' Object"""
        objs = UserProfile.objects.filter(user=user)
        if objs.count() == 0:
            return False

        return True