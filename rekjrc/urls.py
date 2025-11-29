from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from posts import views as post_views

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request):
    return render(request, "500.html", status=500)

urlpatterns = [
    path('', post_views.HomepageView.as_view(), name='homepage'),
    path('admin/', admin.site.urls),
    path('builds/', include('builds.urls')),
    path('clubs/', include('clubs.urls')),
    path('drivers/', include('drivers.urls')),
    path('events/', include('events.urls')),
    path('humans/', include('humans.urls')),
    path('locations/', include('locations.urls')),
    path('posts/', include('posts.urls')),
    path('privacy/', include('privacy.urls')),
    path('profiles/', include('profiles.urls')),
    path('races/', include('races.urls')),
    path('sponsors/', include('sponsors.urls')),
    path('stores/', include('stores.urls')),
    path('stripe/', include('stripe_app.urls')),
    path('support/', include('support.urls')),
    path('teams/', include('teams.urls')),
    path('tracks/', include('tracks.urls')),
    path('u/', include('urls_app.urls')),

]

handler404 = 'rekjrc.urls.custom_404'
handler500 = 'rekjrc.urls.custom_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
