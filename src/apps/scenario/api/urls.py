from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('worldinfo', views.WorldInfoViewSet)
router.register('rating', views.RatingViewSet)
router.register('comment', views.CommentViewSet)

app_name = 'scenarios'

urlpatterns = [
    path('<slug:slug>/delete/', views.ScenarioDeleteView.as_view()),
    path('<slug:slug>/edit/', views.ScenarioEditView.as_view()),
    path('<slug:slug>/worldinfo/', views.ScenarioWIListView.as_view()),
    path('<slug:slug>/ratings/', views.ScenarioRatingListView.as_view()),
    path('<slug:slug>/comments/', views.ScenarioCommentListView.as_view()),
    path('mine/', views.ScenarioPrivateListView.as_view()),
    path('make/', views.ScenarioCreateView.as_view()),
    path('<slug:slug>/', views.ScenarioDetailView.as_view()),
    path('', views.ScenarioPublicListView.as_view()),
    # tag views
    path('<slug:slug>/tag/make/', views.TagCreateView.as_view()),
    path('<slug:slug>/tag/<pk>/delete/', views.TagDeleteView.as_view()),
    path('tag/<slug:slug>/', views.ScenarioPublicFilteredByTag.as_view()),
    path('tag/<slug:slug>/mine/', views.ScenarioPrivateFilteredByTag.as_view()),
    path('<slug:slug>/tag/', views.ScenarioTagListView.as_view()),
    # router views
    path('', include(router.urls)),

]
