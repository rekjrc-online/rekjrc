from django.urls import path
from locations.views import LocationListView, LocationBuildView, LocationDeleteView

app_name = 'locations'

urlpatterns = [
    path('', LocationListView.as_view(), name='location_list'),
    path('build/<uuid:profile_uuid>/', LocationBuildView.as_view(), name='location_build'),
    path('delete/<uuid:profile_uuid>/', LocationDeleteView.as_view(), name='location_delete'),
]
