from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError

#
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
#

from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from taggit.models import Tag

from apps.scenario.api.serializers import ScenarioSerializer, \
                                          ScenarioPreviewSerializer
from apps.scenario.api.permissions import IsAuthor, CanReadObject
from apps.scenario.api.views import TagDeleteView, TagCreateView, \
                                    ScenarioPrivateFilteredByTag, \
                                    ScenarioTagListView, \
                                    ScenarioPublicFilteredByTag
from apps.scenario.models import Scenario

from ..models import Folder
from .serializers import UserSerializer, FolderSerializer, \
                         UserPOSTSerializer
from .permissions import IsSelf


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPOSTSerializer
    permission_classes = [AllowAny]


    def perform_create(self, serializer):
        raw_password = serializer.validated_data['password']
        password = make_password(raw_password)
        serializer.save(password=password)

class UserListContentView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ScenarioSerializer
    permission_classes = [AllowAny]
    lookup_field = 'username'

    def get_queryset(self):
        user = get_object_or_404(self.queryset,
                                 username=self.kwargs['username'])
        if user:
            queryset = user.scenarios.filter(status='published')
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class UserListFoldersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [AllowAny]
    lookup_field = 'username'

    def get_queryset(self):
        user = get_object_or_404(self.queryset,
                             username=self.kwargs['username'])
        queryset = user.folders.filter(status='published')
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveAPIView):
    # needed to get the username when 
    # showing scenarios in the front-end
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserPOSTSerializer
    lookup_field = 'username'
    
    def delete(self, request, *args, **kwargs):
        if self.get_object() == request.user:
            return self.destroy(self, request, *args, **kwargs)
        else:
           return Response(status=403)

# --- folder views ---
class FolderCreateView(generics.CreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FolderEditView(generics.UpdateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated, IsAuthor]

    def perform_update(self, serializer):
        # check if the scenario was published to 
        # perform the according changes
        if serializer.validated_data['status'] == 'published' and \
                self.get_object().status != 'published':
            serializer.save(publish=timezone.now())
        serializer.save()

class FolderDeleteView(generics.DestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated, IsAuthor]

class FolderPublishedView(generics.ListAPIView):
    queryset = Folder.published.all()
    serializer_class = FolderSerializer
    permission_classes = [AllowAny]

class FolderDetailView(generics.RetrieveAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    lookup_field = 'slug'
    permission_classes = [CanReadObject]

class UserParentFolders(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    
    def get_queryset(self):
        queryset = get_list_or_404(self.queryset,
                                   parent=None,
                                   user=self.request.user)
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset
        

class FolderChildren(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [CanReadObject]
    lookup_field = 'slug'
    
    def get_queryset(self):
        folder_slug = self.kwargs['slug']
        folder = get_object_or_404(self.queryset, slug=folder_slug)
        self.check_object_permissions(self.request, folder)
        queryset = folder.children.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class FolderScenarios(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = ScenarioPreviewSerializer
    permission_classes = [CanReadObject]
    lookup_field = 'slug'
    
    def get_queryset(self):
        folder = get_object_or_404(self.queryset,
                                   slug=self.kwargs['slug'])
        self.check_object_permissions(self.request, folder)
        queryset = folder.scenarios.all()
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

class FolderAddContent(views.APIView):
    queryset = Folder.objects.all()
    permission_classes = [IsAuthenticated, CanReadObject]

    def post(self, request, *args, **kwargs):
        if 'contentype' in request.data:
            content_type = request.data['contentype']

            parent_folder_slug = self.kwargs['slug']
            folder = get_object_or_404(Folder, slug=parent_folder_slug)
            # we have to access to the permission class manually 
            # since we can not allow that the IsAuthor permission class is 
            # applied globally, bacause that would not allow users to 
            # add other people stuff to their folders.
            is_author = IsAuthor()
            perm = is_author.has_object_permission(request, self, folder)
            perm = True
            if perm:
                object_pk = self.kwargs['pk']

                if content_type == 'scenario':
                    scenario = get_object_or_404(Scenario, pk=object_pk)
                    self.check_object_permissions(self.request, scenario)
                    folder.scenarios.add(scenario)
                elif content_type == 'folder':
                    child_folder = get_object_or_404(Folder, pk=object_pk)
                    # We need to check if the user did not save a folder inside 
                    # itself, since that would create a RecursionLimitExceededError 
                    # when checking permissions.
                    #(XXX) It seems a little dirty to do this here though...
                    if folder == child_folder:
                        return Response({
                                         'non_field_erros':
                                         'You can\'t put a folder ' \
                                         'inside itself'
                                         },
                                        status=400)
                    self.check_object_permissions(self.request, child_folder)
                    
                    folder.children.add(child_folder)
                else:
                    return Response({
                                    'non_field_errors':
                                    f'{content_type} is not a valid content_type',
                                    },
                                    status=400)
                return Response(status=200)
        return Response({
                        'non_field_errors':
                        'The contentype can not be empty'
                        },
                        status=400)

# adding tag system to folders too...
# ik it says "scenario", maybe I will do a base class later.
class FolderTagCreateView(TagCreateView):
    queryset = Folder.objects.all()

class FolderTagDeleteView(TagDeleteView):
    queryset = Folder.objects.all()

class FolderPublicFilteredByTag(ScenarioPublicFilteredByTag):
    queryset = Folder.objects.all()

class FolderTagListView(ScenarioTagListView):
    queryset = Folder.objects.all()

class FolderPrivateFilteredByTag(ScenarioPrivateFilteredByTag):
    queryset = Folder.objects.all()
