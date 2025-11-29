from django.urls import path
from .views import (
    HumanRegisterView,
    HumanLoginView,
    HumanLogoutView,
    HumanUpdateView,
    GenerateInvitationView,
    VerifyInvitationView,
)
urlpatterns = [
    path('register/', HumanRegisterView.as_view(), name='register'),
    path('login/', HumanLoginView.as_view(), name='login'),
    path('logout/', HumanLogoutView.as_view(), name='logout'),
    path('update/', HumanUpdateView.as_view(), name='update'),
    path('generate-invitation/', GenerateInvitationView.as_view(), name='generate-invitation'),
    path('verify-invitation/', VerifyInvitationView.as_view(), name='verify-invitation'),
]
