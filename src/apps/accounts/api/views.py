from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from django.db.models.query import QuerySet
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from taggit.models import Tag

from apps.scenario.api.serializers import ScenarioSerializer
from apps.scenario.api.permissions import IsAuthor, CanReadObject
from apps.scenario.models import Scenario

from ..models import Folder
from .serializers import UserSerializer, FolderSerializer
from .permissions import IsSelf


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
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny, IsSelf]
    lookup_field = 'username'

    def get_queryset(self):
        user = self.queryset.get(username=self.kwargs['username'])
        queryset = user.scenarios.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

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
class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated, IsAuthor]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True,
            methods=['put'])
    def edit(self, request, *args, **kwargs):
        return self.update(request, *args, *kwargs)
    @action(detail=True,
            methods=['delete'])
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, *kwargs)
    @action(detail=False,
            methods=['post'])
    def make(self, request, *args, **kwargs):
        return self.create(request, *args, *kwargs)
    @action(detail=True,
            methods=['post'])
    def details(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class UserParentFolders(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = get_list_or_404(self.queryset, parent=None)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset
        

class FolderChildren(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [AllowAny, CanReadObject]
    lookup_field = 'slug'
    
    def get_queryset(self):
        folder = get_object_or_404(self.queryset, slug=self.kwargs['slug'])
        queryset = folder.folders.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class FolderScenarios(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny, CanReadObject]
    lookup_field = 'slug'
    
    def get_queryset(self):
        folder = get_object_or_404(self.queryset, slug=self.kwargs['slug'])
        queryset = folder.scenarios.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset
