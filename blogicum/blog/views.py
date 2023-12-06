from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.edit import CreateView

from core.consts import PAGINATOR_VALUE
from core.mixins import CommentMixin, IsAuthorMixin, PostMixin
from core.services import annotation_posts_number_comments, filter_publication
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


class RegistrationCreateView(CreateView):
    """CBV - Регистрирует пользователя."""

    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


class PostListView(ListView):
    """CBV - Рендер главной стрницы."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATOR_VALUE

    def get_queryset(self):
        return annotation_posts_number_comments(
            filter_publication(super().get_queryset())
        )


class PostDetailListView(ListView):
    """CBV - Рендер старницы отдельный постов."""

    model = Comment
    template_name = 'blog/detail.html'
    paginate_by = PAGINATOR_VALUE
    pk_url_kwarg = 'post_id'

    def get_post(self):
        post = get_object_or_404(Post, id=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user and not post.is_published:
            raise Http404('Публикация не найдена')
        return post

    def get_queryset(self):
        return self.get_post().comments.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_post()
        context['form'] = CommentForm()
        return context


class CategoryPostsListView(ListView):
    """CBV - Рендер категорий."""

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
        return annotation_posts_number_comments(
            filter_publication(self.get_category().posts.all())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class GetProfileListView(ListView):
    """CBV - Рендер страницы пользователей."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATOR_VALUE

    def get_author(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username_slug'])

    def get_queryset(self):
        user = self.get_author()
        queryset = annotation_posts_number_comments(
            user.posts.filter()
        )
        if user != self.request.user:
            queryset = filter_publication(queryset)
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

    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username_slug': self.request.user.username})


class PostUpdateView(PostMixin, UpdateView):
    """CBV - редактирует публикацию."""

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(PostMixin, DeleteView):
    """CBV - удаляет публикацию."""

    pass


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
