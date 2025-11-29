from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import Http404
from .models import ShortURL, ClickEvent


def short_url_redirect(request, code):
    """
    Redirects to the destination URL for a given short code.
    Logs the click in ClickEvent.
    """
    short = get_object_or_404(ShortURL, code=code)

    if not short.active:
        # Optionally, show a custom "link inactive" page
        raise Http404("This short link is inactive.")

    # Log the click
    ClickEvent.objects.create(
        short_url=short,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        ip_address=get_client_ip(request),
    )

    return redirect(short.destination_url)


def get_client_ip(request):
    """
    Retrieves client IP considering possible reverse proxies.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip
