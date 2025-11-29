from django.urls import path
from .views import *

app_name = 'stores'

urlpatterns = [
    path("", StoreListView.as_view(), name="store_list"),
    path("build/<uuid:profile_uuid>/", StoreBuildView.as_view(), name="store_build"),
    path("delete/<uuid:profile_uuid>/", StoreDeleteView.as_view(), name="store_delete"),
]