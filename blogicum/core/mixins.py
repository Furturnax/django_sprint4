from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse

from blog.forms import CommentForm
from blog.models import Comment


class IsAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.instance.author


class PostMixin(IsAuthorMixin, LoginRequiredMixin):

    def handle_no_permission(self):
        return reverse('blog:profile',
                       kwargs={'post_id': self.instance.id})

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'username_slug': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.instance}
        return context


class CommentMixin(LoginRequiredMixin):

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.post_id})
