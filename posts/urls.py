from django.views.generic import TemplateView
from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
	path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('<uuid:post_uuid>/', views.PostDetail.as_view(), name='post_detail'),
    path('reply/<uuid:post_uuid>/', views.PostReplyView.as_view(), name='post_reply'),
    path('like-ajax/<uuid:post_uuid>/', views.toggle_like_ajax, name='post_like_ajax'),
    path('replies/ajax/<uuid:post_uuid>/', views.PostRepliesAjax.as_view(), name='PostRepliesAjax'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
]