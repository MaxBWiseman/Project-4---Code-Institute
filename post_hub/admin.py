from django.contrib import admin
from .models import Post, Comment
from django_summernote.admin import SummernoteModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Admin class for the Post model.
    This class is used to configure the Post model in the Django admin interface.
    
    **Context**
    
    ``PostAdmin``
        An instance of :model:`blog.Post` that represents the Post model in the Django admin interface.
   
      
    """
    list_display = ('title', 'slug', 'status', 'date_posted')
    search_fields = ['title', 'content']
    list_filter = ('status','date_posted')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)


# Register your models here.
admin.site.register(Comment)
