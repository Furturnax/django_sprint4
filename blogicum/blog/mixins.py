from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Comment, Post


class PostMixin:
    """Определена модель и путь к шаблону для CBV."""

    model = Post
    template_name = 'blog/create.html'


class CommentMixin:
    """
    Определена модель и путь к шаблону для CBV.
    Определена функция get_success_url.
    """

    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.pk})


class PostdispatchMixin:
    """Определена функция dispatch."""

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['pk'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class CommentdispatchMixin:
    """Определена функция dispatch."""

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
