from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

from apps.scenario.models import Scenario


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")


class Folder(models.Model):
    STATUS_CHOICES = (
        ("private", "Private"),
        ("published", "Published"),
    )

    user = models.ForeignKey(
        User,
        related_name="folders",
        help_text="The creator of the folder.",
        on_delete=models.CASCADE
    )
    scenarios = models.ManyToManyField(
        Scenario,
        blank=True,
        help_text="Scenarios added to the folder, could be anyone\'s as long "\
                    "as they are public or made by the folder owner.",
        related_name="added_to")

    slug = models.SlugField(db_index=True, help_text="Well formatted slug, for url lookups.")
    name = models.CharField(max_length=70, help_text="Folder name.")
    description = models.TextField(
        max_length=400,
        blank=True,
        help_text="Summary of the folder contents.")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="private",
        help_text="Wheter it can be seen by other users or not.",
        db_index=True
    )
    objects = models.Manager()  # default manager
    published = PublishedManager()  # custom manager
    tags = TaggableManager()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}: {self.description[:10]} " \
               f"(children: {self.children.count()}, " \
               f"scenarios: {self.scenarios.count()})"


Folder.add_to_class(
    "parents",
    models.ManyToManyField(
        Folder,
        blank=True,
        help_text="Parent folders. Notice that a folder can have parent folders from " \
                      "multiple users.",
        related_name="children")
)
