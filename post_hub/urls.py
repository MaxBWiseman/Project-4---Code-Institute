from django.urls import path
from . import views
from .views import CategoryDetailView, edit_comment, DeleteComment

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', DeleteComment.as_view(), name='comment_delete'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('vote/', views.vote, name='vote'),
]
