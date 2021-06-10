from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import *
from . import views

app_name = 'accounts'

#router = routers.DefaultRouter()
#router.register('folder', views.FolderViewSet)

urlpatterns = [
    # folder views
    path('folder/', views.FolderPublishedView.as_view()),
    path('folder/mine/', views.UserParentFolders.as_view()),
    path('folder/make/', views.FolderCreateView.as_view()),
    path('folder/<slug:slug>/', views.FolderDetailView.as_view()),
    path('folder/<slug:slug>/edit/', views.FolderEditView.as_view()),
    path('folder/<slug:slug>/delete/', views.FolderDeleteView.as_view()),
    path('folder/<slug:slug>/children/', views.FolderChildren.as_view()),
    path('folder/<slug:slug>/scenarios/', views.FolderScenarios.as_view()),
    path('folder/<slug:slug>/add/<pk>/', views.FolderAddContent.as_view()),
    # tag urls
    path('folder/<slug:slug>/tag/make/',
                       views.FolderTagCreateView.as_view()),
    path('folder/<slug:slug>/tag/<pk>/delete/',
                       views.FolderTagDeleteView.as_view()),
    path('folder/tag/<slug:slug>/',
                       views.FolderPublicFilteredByTag.as_view()),
    path('folder/tag/<slug:slug>/mine/',
                      views.FolderPrivateFilteredByTag.as_view()),
    path('folder/<slug:slug>/tag/', views.FolderTagListView.as_view()),
    # user urls
    path('login/', ObtainAuthToken.as_view()),
    path('register/', views.UserCreateView.as_view()),
    path('<username>/content/', views.UserListContentView.as_view()),
    path('<username>/folders/', views.UserListFoldersView.as_view()),
    path('<username>/delete/', views.UserDestroyView.as_view()),
    path('<username>/', views.UserDetailView.as_view()),
    path('', views.UserListView.as_view()),
]
