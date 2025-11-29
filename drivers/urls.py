# drivers/urls.py
from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.DriverListView.as_view(), name='driver_list'),
    path('update/<uuid:profile_uuid>/', views.DriverUpdateView.as_view(), name='driver_update'),
]
