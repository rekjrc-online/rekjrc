from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.ProfilesListView.as_view(), name='profiles-list'),
    path('build/', views.ProfileBuildView.as_view(), name='build-profile'),
    path('<uuid:profile_uuid>/', views.ProfileDetailView.as_view(), name='detail-profile'),
    path('update/<uuid:profile_uuid>/', views.ProfileUpdateView.as_view(), name='update-profile'),
    path('delete/<uuid:profile_uuid>/', views.ProfileDeleteView.as_view(), name='delete-profile'),
]
