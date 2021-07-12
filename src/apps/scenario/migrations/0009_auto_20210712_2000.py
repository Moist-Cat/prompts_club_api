# Generated by Django 3.1.7 on 2021-07-12 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scenario', '0008_auto_20210609_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], db_index=True, default='draft', max_length=10),
        ),
    ]
