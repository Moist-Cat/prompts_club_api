from rest_framework import serializers
from ..models import Scenario, WorldInfo, Rating
from taggit.models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'slug', 'name']

class WorldInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorldInfo
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

class ScenarioPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'user', 'title', 'description', 'nsfw', 'publish', 'created',
                  'updated', 'status']

class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'user', 'title', 'description', 'memory',
                  'authors_note', 'prompt', 'nsfw', 'publish', 'created',
                  'updated', 'status']
