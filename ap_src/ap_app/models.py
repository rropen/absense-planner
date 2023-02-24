from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model
from river.models.fields.state import StateField, State
from river.models import TransitionApproval
from django.utils.timezone import now
from django.utils.translation import gettext_lazy

from recurrence.fields import RecurrenceField
from ckeditor.fields import RichTextField

User = get_user_model()

# TODO: is the ID, id field needed. Django has this built in as part of the Model class


class Absence(models.Model):
    ID = models.AutoField(primary_key=True)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="absences")
    Target_User_ID = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="+",
    )
    absence_date_start = models.DateField(
        gettext_lazy("Date"), max_length=200, default=now
    )
    absence_date_end = models.DateField(
        gettext_lazy("Date"), max_length=200, default=now
    )

    _equivalent_if_fields_equal = (
        "Target_User_ID",
        "absence_date_start",
        "absence_date_end",
    )

    def is_equivalent(self, other: "Absence") -> bool:
        """Returns True if the provided `other` instance of Absence
        is effectively equivalent to self.

        Keyword Arguments:
        -- other: The other MyModel to compare this self to
        """
        for field in self._equivalent_if_fields_equal:
            try:
                if getattr(self, field) != getattr(other, field):
                    return False
            except AttributeError:
                raise AttributeError(
                    f"All fields should be present on both instances. `{field}` is missing."
                )
        return True

    def save(self, *args, **kwargs):
        if not self.Target_User_ID:
            self.Target_User_ID = self.User_ID()
        super(Absence, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.Target_User_ID}, {self.absence_date_start} - {self.absence_date_end}, made by {self.User_ID}"


class RecurringAbsences(models.Model):
    ID = models.AutoField(primary_key=True)
    Target_User_ID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    Recurrences = RecurrenceField()
    User_ID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recurring_absences"
    )

    def __str__(self):
        return f"Recurring Absence No.{self.ID} for {self.Target_User_ID} by {self.User_ID}"


class Team(models.Model):
    """This includes all the attributes of a Team"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True, null=False)
    description = models.CharField(max_length=512)
    notes = RichTextField()  # models.CharField(max_length=512, null=False, default="")

    private = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    @property
    def count(self):
        return Relationship.objects.filter(
            team=self, status=State.objects.get(slug="active")
        ).count()

    @property
    def users(self):
        return Relationship.objects.filter(
            team=self, status=State.objects.get(slug="active")
        )


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
        return f"User: {self.user.username}({self.user.id}) --> {self.team.name}({self.team.id}) as {self.role} ({self.status})"

    def custom_delete(self):
        to_delete = TransitionApproval.objects.filter(object_id=self.pk)
        for obj in to_delete:
            obj.delete()
        self.delete()


class UserProfile(models.Model):
    """Extension of fields for User class"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    edit_whitelist = models.ManyToManyField(
        User,
        related_name="permissions",
    )
    # Extra Fields
    accepted_policy = models.BooleanField()

    privacy = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}"
