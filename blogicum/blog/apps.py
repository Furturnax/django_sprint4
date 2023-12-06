from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Конфигурация приложения Блог."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
