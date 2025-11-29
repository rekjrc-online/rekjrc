from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Store
from .forms import StoreForm
from profiles.models import Profile

class StoreListView(LoginRequiredMixin, ListView):
    model = Store
    template_name = 'stores/store_list.html'
    context_object_name = 'stores'

    def get_queryset(self):
        return Store.objects.filter(profile__human=self.request.user)

class StoreBuildView(LoginRequiredMixin, CreateView):
    model = Store
    form_class = StoreForm
    template_name = 'stores/store_form.html'

    def dispatch(self, request, *args, **kwargs):
        profile_uuid = kwargs.get('profile_uuid')
        self.profile = get_object_or_404(Profile, uuid=profile_uuid, human=request.user)
        if hasattr(self.profile, 'store'):
            return redirect('profiles:detail-profile', self.profile.uuid)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.profile = self.profile
        form.instance.human = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return redirect('profiles:detail-profile', self.profile.uuid)

class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    template_name = 'stores/store_confirm_delete.html'

    def get_object(self):
        profile_uuid = self.kwargs.get('profile_uuid')
        profile = get_object_or_404(Profile, uuid=profile_uuid, human=self.request.user)
        return getattr(profile, 'store', None)

    def get_success_url(self):
        return reverse_lazy('store:list')
