from django.urls import path
from . import views

app_name = 'races'

urlpatterns = [
    path("", views.RaceListView.as_view(), name="race_list"),
    path("build/<uuid:profile_uuid>/", views.RaceBuildView.as_view(), name="race_build"),
    path("delete/<uuid:profile_uuid>/", views.RaceDeleteView.as_view(), name="race_delete"),
    path("join/<uuid:profile_uuid>/", views.RaceJoinView.as_view(), name="race_join"),
    path("upload-lapmonitor/<uuid:race_uuid>/", views.LapMonitorUploadView.as_view(), name="lapmonitor_upload"),
    path("drag-race/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceDragRaceView.as_view(), name="race_drag_race"),
    path("crawler-comp/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceCrawlerCompView.as_view(), name="race_crawler_comp"),
    path("crawler-comp/run/<uuid:profile_uuid>/<uuid:race_uuid>/<uuid:racedriver_uuid>/", views.RaceCrawlerRunView.as_view(), name="race_crawler_run"),
    path("crawler-comp/finish/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceCrawlerFinishView.as_view(), name="race_crawler_finish"),
]