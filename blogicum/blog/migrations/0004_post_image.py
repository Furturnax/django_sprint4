# Generated by Django 3.2.16 on 2023-10-27 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20231026_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='posts_images', verbose_name='Фото'),
        ),
    ]
