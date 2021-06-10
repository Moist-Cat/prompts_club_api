from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from taggit.models import Tag

from ..models import Scenario, WorldInfo, Rating
from .permissions import CanReadObject, IsAuthor
from .serializers import ScenarioSerializer, WorldInfoSerializer, \
                                RatingSerializer, TagSerializer, \
                                ScenarioPreviewSerializer

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
    serializer_class = ScenarioPreviewSerializer
    permission_classes = [AllowAny]

class ScenarioPrivateListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioPreviewSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.pk)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioDetailView(generics.RetrieveAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'
    permission_classes = [CanReadObject]

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
    permission_classes = [CanReadObject]

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
    permission_classes = [CanReadObject] 
    
    def get_queryset(self):
        scenario = self.queryset.get(slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, scenario)
        queryset = scenario.rating_set.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioAverageRatingView(views.APIView):
    permission_classes = [CanReadObject]
 
    def get(self, *args, **kwargs):
        scenario_slug = self.kwargs['slug']
        scenario = get_object_or_404(Scenario, slug=scenario_slug)
        self.check_object_permissions(self.request, scenario)
        value = scenario.get_average_rating()
        return Response({'average_rating': value}, status=200)

class ScenarioPrivateFilteredByTag(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioPreviewSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        queryset = self.queryset.filter(tags__in=[tag],
                                        user=self.request.user)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioTagListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = TagSerializer
    permission_classes = [CanReadObject]
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
    serializer_class = ScenarioPreviewSerializer
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
class WorldInfoCreateView(generics.CreateAPIView):
    queryset = WorldInfo.objects.all()
    serializer_class = WorldInfoSerializer
    permission_classes=[IsAuthenticated, IsAuthor]

    def perform_create(self, serializer):
        scenario = serializer.validated_data['scenario']
        self.check_object_permissions(self.request, scenario)
        serializer.save()

class WorldInfoEditView(generics.UpdateAPIView):
    queryset = WorldInfo.objects.all()
    serializer_class = WorldInfoSerializer
    permission_classes=[IsAuthenticated, IsAuthor]

class WorldInfoDeleteView(generics.DestroyAPIView):
    queryset = WorldInfo.objects.all()
    serializer_class = WorldInfoSerializer
    permission_classes=[IsAuthenticated, IsAuthor]

class RatingCreateView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RatingEditView(generics.UpdateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsAuthor]

class RatingDeleteView(generics.DestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsAuthor]
