# Generated by Django 4.2.16 on 2024-09-26 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_hub', '0009_alter_comment_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='admin_message',
            field=models.TextField(blank=True),
        ),
    ]
