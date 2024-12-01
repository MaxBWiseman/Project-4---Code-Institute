"""
This module configures the Django admin interface for the application's models.

Admin Classes:
    PostAdmin: Custom admin class for the Post model,
    using Summernote for rich text editing.

Registered Models:
    Comment: Registered with MPTTModelAdmin to support tree
            structure for nested comments.
    Category: Registered with the default admin interface.
    UserGroup: Registered with the default admin interface.
"""
from django.contrib import admin

from django_summernote.admin import SummernoteModelAdmin
from mptt.admin import MPTTModelAdmin

from .models import Category, Comment, Post, UserGroup


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Admin class for the Post model.
    This class is used to configure the Post model
    in the Django admin interface.

    **Context**

    ``PostAdmin``
        An instance of :model:`blog.Post` that represents the
        Post model in the Django admin interface.


    """
    list_display = ('title', 'slug', 'status', 'created_at')
    search_fields = ['title', 'content', 'category_name']
    list_filter = ('status', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)


# Register your models here.
admin.site.register(Comment, MPTTModelAdmin)

admin.site.register(Category)

admin.site.register(UserGroup)
