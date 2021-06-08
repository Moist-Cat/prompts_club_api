from rest_framework import serializers
from ..models import Scenario, WorldInfo, Rating, \
                      Comment
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

class ScenarioSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Scenario
        fields = ['id', 'user', 'title', 'description', 'memory',
                  'authors_note', 'prompt', 'nsfw', 'publish', 'created',
                  'updated', 'status']
"""
class ScenarioSerializer(serializers.ModelSerializer):
    worldinfo_set = WorldInfoSerializer(many=True, read_only=True)
    rating_set = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Scenario
        fields = ['id', 'user', 'title', 'description', 'memory',
                  'authors_note', 'prompt', 'nsfw', 'publish', 'created',
                  'updated', 'status', 'worldinfo_set', 'rating_set']
"""
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
