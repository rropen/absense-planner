from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from recurrence.fields import RecurrenceField

User = get_user_model()

# TODO: is the ID, id field needed. Django has this built in as part of the Model class


class Status(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=65, null=False, unique=True)

    def __str__(self):
        return f"{self.status}"


class Absence(models.Model):
    ID = models.AutoField(primary_key=True)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    Target_User_ID = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="target_user",
    )
    absence_date_start = models.DateField(_("Date"), max_length=200, default=now)
    absence_date_end = models.DateField(_("Date"), max_length=200, default=now)

    DAYS_CHOICES = (
        ("NORMAL", "Normal"),
        ("AFTERNOON", "Afternoon"),
        ("MORNING", "Morning"),
    )

    half_day = models.CharField(max_length=200, choices=DAYS_CHOICES, default="NORMAL")

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


class Role(models.Model):
    """This includes all the attributes of a Role"""

    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=64, null=False, unique=True)

    def __str__(self):
        return f"{self.role}"


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

    region = models.CharField(max_length=200, default="GB")

    def __str__(self):
        return f"{self.user.username}"


class RecurringException(models.Model):
    ID = models.AutoField(primary_key=True)
    Target_User_ID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    User_ID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recurringexception"
    )
    Exception_Start = models.DateField(_("Date"), max_length=200, default=now)
    Exception_End = models.DateField(_("Date"), max_length=200, default=now)


class ColourScheme(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    default = models.CharField(max_length=100)


class ColorData(models.Model):
    id = models.AutoField(primary_key=True)
    scheme = models.ForeignKey(
        ColourScheme, on_delete=models.CASCADE, related_name="colorscheme"
    )
    color = models.CharField(max_length=20)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            "user",
            "scheme",
        )
