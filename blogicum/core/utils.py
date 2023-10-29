from django.db.models import Count
from django.utils.timezone import now


def filter_posts(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    ).select_related(
        'author',
        'location',
        'category',
    )


def comments_count(queryset):
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
