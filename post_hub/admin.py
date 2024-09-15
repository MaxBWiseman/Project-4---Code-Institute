from django.contrib import admin
from .models import Post, Comment, Category
from django_summernote.admin import SummernoteModelAdmin
from mptt.admin import MPTTModelAdmin


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Admin class for the Post model.
    This class is used to configure the Post model in the Django admin interface.
    
    **Context**
    
    ``PostAdmin``
        An instance of :model:`blog.Post` that represents the Post model in the Django admin interface.
   
      
    """
    list_display = ('title', 'slug', 'status', 'created_at')
    search_fields = ['title', 'content', 'category_name']
    list_filter = ('status','created_at')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)


# Register your models here.
admin.site.register(Comment, MPTTModelAdmin)

admin.site.register(Category)
