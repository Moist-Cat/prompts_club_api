from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

from apps.scenario.models import Scenario

class Folder(models.Model):
    user = models.ForeignKey(User,
                             related_name='folders',
                             on_delete=models.CASCADE)
    scenarios = models.ManyToManyField(Scenario,
                                    blank=True,
                                    related_name='folder')

    slug = models.SlugField()
    name = models.CharField(max_length=70)
    description = models.TextField(max_length=400)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


Folder.add_to_class('parent',
                        models.ForeignKey(Folder,
                        null=True,
                        blank=True,
                        related_name='folders',
                        on_delete=models.CASCADE))
