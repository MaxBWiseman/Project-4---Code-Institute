# Generated by Django 4.2.16 on 2024-09-25 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post_hub', '0007_rename_group_usergroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_comments', to='post_hub.usergroup'),
        ),
    ]