from django.urls import path
from . import views

app_name = 'builds'

urlpatterns = [
    path("", views.BuildListView.as_view(), name="build_list"),
    path('build/<uuid:profile_uuid>/', views.BuildBuildView.as_view(), name='build_build'),
    path('delete/<uuid:profile_uuid>/', views.BuildDeleteView.as_view(), name='build_delete'),
]
