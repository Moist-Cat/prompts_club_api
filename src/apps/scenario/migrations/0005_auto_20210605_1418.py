# Generated by Django 3.1.7 on 2021-06-05 14:18

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scenario', '0004_auto_20210605_0006'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together={('scenario', 'user')},
        ),
    ]