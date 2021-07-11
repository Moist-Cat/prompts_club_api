from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status="published")


class Scenario(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    user = models.ForeignKey(User, related_name="scenarios", on_delete=models.CASCADE)

    title = models.CharField(max_length=70, unique=True)
    slug = models.SlugField(unique=True, db_index=True)

    description = models.TextField(max_length=400, blank=True)
    prompt = models.TextField(max_length=2000)
    memory = models.TextField(max_length=1000, blank=True)
    authors_note = models.CharField(max_length=140, blank=True)
    nsfw = models.BooleanField(default=False)

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    objects = models.Manager()  # default manager
    published = PublishedManager()  # custom manager
    tags = TaggableManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_average_rating(self):
        total = 0
        ratings = self.rating_set.all()
        for rating in ratings:
            total += rating.value
        try:
            return total / ratings.count()
        except ZeroDivisionError:
            return 0

    class Meta:
        ordering = ("-publish",)

    def __str__(self):
        return f'{self.title} made by {self.user}: {self.description[:50]}(...)'


# Base Model for Scenario-dependant Models
class BaseModel(models.Model):
    RELATED_NAME = None

    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name=RELATED_NAME
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created",)

    def __str__(self):
        return f"{self.__class__.__name__} belonging to {self.scenario.title}"


class Rating(BaseModel):
    RELATED_NAME = "rating"
    RATING_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name=RELATED_NAME
    )

    value = models.IntegerField(choices=RATING_CHOICES)

    review = models.TextField(max_length=400)

    def __str__(self):
        return f"{self.user} rated {self.scenario.title}: {self.value}"

    class Meta:
        unique_together = [["scenario", "user"]]


class WorldInfo(BaseModel):
    RELATED_NAME = "world_info"

    keys = models.CharField(max_length=200)
    entry = models.TextField(max_length=500)
