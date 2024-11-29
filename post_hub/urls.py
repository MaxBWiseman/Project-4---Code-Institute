
"""
URL configuration for the post_hub application.

This module defines the URL patterns for the post_hub application. Each URL
pattern is associated with a view function or class-based view that handles
the request and returns a response. The URL patterns include paths for
creating, editing, and deleting posts and comments, viewing profiles,
managing user groups, and other functionalities.

URL Patterns:
- '' (home): Displays the list of posts.
- 'create/' (create_post): Handles the creation of a new post.
- 'post/<slug:slug>/edit/' (edit_post): Handles editing of an existing post.
- 'post/<int:pk>/delete/' (delete_post): Handles the deletion of a post.
- 'edit_comment/<int:comment_id>/' (edit_comment): Editing of a comment.
- 'comment/<int:pk>/delete/' (comment_delete): Handles deletion of a comment.
- 'post/<slug:slug>/' (post_detail): Displays the details of a specific post.
- 'usergroup/create/' (create_group): Handles the creation of a new user group.
- 'usergroup/<slug:slug>/' (group_detail): Displays details of a user group.
- 'usergroup/<slug:slug>/join/' (join_group): Joining of a user to a group.
- 'usergroup/<slug:slug>/remove_member/<int:user_id>/' (remove_member):
                                Handles the removal of a member from a group.
- 'usergroups/' (group_index): Displays list of groups and their latest posts.
- 'categories/' (category_list): Displays a list of categories.
- 'category/<slug:slug>/' (category_detail): Displays details of a category.
- 'vote/' (vote): Handles voting on posts and comments.
- 'profile/edit/' (edit_profile): Handles the editing of a user's profile.
- 'profile/<str:username>/' (view_profile): Displays the profile of a user.
- 'terms-conditions/' (terms_conditions): Display terms and conditions page.
- 'contact/' (contact): Displays the contact page.
- 'send_email/' (send_email): Sending of an email from the contact form.
"""
from django.urls import path
from . import views
from .views import CategoryDetailView, edit_comment, DeleteComment, DeletePost

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', DeletePost.as_view(), name='delete_post'),
    path('edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/',
         DeleteComment.as_view(), name='comment_delete'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('usergroup/create/', views.create_group, name='create_group'),
    path('usergroup/<slug:slug>/', views.group_detail, name='group_detail'),
    path('usergroup/<slug:slug>/join/', views.join_group, name='join_group'),
    path('usergroup/<slug:slug>/remove_member/<int:user_id>/',
         views.remove_member, name='remove_member'),
    path('usergroups/', views.group_index, name='group_index'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/',
         CategoryDetailView.as_view(), name='category_detail'),
    path('vote/', views.vote, name='vote'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('security/', views.security, name='security'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('contact/', views.contact, name='contact'),
    path('send_email/', views.send_email, name='send_email'),
]
