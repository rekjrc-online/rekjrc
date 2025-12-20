from django.urls import path
from . import views

app_name = 'races'

urlpatterns = [
    path("", views.RaceListView.as_view(), name="race_list"),
    path("build/<uuid:profile_uuid>/", views.RaceBuildView.as_view(), name="race_build"),
    path("delete/<uuid:profile_uuid>/", views.RaceDeleteView.as_view(), name="race_delete"),
    path("join/<uuid:profile_uuid>/", views.RaceJoinView.as_view(), name="race_join"),
    path("locktoggle/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceLockToggleView.as_view(), name="race_lock_toggle"),
    path("upload-lapmonitor/<uuid:race_uuid>/", views.LapMonitorUploadView.as_view(), name="lapmonitor_upload"),
    path("drag-race/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceDragRaceView.as_view(), name="race_drag_race"),
    path("crawler-comp/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceCrawlerCompView.as_view(), name="race_crawler_comp"),
    path("crawler-comp/run/<uuid:profile_uuid>/<uuid:race_uuid>/<uuid:racedriver_uuid>/", views.RaceCrawlerRunView.as_view(), name="race_crawler_run"),
    path("crawler-comp/finish/<uuid:profile_uuid>/<uuid:race_uuid>/", views.RaceCrawlerFinishView.as_view(), name="race_crawler_finish"),
    path("stopwatch-race/<uuid:profile_uuid>/<uuid:race_uuid>/", views.StopwatchRaceListView.as_view(), name="stopwatch_race_list"),
    path("stopwatch-race/<uuid:profile_uuid>/<uuid:race_uuid>/<uuid:racedriver_uuid>/", views.StopwatchRaceRunView.as_view(), name="stopwatch_race_run"),
    path("stopwatch-race/<uuid:profile_uuid>/<uuid:race_uuid>/finish/", views.StopwatchRaceFinishView.as_view(), name="stopwatch_race_finish"),
    path("longjump-race/<uuid:profile_uuid>/<uuid:race_uuid>/", views.LongJumpListView.as_view(), name="longjump_race_list"),
    path("longjump-race/<uuid:profile_uuid>/<uuid:race_uuid>/<uuid:racedriver_uuid>/", views.LongJumpRunView.as_view(), name="longjump_race_run"),
    path("longjump-race/<uuid:profile_uuid>/<uuid:race_uuid>/finish/", views.LongJumpFinishView.as_view(), name="longjump_race_finish"),
    path("topspeed-race/<uuid:profile_uuid>/<uuid:race_uuid>/", views.TopSpeedRaceListView.as_view(), name="topspeed_race_list"),
    path("topspeed-race/<uuid:profile_uuid>/<uuid:race_uuid>/<uuid:racedriver_uuid>/", views.TopSpeedRaceRunView.as_view(), name="topspeed_race_run"),
    path("topspeed-race/<uuid:profile_uuid>/<uuid:race_uuid>/finish/", views.TopSpeedRaceFinishView.as_view(), name="topspeed_race_finish"),
]