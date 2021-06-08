from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import *
from . import views

app_name = 'accounts'
router = routers.DefaultRouter()
router.register('folders', views.FolderViewSet)

urlpatterns = [
    # scenario-related urls
    path('login/', ObtainAuthToken.as_view()),
    path('register/', views.UserCreateView.as_view()),
    path('<username>/content/', views.UserListContentView.as_view()),
    path('<username>/delete/', views.UserDestroyView.as_view()),
    path('<username>/', views.UserDetailView.as_view()),
    path('', views.UserListView.as_view()),
    # folder views
    path('folders/mine/', views.UserParentFolders.as_view()),
    path('', include(router.urls)),
    path('folders/<slug:slug>/children/', views.FolderChildren.as_view()),
    path('folders/<slug:slug>/scenarios/', views.FolderScenarios.as_view()),
]
