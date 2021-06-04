from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import *
from . import views

app_name = 'accounts'

urlpatterns = [
    # scenario-related urls
    path('login/', ObtainAuthToken.as_view()),
    path('register/', views.UserCreateView.as_view()),
    path('create/folder/', views.ForlderCreateView.as_view()),
    path('content/<username>', views.UserListContentView.as_view()),
    path('delete/<username>/', views.UserDestroyView.as_view()),
    path('<username>/', views.UserDetailView.as_view()),
    path('', views.UserListView.as_view()),
    # comment urls
    # folder urls
]
