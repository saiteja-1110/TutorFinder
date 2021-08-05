# Generated by Django 3.2 on 2021-06-15 06:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_tutor_slots'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutor',
            name='favourite',
            field=models.ManyToManyField(blank=True, related_name='favourite', to=settings.AUTH_USER_MODEL),
        ),
    ]
