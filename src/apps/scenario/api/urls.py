from django.urls import path, include
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register('worldinfo', views.WorldInfoViewSet)
# router.register('rating', views.RatingViewSet)

app_name = "scenarios"

urlpatterns = [
    path("<slug:slug>/delete/", views.ScenarioDeleteView.as_view()),
    path("<slug:slug>/edit/", views.ScenarioEditView.as_view()),
    path("<slug:slug>/worldinfo/", views.ScenarioWIListView.as_view()),
    path("<slug:slug>/ratings/", views.ScenarioRatingListView.as_view()),
    path("<slug:slug>/ratings/average/", views.ScenarioAverageRatingView.as_view()),
    path("mine/", views.ScenarioPrivateListView.as_view()),
    path("make/", views.ScenarioCreateView.as_view()),
    path("<slug:slug>/", views.ScenarioDetailView.as_view()),
    path("", views.ScenarioPublicListView.as_view()),
    # tag views
    path("<slug:slug>/tag/make/", views.ScenarioTagCreateView.as_view()),
    path("<slug:slug>/tag/<pk>/delete/", views.ScenarioTagDeleteView.as_view()),
    path("tag/<slug:slug>/", views.ScenarioPublicFilteredByTag.as_view()),
    path("tag/<slug:slug>/mine/", views.ScenarioPrivateFilteredByTag.as_view()),
    path("<slug:slug>/tag/", views.ScenarioTagListView.as_view()),
    # wi views
    path("worldinfo/make/", views.WorldInfoCreateView.as_view()),
    path("worldinfo/<pk>/edit/", views.WorldInfoEditView.as_view()),
    path("worldinfo/<pk>/delete/", views.WorldInfoDeleteView.as_view()),
    # rating views
    path("rating/make/", views.RatingCreateView.as_view()),
    path("rating/<pk>/edit/", views.RatingEditView.as_view()),
    path("rating/<pk>/delete/", views.RatingDeleteView.as_view()),
]
