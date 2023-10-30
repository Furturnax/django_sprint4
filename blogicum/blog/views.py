from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView)
from django.views.generic.edit import CreateView
from django.urls import reverse, reverse_lazy

from core.consts import PAGINATOR_VALUE
from core.mixins import CommentMixin, IsAuthorMixin, PostMixin
from core.utils import filter_posts, comments_count
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


class RegistrationCreateView(CreateView):
    """CBV - Регистрирует пользователя."""

    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


class PostListView(ListView):

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR_VALUE

    def get_queryset(self):
        return comments_count(filter_posts(super().get_queryset()))


class PostDetailListView(ListView):

    model = Comment
    template_name = 'blog/detail.html'
    paginate_by = PAGINATOR_VALUE

    def get_post(self, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != self.request.user and not post.is_published:
            raise PermissionDenied()
        return post

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = self.get_post(post_id)
        return Comment.objects.filter(post=post)

    def get_context_data(self, **kwargs):
        post_id = self.kwargs['post_id']
        context = {
            'post': self.get_post(post_id),
            'form': CommentForm()
        }
        context.update(super().get_context_data(**kwargs))
        return context


class CategoryPostsListView(ListView):

    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATOR_VALUE

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return comments_count(filter_posts(self.get_category().posts.all()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class GetProfileListView(ListView):

    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATOR_VALUE

    def get_author(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username_slug'])

    def get_queryset(self):
        user = self.get_author()
        queryset = comments_count(Post.objects.filter(author=user))
        if user != self.request.user:
            queryset = filter_posts(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV - редактирует профиль."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV - создает публикацию."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username_slug': self.request.user.username})


class PostUpdateView(PostMixin, UpdateView):
    """CBV - редактирует публикацию."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['post_id']}))
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(PostMixin, DeleteView):
    """CBV - удаляет публикацию."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:profile')

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'pk': self.kwargs['post_id']}))
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'username': self.request.user.username})


class CommentCreateView(CommentMixin, CreateView):
    """CBV - создаёт комментарий."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, IsAuthorMixin, UpdateView):
    """CBV - редактирует комментарий."""

    pass


class CommenDeleteView(CommentMixin, IsAuthorMixin, DeleteView):
    """CBV - удаляет комментарий."""

    pass
