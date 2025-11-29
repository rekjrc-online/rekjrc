from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.SupportView.as_view(), name='support'),
]
