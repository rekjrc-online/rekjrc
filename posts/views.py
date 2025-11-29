from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Post, PostLike
from .forms import PostForm

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['human'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.human = self.request.user
        return super().form_valid(form)

class PostDetail(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_uuid'
    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.select_related('human', 'profile'),
            uuid=self.kwargs['post_uuid'])
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        post.liked_by_user = (
            self.request.user.is_authenticated
            and post.likes.filter(human=self.request.user).exists())
        context['likes'] = post.likes.select_related('human').all()
        replies_qs = post.replies.select_related('human', 'profile').order_by('-insertdate')
        paginator = Paginator(replies_qs, 5)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        if self.request.user.is_authenticated:
            for reply in page_obj:
                reply.liked_by_user = reply.likes.filter(human=self.request.user).exists()
                reply.LikeCount = reply.likes.count()
                reply.CommentCount = reply.replies.count()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            replies_html = render(
                self.request,
                'posts/post_replies.html',
                {'replies': page_obj}
            ).content.decode('utf-8')
            return JsonResponse({
                'html': replies_html,
                'has_next': page_obj.has_next()})
        context['replies'] = page_obj
        context['post'] = post
        return context

class PostRepliesAjax(View):
    def get(self, request, post_uuid):
        post = get_object_or_404(Post, uuid=post_uuid)
        replies_qs = post.replies.select_related('profile', 'human').order_by('-insertdate')
        paginator = Paginator(replies_qs, 5)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        if request.user.is_authenticated:
            for reply in page_obj:
                reply.liked_by_user = reply.likes.filter(human=request.user).exists()
                reply.LikeCount = reply.likes.count()
                reply.CommentCount = reply.replies.count()
        html = render(
            request,
            'posts/_reply_item.html',
            {'posts': page_obj}
        ).content.decode('utf-8')
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next()})

class PostReplyView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_reply.html'
    login_url = '/humans/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['human'] = self.request.user
        return kwargs

    def form_valid(self, form):
        parent_post = get_object_or_404(Post, uuid=self.kwargs['post_uuid'])
        form.instance.human = self.request.user
        form.instance.parent = parent_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('posts:post_detail', args=[self.kwargs['post_uuid']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_post'] = get_object_or_404(Post, uuid=self.kwargs['post_uuid'])
        return context

class HomepageView(ListView):
    model = Post
    template_name = 'homepage.html'
    context_object_name = 'posts'
    ordering = ['-insertdate']
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            for post in context['posts']:
                post.liked_by_user = post.likes.filter(human=self.request.user).exists()
        return context
    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
            object_list = page_obj.object_list
        except (EmptyPage, PageNotAnInteger):
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                page_obj = None
                object_list = []
                is_paginated = False
                return paginator, page_obj, object_list, is_paginated
            else:
                raise
        is_paginated = page_obj.has_other_pages()
        return paginator, page_obj, object_list, is_paginated
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(self.request, 'posts/post_list.html', {'posts': context['posts']})
        return super().render_to_response(context, **response_kwargs)

@login_required
def toggle_like(request, post_id):
    try:
        human = request.user
    except AttributeError:
        return redirect('/')

    post = get_object_or_404(Post, uuid=post_id)
    like, created = PostLike.objects.get_or_create(human=human, post=post)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def toggle_like_ajax(request, post_id):
    try:
        human = request.user
        post = get_object_or_404(Post, uuid=post_id)
        like, created = PostLike.objects.get_or_create(human=human, post=post)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['content']
    template_name = 'posts/post_form.html'
    login_url = '/humans/login/'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.human != request.user:
            return redirect('profiles:detail-profile', profile_uuid=post.profile.uuid)
        return super().dispatch(request, *args, **kwargs)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    login_url = '/humans/login/'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.human != request.user:
            return redirect('profiles:detail-profile', profile_uuid=post.profile.uuid)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('posts:homepage')