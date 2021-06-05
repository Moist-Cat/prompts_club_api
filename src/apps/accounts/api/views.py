from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
#from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
#from rest_framework import mixins
from rest_framework.decorators import action

from apps.scenario.api.serializers import ScenarioSerializer
from .serializers import UserSerializer
from ..models import Folder
from .serializers import FolderSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        raw_password = serializer.validated_data['password']
        password = make_password(raw_password)
        serializer.save(password=password)

class UserListContentView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = generics.get_object_or_404(User, username=kwargs['username'])
        if not request.user != user.username:
            self.queryset = user.scenarios.published.all()
        else:
            self.queryset = user.scenarios
        self.serializer_class = ScenarioSerializer
        return self.list(self, request, *args, **kwargs)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [AllowAny]

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    
    def delete(self, request, *args, **kwargs):
        if self.get_object() == request.user:
            return self.destroy(self, request, *args, **kwargs)
        else:
           return Response(status=403)

# --- folder views ---
class ForlderCreateView(generics.CreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [AllowAny]
