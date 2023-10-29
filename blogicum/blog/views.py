from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import (CreateView, DeleteView, UpdateView)
from django.views.generic.edit import CreateView
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now

from .const import PAGINATOR_VALUE
from .forms import CommentForm, PostForm, ProfileForm
from .mixins import (
    CommentdispatchMixin, CommentMixin, PostdispatchMixin, PostMixin
)
from .models import Category, Comment, Post


class RegistrationCreateView(CreateView):
    """CBV - Регистрирует пользователя."""

    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


def filter_posts(query_set):
    """Вернёт отфильтрованный query_set."""
    return query_set.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    ).order_by('-pub_date').select_related('author', 'location', 'category',)


def get_paginator(request, list, value: int):
    """Создаст пагинатор с количеством элементов на странице value."""
    page_number = request.GET.get('page')
    return Paginator(list, value).get_page(page_number)


@login_required
def index(request):
    """Рендерит страницу index.html."""
    post_list = filter_posts(
        Post.objects
    ).annotate(comment_count=Count('comments'))
    return render(request, 'blog/index.html', {
        'post_list': post_list,
        'page_obj': get_paginator(request, post_list, PAGINATOR_VALUE),
    })


@login_required
def post_detail(request, post_id: int):
    """Рендерит страницу detail.html."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(filter_posts(Post.objects), pk=post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post_id=post_id)
    })


@login_required
def category_posts(request, category_slug: str):
    """Рендерит страницу category.html."""
    category = get_object_or_404(
        Category.objects,
        slug=category_slug,
        is_published=True
    )
    post_list = filter_posts(
        category.posts.all()
    ).annotate(comment_count=Count('comments'))
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': get_paginator(request, post_list, PAGINATOR_VALUE),
    })


def get_profile(request, username: str):
    """Рендерит страницу profile.html."""
    user_name = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author=user_name.id
    ).order_by('-pub_date').annotate(comment_count=Count('comments'))
    return render(request, 'blog/profile.html', {
        'profile': user_name,
        'page_obj': get_paginator(request, post_list, PAGINATOR_VALUE),
    })


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV - редактирует профиль."""

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """CBV - создает публикацию."""

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, PostMixin,
                     PostdispatchMixin, UpdateView):
    """CBV - редактирует публикацию."""

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.pk})


class PostDeleteView(LoginRequiredMixin, PostMixin,
                     PostdispatchMixin, DeleteView):
    """CBV - удаляет публикацию."""

    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.instance}
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """CBV - создаёт комментарий."""

    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.instance
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentMixin,
                        CommentdispatchMixin, UpdateView):
    """CBV - редактирует комментарий."""

    form_class = CommentForm


class CommenDeleteView(LoginRequiredMixin, CommentMixin,
                       CommentdispatchMixin, DeleteView):
    """CBV - удаляет комментарий."""

    template_name = 'blog/comment.html'
