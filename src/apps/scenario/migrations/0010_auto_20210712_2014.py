# Generated by Django 3.1.7 on 2021-07-12 20:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scenario', '0009_auto_20210712_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='review',
            field=models.TextField(help_text='Comment from the user', max_length=400),
        ),
        migrations.AlterField(
            model_name='rating',
            name='value',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], help_text='Rating value, from 1 to 5.'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='authors_note',
            field=models.CharField(blank=True, help_text='Context for the AI, more essential tan memory, but also shorter: 500 chars max', max_length=500),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='description',
            field=models.TextField(blank=True, help_text='Summary of the prompt content.', max_length=400),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='memory',
            field=models.TextField(blank=True, help_text='Context for the AI. 3K chars max.', max_length=3000),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='nsfw',
            field=models.BooleanField(default=False, help_text='Wheter it is safe to read it at work or not. Default false'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='prompt',
            field=models.TextField(help_text='Main block of text. No more than 10K chars. Required.', max_length=10000),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='slug',
            field=models.SlugField(help_text='Well formatted slug, for url lookups.', unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], db_index=True, default='draft', help_text='Wheter it can be seen by other users or not.', max_length=10),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='title',
            field=models.CharField(help_text='Unique title', max_length=70, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='user',
            field=models.ForeignKey(help_text='Scenario author', on_delete=django.db.models.deletion.CASCADE, related_name='scenarios', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='worldinfo',
            name='entry',
            field=models.TextField(help_text='Context triggered by a pre-defined key.', max_length=500),
        ),
        migrations.AlterField(
            model_name='worldinfo',
            name='keys',
            field=models.CharField(help_text='Key for the WI entry.', max_length=200),
        ),
    ]
