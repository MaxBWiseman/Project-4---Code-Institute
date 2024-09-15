from django.urls import path
from . import views
from .views import CategoryDetailView

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('create/', views.create_post, name='create_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]
