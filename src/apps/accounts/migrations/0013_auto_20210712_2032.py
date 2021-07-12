# Generated by Django 3.1.7 on 2021-07-12 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scenario', '0011_auto_20210712_2031'),
        ('accounts', '0012_auto_20210712_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='scenarios',
            field=models.ManyToManyField(blank=True, help_text="Scenarios added to the folder, could be anyone's as long as they are public or made by the folder owner.", related_name='added_to', to='scenario.Scenario'),
        ),
    ]