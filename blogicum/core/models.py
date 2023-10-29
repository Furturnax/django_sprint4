from django.db import models

from core.consts import MAX_LENGTH


class TitleModel(models.Model):
    """Модель абстрактного класса Заголовок."""

    title = models.CharField(
        'Заголовок',
        max_length=MAX_LENGTH
    )

    class Meta:
        abstract = True


class CreatedModel(models.Model):
    """Модель абстрактного класса Добавлено."""

    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        ordering = ('created_at',)


class PublishedCreatedModel(CreatedModel):
    """
    Модель абстрактного класса Опубликовано с унаследованием
    от абстрактного класса Добавлено.
    """

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)
