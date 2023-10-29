from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (CreateView, DeleteView, UpdateView)
from django.views.generic.edit import CreateView
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now

from core.consts import PAGINATOR_VALUE
from core.mixins import CommentMixin
from .forms import CommentForm, PostForm, ProfileForm
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


def index(request):
    """Рендерит страницу index.html."""
    post_list = filter_posts(
        Post.objects
    ).annotate(comment_count=Count('comments'))
    return render(request, 'blog/index.html', {
        'post_list': post_list,
        'page_obj': get_paginator(request, post_list, PAGINATOR_VALUE),
    })


def post_detail(request, post_id: int):
    """Рендерит страницу detail.html."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        post = get_object_or_404(filter_posts(Post.objects), id=post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post_id=post_id)
    })


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


def get_profile(request, username_slug: str):
    """Рендерит страницу profile.html."""
    user_name = get_object_or_404(User, username=username_slug)
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
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV - создает публикацию."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username_slug': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """CBV - редактирует публикацию."""

    instance = None
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, id=kwargs['post_id'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """CBV - удаляет публикацию."""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, id=kwargs['post_id'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.instance}
        return context


class CommentCreateView(CommentMixin, CreateView):
    """CBV - создаёт комментарий."""

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.id})


class CommentUpdateView(CommentMixin, UpdateView):
    """CBV - редактирует комментарий."""

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Comment, id=kwargs['comment_id'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommenDeleteView(CommentMixin, DeleteView):
    """CBV - удаляет комментарий."""

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Comment, id=kwargs['comment_id'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
