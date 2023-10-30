from django.db.models import Count
from django.utils.timezone import now


def filter_publication(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    )


def annotation_posts_number_comments(queryset):
    return queryset.select_related(
        'author',
        'location',
        'category',
    ).order_by(
        '-pub_date'
    ).annotate(
        comment_count=Count('comments')
    )
