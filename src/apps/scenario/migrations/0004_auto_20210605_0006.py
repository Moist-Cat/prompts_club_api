# Generated by Django 3.1.7 on 2021-06-05 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("scenario", "0003_auto_20210604_2346"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rating",
            name="scenario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="scenario.scenario"
            ),
        ),
    ]
