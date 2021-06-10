from django.contrib.auth.models import User

from rest_framework import serializers

from ..models import Folder

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields =  ['id', 'name', 'description', 'status', \
                  'created', 'updated', 'user', 'parent', 'scenarios']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class UserPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
