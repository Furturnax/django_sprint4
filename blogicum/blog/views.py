from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (CreateView, DeleteView,
                                  UpdateView)
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now

from .const import PAGINATOR_VALUE
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


def filter_posts(query_set):
    return query_set.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    ).order_by('-pub_date').select_related('author', 'location', 'category',)


@login_required
def index(request):
    post_list = filter_posts(
        Post.objects
    ).annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, PAGINATOR_VALUE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'post_list': post_list,
                                               'page_obj': page_obj})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(filter_posts(Post.objects), pk=post_id)
    return render(request, 'blog/detail.html',
                  {'post': post,
                   'form': CommentForm(),
                   'comments': Comment.objects.filter(post_id=post_id)})


@login_required
def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects,
        slug=category_slug,
        is_published=True
    )
    post_list = filter_posts(
        category.posts.all()
    ).annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, PAGINATOR_VALUE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html', {'category': category,
                                                  'page_obj': page_obj})


def profile(request, username):
    user_name = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author=user_name.id
    ).order_by('-pub_date').annotate(comment_count=Count('comments'))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html', {'profile': user_name,
                                                 'page_obj': page_obj})


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    instance = None
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['pk'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['pk'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.instance}
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.instance.post_id})


class CommenDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
