# Generated by Django 4.2.6 on 2023-10-31 11:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ap_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="external_teams",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="absence",
            name="Target_User_ID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="target_user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="absence",
            name="User_ID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
