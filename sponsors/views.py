from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from .models import Sponsor, SponsorClick

class SponsorClickView(View):
    def post(self, request, sponsor_id):
        try:
            sponsor = Sponsor.objects.get(pk=sponsor_id)
        except Sponsor.DoesNotExist:
            return HttpResponseBadRequest("Invalid sponsor")
        human = request.user if request.user.is_authenticated else None
        ip = self.get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        SponsorClick.objects.create(
            human=human,
            sponsor=sponsor,
            ip_address=ip,
            user_agent=ua
        )
        return JsonResponse({'redirect_url': sponsor.website})

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
