# Generated by Django 3.1.7 on 2021-07-12 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20210618_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='parents',
            field=models.ManyToManyField(blank=True, help_text='Parent folders. Notice that a folder can have parent folders from multiple users', related_name='children', to='accounts.Folder'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='slug',
            field=models.SlugField(help_text='Well formatted slug, for url lookups.'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='status',
            field=models.CharField(choices=[('private', 'Private'), ('published', 'Published')], db_index=True, default='private', help_text='Wheter it can be seen by other users or not', max_length=10),
        ),
    ]