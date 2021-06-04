from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey

from taggit.managers import TaggableManager

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,
            self).get_queryset().filter(status='published')

class Scenario(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    author = models.ForeignKey(User,
                               related_name='scenarios',
                               on_delete=models.CASCADE,
                               null=True)

    title = models.CharField(max_length=70, unique=True, blank=False)
    slug = models.SlugField()
    tags = TaggableManager()

    description = models.TextField(max_length=400)
    prompt = models.TextField(max_length=2000, blank=False)
    memory = models.TextField(max_length=1000)
    authors_note = models.CharField(max_length=140)
    nsfw = models.BooleanField(default=False)

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10,
                                choices=STATUS_CHOICES,
                                default='draft')

    objects = models.Manager() # default manager
    published = PublishedManager() # custom manager

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_average_rating(self):
       total = 0
       ratings = self.rating_set.all()
       for rating in ratings:
           total+=rating.value
       return total/ratings.count()
    
    def __str__(self):
        return self.title

# Base Model for Scenario-dependant Models
class BaseModel(models.Model):
    RELATED_NAME = None

    scenario = models.ForeignKey(Scenario,
                                on_delete=models.CASCADE,
                                related_name=RELATED_NAME)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.scenario.title

class Rating(BaseModel):
    RELATED_NAME = 'ratings'
    RATING_CHOICES = (
        (1, 1), (2, 2),
        (3, 3), (4, 4),
        (5, 5)
    )
    user = models.OneToOneField(User,
                                on_delete=models.DO_NOTHING,
                                related_name='ratings')
    value = models.IntegerField(choices=RATING_CHOICES)
    
    def __str__(self):
        return f'{self.user} rated {self.scenario}: {self.value}'

class WorldInfo(BaseModel):
    RELATED_NAME = 'world_info'

    keys = models.CharField(max_length=200)
    entry = models.TextField(max_length=500)

class Comment(BaseModel):
    RELATED_NAME = 'comments'

    name = models.CharField(max_length=80, default='Anonymous')
    email = models.EmailField(blank=True)
    body = models.TextField(max_length=2000)
    active = models.BooleanField(default=True)
