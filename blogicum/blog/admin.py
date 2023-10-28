from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'

admin.site.unregister(Group)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка раздела Категории."""

    list_display = ('title', 'description', 'slug',
                    'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description', 'slug')
    ordering = ('-created_at',)
    list_display_links = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Настройка раздела Местоположения."""

    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)
    ordering = ('-created_at',)
    list_display_links = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройка раздела Публикации."""

    list_display = ('title', 'text', 'pub_date', 'author', 'location',
                    'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'author', 'location', 'category')
    search_fields = ('title', 'text')
    ordering = ('-created_at',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройка раздела Комментарии."""

    list_display = ('text', 'author', 'created_at')
    list_filter = ('text', 'author')
    search_fields = ('text', 'author')
    ordering = ('-created_at',)
    list_display_links = ('text',)
