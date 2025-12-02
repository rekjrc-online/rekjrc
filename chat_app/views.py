from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from profiles.models import Profile
from chat_app.models import ChatMessage

from django.utils import timezone
from datetime import timedelta

class ChatRoomView(LoginRequiredMixin, View):
    template_name = "chat/chat_room.html"

    def get(self, request, profile_uuid):
        if request.user.is_verified==False:
            return redirect('/')
        channel_profile = get_object_or_404(Profile, uuid=profile_uuid)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        messages = ChatMessage.objects.filter(
            channel_profile=channel_profile,
            insertdate__gte=one_hour_ago
        ).select_related("human", "profile").order_by("insertdate")
        profiles = Profile.objects.filter(
            human=request.user,
            profiletype='DRIVER'
        )
        return render(request, self.template_name, {
            "channel_profile": channel_profile,
            "profiles": profiles,
            "messages": messages,
        })

    def post(self, request, profile_uuid):
        channel_profile = get_object_or_404(Profile, uuid=profile_uuid)

        content = request.POST.get("content", "").strip()
        if not content:
            return redirect(request.path)

        profile_uuid = request.POST.get("profile_uuid")
        acting_profile = None

        if profile_uuid:
            acting_profile = get_object_or_404(Profile, uuid=profile_uuid)

        ChatMessage.objects.create(
            human=self.request.user,
            profile=acting_profile,
            channel_profile=channel_profile,
            content=content,
        )

        return redirect(request.path)
