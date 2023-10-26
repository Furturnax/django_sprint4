from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.urls import reverse
from django.utils.timezone import now

from blog.forms import PostForm
from blog.models import Category, Post
from blog.const import INDEX_LIMIT


def filter_posts(query_set):
    return query_set.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    ).select_related('author', 'location', 'category',)


def index(request):
    post_list = filter_posts(Post.objects)[:INDEX_LIMIT]
    return render(request, 'blog/index.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(filter_posts(Post.objects), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects,
        slug=category_slug,
        is_published=True
    )
    post_list = filter_posts(category.posts.all())
    return render(request, 'blog/category.html', {'category': category,
                                                  'post_list': post_list})


def profile(request, username):
    user_name = get_object_or_404(User, username=username)
    return render(request, 'blog/profile.html', {'profile': user_name})


class PostCreateView(LoginRequiredMixin, CreateView):

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=(self.request.user.get_username()))
