from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import Scenario, Comment
from .serializers import ScenarioSerializer, \
                                CommentSerializer, BaseScenarioSerializer, \
                                WorldInfoSerializer, RatingSerializer

UNALOWED_MESSAGE_ERROR = {'err_message': 'Uh, oh... Something went wrong. Want to try again?'}
NOT_FOUND_MESSAGE_ERROR = {'err_message': "Here is not the data you are looking for. "
                                             "Or... it is? Who kwnows, ha ha haaa!"}

# ---scenario views---
class ScenarioCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = BaseScenarioSerializer
    permission_classes = [AllowAny]

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

class ScenarioDetailView(generics.RetrieveAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        # make sure is their content or it is public
        if request.user == self.get_object().author or \
             self.get_object().status == 'published':
            return self.retrieve(self, request, *args, **kwargs)
        else:
            return Response(NOT_FOUND_MESSAGE_ERROR, status=404)

class ScenarioEditView(generics.UpdateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = BaseScenarioSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def perform_update(self, serializer):
        # check if the scenario was published to 
        # perform the according changes
        if serializer.validated_data['status'] == 'published' and \
                self.get_object().status != 'published':
            serializer.save(publish=timezone.now())
        serializer.save()

    def put(self, request, *args, **kwargs):
        if request.data['author'] == self.get_object().author and \
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


class WorldInfoDeleteView(generics.DestroyAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
    lookup_field = 'slug'

    def delete(self, request, *args, **kwargs):
        if request.user == self.get_object().author:
            return self.destroy(request, *args, **kwargs)
        else:
           return Response(UNALOWED_MESSAGE_ERROR, status=403)

# --- rating views ---
class RatingCreateView(generics.CreateAPIView):
    queryset = Scenario.objects.all()
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
