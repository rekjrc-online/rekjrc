from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path("", views.ClubListView.as_view(), name="club_list"),
    path("build/<uuid:profile_uuid>/", views.ClubBuildView.as_view(), name="club_build"),
    path("delete/<uuid:profile_uuid>/", views.ClubDeleteView.as_view(), name="club_delete"),
]