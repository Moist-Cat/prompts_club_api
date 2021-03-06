# Generated by Django 3.1.7 on 2021-06-09 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_auto_20210609_1702"),
    ]

    operations = [
        migrations.AlterField(
            model_name="folder",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="accounts.folder",
            ),
        ),
    ]
