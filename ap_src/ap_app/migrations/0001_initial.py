# Generated by Django 4.2.6 on 2023-10-30 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import recurrence.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("role", models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Status",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("status", models.CharField(max_length=65, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=128, unique=True)),
                ("description", models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("accepted_policy", models.BooleanField()),
                ("privacy", models.BooleanField(default=False)),
                ("region", models.CharField(default="GB", max_length=200)),
                (
                    "edit_whitelist",
                    models.ManyToManyField(
                        related_name="permissions", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecurringAbsences",
            fields=[
                ("ID", models.AutoField(primary_key=True, serialize=False)),
                ("Recurrences", recurrence.fields.RecurrenceField()),
                (
                    "Target_User_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "User_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recurring_absences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Absence",
            fields=[
                ("ID", models.AutoField(primary_key=True, serialize=False)),
                (
                    "absence_date_start",
                    models.DateField(
                        default=django.utils.timezone.now,
                        max_length=200,
                        verbose_name="Date",
                    ),
                ),
                (
                    "absence_date_end",
                    models.DateField(
                        default=django.utils.timezone.now,
                        max_length=200,
                        verbose_name="Date",
                    ),
                ),
                (
                    "half_day",
                    models.CharField(
                        choices=[
                            ("NORMAL", "Normal"),
                            ("AFTERNOON", "Afternoon"),
                            ("MORNING", "Morning"),
                        ],
                        default="NORMAL",
                        max_length=200,
                    ),
                ),
                (
                    "Target_User_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "User_ID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="absences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Relationship",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ap_app.role"
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ap_app.status"
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="ap_app.team"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "team")},
            },
        ),
    ]
