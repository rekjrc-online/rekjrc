from .models import Sponsor

def sponsors_context(request):
    sponsors = Sponsor.objects.filter(deleted=False).order_by('?')[:3]
    return {'sponsors_list': sponsors}
