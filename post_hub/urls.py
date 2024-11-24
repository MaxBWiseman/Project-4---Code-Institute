from django.urls import path
from . import views
from .views import CategoryDetailView, edit_comment, DeleteComment, DeletePost

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', DeletePost.as_view(), name='delete_post'),
    path('edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', DeleteComment.as_view(), name='comment_delete'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('usergroup/create/', views.create_group, name='create_group'),
    path('usergroup/<slug:slug>/', views.group_detail, name='group_detail'),
    path('usergroup/<slug:slug>/join/', views.join_group, name='join_group'),
    path('usergroup/<slug:slug>/remove_member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('usergroups/', views.group_index, name='group_index'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('vote/', views.vote, name='vote'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
]
