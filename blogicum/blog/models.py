from django.contrib.auth.models import User
from django.db import models

from core.consts import MAX_LENGTH, SLICE
from core.models import CreatedModel, PublishedCreatedModel, TitleModel


class Category(TitleModel, PublishedCreatedModel):
    """Модель таблицы Категория."""

    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta(PublishedCreatedModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:SLICE]


class Location(PublishedCreatedModel):
    """Модель таблицы Локация."""

    name = models.CharField(
        'Название места',
        max_length=MAX_LENGTH,
    )

    class Meta(PublishedCreatedModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:SLICE]


class Post(TitleModel, PublishedCreatedModel):
    """Модель таблицы Публикация."""

    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно '
        'делать отложенные публикации.',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:SLICE]


class Comment(CreatedModel):
    """Модель таблицы Комментарий."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарий',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:SLICE]
