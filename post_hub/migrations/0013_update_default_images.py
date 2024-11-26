# Generated by Django 4.2.16 on 2024-11-19 18:50

from django.db import migrations

def update_default_images(apps, schema_editor):
    UserGroup = apps.get_model('post_hub', 'UserGroup')
    Post = apps.get_model('post_hub', 'Post')

    old_default_image = 'https://res.cloudinary.com/dbbqdfomn/image/upload/placeholder'
    new_default_image = 'https://res.cloudinary.com/dbbqdfomn/image/upload/v1732040135/default.jpg'

    # Update UserGroup records
    UserGroup.objects.filter(group_image=old_default_image).update(group_image=new_default_image)

    # Update Post records
    Post.objects.filter(banner_image=old_default_image).update(banner_image=new_default_image)

class Migration(migrations.Migration):

    dependencies = [
        ('post_hub', '0012_alter_post_banner_image_alter_usergroup_group_image'),
    ]

    operations = [
        migrations.RunPython(update_default_images),
    ]