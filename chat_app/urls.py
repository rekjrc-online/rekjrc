from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path("club/<uuid:profile_uuid>/", views.ChatRoomView.as_view(), name="club_chat"),
    path("team/<uuid:profile_uuid>/", views.ChatRoomView.as_view(), name="team_chat"),
    path("store/<uuid:profile_uuid>/", views.ChatRoomView.as_view(), name="store_chat"),
    path("location/<uuid:profile_uuid>/", views.ChatRoomView.as_view(), name="location_chat"),
]
