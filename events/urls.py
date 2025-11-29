from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('build/<uuid:profile_uuid>/', views.EventBuildView.as_view(), name='event_build'),
    path('delete/<uuid:profile_uuid>/', views.EventDeleteView.as_view(), name='event_delete'),
    path('interest/add/<uuid:profile_uuid>/<uuid:event_uuid>/', views.AddInterestView.as_view(), name='add_interest'),
    path('interest/remove/<uuid:profile_uuid>/<uuid:event_uuid>/', views.RemoveInterestView.as_view(), name='remove_interest'),
]
