from django.views.generic import TemplateView

class PrivacyView(TemplateView):
    template_name = 'privacy/privacy.html'

class TermsView(TemplateView):
    template_name = 'privacy/terms.html'

class PrivacyViewCrawlercomp(TemplateView):
    template_name = 'privacy/privacy_crawler_comp.html'
