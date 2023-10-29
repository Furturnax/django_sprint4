from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('',
         views.PostListView.as_view(),
         name='index'),
    path('auth/registration/',
         views.RegistrationCreateView.as_view(),
         name='registration'),
    path('posts/<int:post_id>/',
         views.PostDetailListView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsListView.as_view(),
         name='category_posts'),
    path('profile/<slug:username_slug>/',
         views.GetProfileListView.as_view(),
         name='profile'),
    path('edit/<int:post_id>/',
         views.EditProfileUpdateView.as_view(),
         name='edit_profile'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:post_id>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommenDeleteView.as_view(),
         name='delete_comment'),
]
