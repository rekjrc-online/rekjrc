from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.TeamListView.as_view(), name='team_list'),
    path('build/<uuid:profile_uuid>/', views.TeamBuildView.as_view(), name='team_build'),
    path('delete/<uuid:profile_uuid>/', views.TeamDeleteView.as_view(), name='team_delete'),
]
