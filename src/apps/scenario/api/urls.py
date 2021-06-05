from django.urls import path, include
from rest_framework import routers
from . import views

#router = routers.DefaultRouter()
#router.register('wi', views.WorldInfoViewSet)

app_name = 'scenarios'

urlpatterns = [
    # wi urls
    path('worldinfo/<pk>/edit/', views.WorldInfoEditView.as_view()),
    path('worldinfo/<pk>/delete/', views.WorldInfoDeleteView.as_view()),
    path('worldinfo/create/', views.WorldInfoCreateView.as_view()),
    # ratings urls
    path('rating/<pk>/edit/', views.RatingEditView.as_view()),
    path('rating/<pk>/delete/', views.RatingDeleteView.as_view()),
    path('rating/create/', views.RatingCreateView.as_view()),
    # scenario urls
    path('<slug:slug>/tag/', views.ScenarioTagView.as_view()),
    path('<slug:slug>/tag/create/', views.TagCreateView.as_view()),
#    path('tag/delete', view.TagCreateView.as_view()),
    path('<slug:slug>/delete/', views.ScenarioDeleteView.as_view()),
    path('<slug:slug>/edit/', views.ScenarioEditView.as_view()),
    path('mine/', views.ScenarioPrivateListView.as_view()),
    path('create/', views.ScenarioCreateView.as_view()),
    path('<slug:slug>/', views.ScenarioDetailView.as_view()),
    path('', views.ScenarioPublicListView.as_view()),

]
