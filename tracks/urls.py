from django.urls import path
from . import views

app_name = 'tracks'

urlpatterns = [
    path("", views.TrackListView.as_view(), name="track_list"),
    path("build/<uuid:profile_uuid>/", views.TrackBuildView.as_view(), name="track_build"),
    path("delete/<uuid:profile_uuid>/", views.TrackDeleteView.as_view(), name="track_delete"),
]