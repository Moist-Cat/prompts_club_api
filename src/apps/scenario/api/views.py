from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from taggit.models import Tag

from ..models import Scenario, Comment, WorldInfo, \
                     Rating
from .permissions import CanReadObject, IsAuthor
from .serializers import ScenarioSerializer, CommentSerializer, \
                                WorldInfoSerializer, RatingSerializer, \
                                TagSerializer

#permission_classes = [AllowAny]

# ---scenario views---
class ScenarioCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def perform_create(self, serializer):
        user = get_object_or_404(User, username=self.request.user)
        serializer.save(user=user)

class ScenarioPublicListView(generics.ListAPIView):
    queryset = Scenario.published.all()
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny]

class ScenarioPrivateListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioDetailView(generics.RetrieveAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'
    permission_classes = [CanReadObject, AllowAny]

class ScenarioEditView(generics.UpdateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated, IsAuthor]
    def perform_update(self, serializer):
        # check if the scenario was published to 
        # perform the according changes
        if serializer.validated_data['status'] == 'published' and \
                self.get_object().status != 'published':
            serializer.save(publish=timezone.now())
        serializer.save()

class ScenarioDeleteView(generics.DestroyAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated, IsAuthor]

class ScenarioWIListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = WorldInfoSerializer
    permission_classes = [CanReadObject, AllowAny]

    def get_queryset(self):
        scenario = self.queryset.get(slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, scenario)
        queryset = scenario.worldinfo_set.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioRatingListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [CanReadObject, AllowAny] 
    
    def get_queryset(self):
        scenario = self.queryset.get(slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, scenario)
        queryset = scenario.rating_set.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioCommentListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [CanReadObject, AllowAny] 
    
    def get_queryset(self):
        scenario = self.queryset.get(slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, scenario)
        queryset = scenario.comment_set.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset
    
class ScenarioPrivateFilteredByTag(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        print(tag)
        queryset = self.queryset.filter(tags__in=[tag],
                                        user=self.request.user)
        print(queryset)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioTagListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = TagSerializer
    permission_classes = [CanReadObject, IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        scenario = self.queryset.get(slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, scenario)
        queryset = scenario.tags.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioPublicFilteredByTag(generics.ListAPIView):
    queryset = Scenario.published.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        queryset = self.queryset.filter(tags__in=[tag])
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

# tag views
"""
I have to acces through the scenario 
tag manager, since I can not save it 
without checking the permissions 

This:
    serializer.validated_data['scenario']

Can not be done since the scenario id is 
not posted with the tag unlike the other models.
We will use the slug to get both the scenario and the tags to 
validate and filter the data.
I hope it is not too confusing...
And I (of course) have to return the data manually.
"""
class TagDeleteView(generics.GenericAPIView):
    queryset = Scenario.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    lookup_field = 'slug'

    @action(detail=True,
            methods=['delete'])
    def delete(self, request, *args, **kwargs):
        scenario = self.get_object()
        tag_id = kwargs['pk']
        tag = scenario.tags.get(pk=tag_id)
        tag.delete()
        return Response(status=204)

class TagCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
    lookup_field = 'slug'

    def create(self, request, *args, **kwargs):
        if 'name' in request.data:
            scenario = self.get_object()
            tag_name = request.data['name']
            scenario.tags.add(request.data['name'])
            new_tag = scenario.tags.get(name=tag_name)
            response_json = {'id': new_tag.id, 'slug': new_tag.slug,
                         'name': new_tag.name}
            return Response(response_json, status=201)
        return Response(status=400)

# --- wi views ---
class WorldInfoViewSet(viewsets.ModelViewSet):
    queryset = WorldInfo.objects.all()
    serializer_class = WorldInfoSerializer
    permission_classes=[IsAuthenticated, IsAuthor]

    def perform_create(self, serializer):
        scenario = serializer.validated_data['scenario']
        self.check_object_permissions(self.request, scenario)
        serializer.save()

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

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
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

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
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
