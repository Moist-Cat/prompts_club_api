from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from rest_framework import status
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from taggit.models import Tag

from ..models import Scenario, Comment, WorldInfo, \
                     Rating
from .serializers import ScenarioSerializer, \
                                CommentSerializer, BaseScenarioSerializer, \
                                WorldInfoSerializer, RatingSerializer, \
                                TagSerializer

UNALOWED_MESSAGE_ERROR = {'err_message': 'Uh, oh... Something went wrong. Want to try again?'}
NOT_FOUND_MESSAGE_ERROR = {'err_message': "Here is not the data you are looking for. "
                                             "Or... it is? Who kwnows, ha ha haaa!"}

# ---scenario views---
class ScenarioCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = BaseScenarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request.user.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, user_pk):
        author = get_object_or_404(User, pk=user_pk)
        serializer.save(author=author)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ScenarioPublicListView(generics.ListAPIView):
    queryset = Scenario.published.all()
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny]

class ScenarioPrivateListView(generics.ListAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    
    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(author=self.request.user.id)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class ScenarioDetailView(generics.RetrieveAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        if obj.status == 'published' or \
                self.request.user == obj.author:
            # May raise a permission denied
            self.check_object_permissions(self.request, obj)

            return obj

class ScenarioEditView(generics.UpdateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = BaseScenarioSerializer
    lookup_field = 'slug'

    def perform_update(self, serializer):
        # check if the scenario was published to 
        # perform the according changes
        if serializer.validated_data['status'] == 'published' and \
                self.get_object().status != 'published':
            serializer.save(publish=timezone.now())
        serializer.save()

    def put(self, request, *args, **kwargs):
        """
        We do 3 checks here.
        1: User is posting the author or 
           the scenario. I would add it sinamically
           but since it is an ImmutableDict, I can not
           do so.
        2: User is not trying to change the author of 
           the scenario to impersonate someone else.
           Notice how the JSON is a string so we have 
           to change it\'s type.
        3: Who is editing the scenario is the author.
        """
        if request.data['author'] and \
               int(request.data['author']) == \
                   self.get_object().author.pk and \
               request.user == self.get_object().author:
            return self.update(request, *args, **kwargs)
        return Response(UNALOWED_MESSAGE_ERROR, status=403)

class ScenarioDeleteView(generics.DestroyAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'

    def delete(self, request, *args, **kwargs):
        if request.user == self.get_object().author:
            return self.destroy(request, *args, **kwargs)
        else:
           return Response(UNALOWED_MESSAGE_ERROR, status=403)

# --- wi views ---
class WorldInfoCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = WorldInfoSerializer

    def post(self, request, *args, **kwargs):
        # notice here that we will 404 if the user
        # tries to make WI for an unexistent scenario
        scenario = get_object_or_404(Scenario, id=request.data['scenario'])
        if request.user == scenario.author:
            return self.create(request, *args, **kwargs)
        return Response(UNALOWED_MESSAGE_ERROR, status=403)

class WorldInfoEditView(generics.UpdateAPIView):
    queryset = WorldInfo.objects.all()
    serializer_class = WorldInfoSerializer

    def put(self, request, *args, **kwargs):
        if 'scenario' in request.data:
            scenario = get_object_or_404(Scenario, id=request.data['scenario'])
            if request.user == scenario.author:
                return self.update(request, *args, **kwargs)
        return Response(status=400)

class WorldInfoDeleteView(generics.DestroyAPIView):
    queryset = WorldInfo.objects.all()
    serializer_class = WorldInfoSerializer

    def delete(self, request, *args, **kwargs):
        world_info = get_object_or_404(WorldInfo, pk=kwargs['pk'])
        if request.user == world_info.scenario.author:
            return self.destroy(request, *args, **kwargs)
        return Response(status=400)

# --- rating views ---
class RatingCreateView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request.user.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, user_pk):
        author = get_object_or_404(User, pk=user_pk)
        serializer.save(user=author)

    def post(self, request, *args, **kwargs):
        # same process than the WI creation
        scenario = get_object_or_404(Scenario, id=request.data['scenario'])
        if request.user == scenario.author:
            return self.create(request, *args, **kwargs)
        return Response(UNALOWED_MESSAGE_ERROR, status=403)

class RatingEditView(generics.UpdateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def put(self, request, *args, **kwargs):
        if 'scenario' in request.data:
            scenario = get_object_or_404(Scenario, id=request.data['scenario'])
            if request.user == scenario.author:
                return self.update(request, *args, **kwargs)
        return Response(status=400)

class RatingDeleteView(generics.DestroyAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def delete(self, request, *args, **kwargs):
        rating = get_object_or_404(Rating, pk=kwargs['pk'])
        if request.user == rating.scenario.author:
            return self.destroy(request, *args, **kwargs)
        return Response(status=400)
# tag views
class ScenarioTagView(generics.ListAPIView):
    queryset = Scenario.published.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'

    def get_object(self):
        queryset = self.filter_queryset(self.queryset)

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
    
        if obj.status == 'published' or \
                self.request.user == obj.author:
            # May raise a permission denied
            self.check_object_permissions(self.request, obj)

            return obj
        # notice how we return an empty
        # (even if serialized) response
        # if the user requests aother user
        # unpublished content

    def get_queryset(self):
        scenario = self.get_object()
        if scenario:
            queryset = scenario.tags.all()
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

class TagCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_object(self):
        queryset = self.filter_queryset(self.queryset)

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
#                         'author': self.request.user.pk}
        obj = get_object_or_404(queryset, **filter_kwargs)


        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        
        return obj

    def post(self, request, *args, **kwargs):
        scenario = self.get_object()
        if 'name' in request.data:
            tag_name = request.data['name']
            scenario.tags.add(request.data['name'])
            return Response(status=201)
        return Response(status=400)
