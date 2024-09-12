# Generated by Django 4.2.16 on 2024-09-12 17:15

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_hub', '0002_rename_name_category_category_name_alter_post_blurb'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='banner_image',
            field=cloudinary.models.CloudinaryField(default='placeholder', max_length=255, verbose_name='image'),
        ),
    ]
