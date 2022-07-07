# Generated by Django 3.2.9 on 2022-07-07 10:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ap_app', '0008_absence_target_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='edit_whitelist',
            field=models.ManyToManyField(related_name='permissions', to=settings.AUTH_USER_MODEL),
        ),
    ]