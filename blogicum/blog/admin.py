from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

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

    list_display = ('is_published', 'title', 'text', 'image_tag', 'author',
                    'location', 'category', 'pub_date', 'created_at')
    list_filter = ('is_published', 'author', 'location', 'category')
    search_fields = ('title', 'text')
    ordering = ('-created_at',)
    list_display_links = ('title',)
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        """Добавляет изображение в разделе Публикации и в самом посте."""
        if obj.image:
            return mark_safe(
                f'<img src={obj.image.url} width="80" height="60">'
            )
        return 'Нет изображения'

    image_tag.short_description = 'Изображение'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройка раздела Комментарии."""

    list_display = ('text', 'author', 'created_at')
    list_filter = ('text', 'author')
    search_fields = ('text', 'author')
    ordering = ('-created_at',)
    list_display_links = ('text',)
