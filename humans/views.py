from django.db.models import Q
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse
from .forms import HumanRegistrationForm
from .models import Human, Invitation
from datetime import timedelta
import random


class HumanRegisterView(CreateView):
    model = Human
    form_class = HumanRegistrationForm
    template_name = 'humans/register.html'
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class HumanLoginView(LoginView):
    template_name = 'humans/login.html'

    def get_success_url(self):
        return '/'


class HumanLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return redirect('/')

    def get_next_page(self):
        return '/'


class HumanUpdateView(LoginRequiredMixin, UpdateView):
    model = Human
    fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
    template_name = 'humans/update.html'
    success_url = '/humans/update'

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        # Ensure the logged-in user is editing their own account only
        if not request.user.is_authenticated:
            return redirect('/humans/login/')
        if str(request.user.id) != str(kwargs.get('pk', request.user.id)):
            # Redirect to that user's own profile instead of allowing edit
            return redirect('profiles:detail-profile', request.user.profile.id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Calculate hours_remaining for invitation cooldown
        recent_invite = Invitation.objects.filter(
            Q(from_human=user) | Q(to_human=user),
            insertdate__gte=timezone.now() - timedelta(hours=12)
        ).order_by('-insertdate').first()

        hours_remaining = 0
        if recent_invite:
            elapsed = timezone.now() - recent_invite.insertdate
            hours_remaining = max(0, 12 - elapsed.total_seconds() / 3600)
        context['hours_remaining'] = hours_remaining

        return context


class GenerateInvitationView(LoginRequiredMixin, View):
    template_name = 'includes/invitations.html'
    login_url = '/humans/login/'

    def get(self, request, *args, **kwargs):
        user = request.user
        recent_invite = Invitation.objects.filter(
            Q(from_human=user) | Q(to_human=user),
            insertdate__gte=timezone.now() - timedelta(hours=12)
        ).order_by('-insertdate').first()

        hours_remaining = 0
        if recent_invite:
            elapsed = timezone.now() - recent_invite.insertdate
            hours_remaining = max(0, 12 - elapsed.total_seconds() / 3600)

        context = {'user': user, 'hours_remaining': hours_remaining}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user

        # Enforce ownership — must be the logged-in user
        if not user.is_authenticated:
            return redirect('/humans/login/')

        # Prevent generation if still in 12-hour cooldown
        recent_invite = Invitation.objects.filter(
            Q(from_human=user) | Q(to_human=user),
            insertdate__gte=timezone.now() - timedelta(hours=12)
        ).first()

        if recent_invite:
            messages.warning(request, "You must wait 12 hours before generating another code.")
            return redirect('profiles:detail-profile', user.profile.id)

        if not user.invitation_code:
            user.invitation_code = str(random.randint(11111111, 99999999))
            user.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))


class VerifyInvitationView(LoginRequiredMixin, View):
    login_url = '/humans/login/'

    def post(self, request, *args, **kwargs):
        current_user = request.user
        code = request.POST.get('code', '').strip()

        # Enforce ownership — a user can only verify their own account
        if not current_user.is_authenticated:
            return redirect('/humans/login/')

        if not code.isdigit() or len(code) != 8:
            messages.error(request, "Please enter a valid 8-digit code.")
            return redirect('/humans/update/')

        try:
            inviter = Human.objects.get(
                invitation_code=code,
                is_active=True,
                is_verified=True
            )
        except Human.DoesNotExist:
            messages.error(request, "Invalid or inactive invitation code.")
            return redirect('/humans/update/')

        if inviter == current_user:
            messages.error(request, "You cannot use your own invitation code.")
            return redirect('/humans/update/')

        # Verify and record
        current_user.is_verified = True
        current_user.save()

        #inviter.invitation_code = None
        #inviter.save()

        try:
            Invitation.objects.create(
                from_human=inviter,
                to_human=current_user
            )
        except Exception as e:
            messages.error(request, "Failed to record invitation.")
            return redirect('/humans/update/')

        messages.success(request, "Invitation verified successfully.")
        return redirect('/humans/update/')
