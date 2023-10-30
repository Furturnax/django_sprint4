from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse

from blog.forms import CommentForm, PostForm
from blog.models import Comment, Post


class IsAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user



class PostMixin(IsAuthorMixin, LoginRequiredMixin):

    # model = Post
    # template_name = 'blog/create.html'
    # form_class = PostForm
    # pk_url_kwarg = 'post_id'

    # def handle_no_permission(self):
    #     return reverse('blog:profile',
    #                    kwargs={'post_id': self.kwargs['post_id']})

    # def get_success_url(self):
    #     return reverse('blog:post_detail',
    #                    kwargs={'username': self.request.user.username})

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = PostForm()
    #     return context
    pass


class CommentMixin(LoginRequiredMixin):
    """Миксин раздела комментарии."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})