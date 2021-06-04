from django.urls import path, include
from rest_framework import routers
from . import views

app_name = 'scenarios'

urlpatterns = [
    # deletion urls
    path('delete/<slug:slug>/', views.ScenarioDeleteView.as_view()),
    # edition urls
    path('edit/<slug:slug>/', views.ScenarioEditView.as_view()),
    # creation urls
    path('create/wi/', views.WorldInfoCreateView.as_view()),
    path('create/rating/', views.RatingCreateView.as_view()),
    path('create/', views.ScenarioCreateView.as_view()),
    # read-only urls
    path('<slug:slug>/', views.ScenarioDetailView.as_view()),
    path('', views.ScenarioPublicListView.as_view()),

]
