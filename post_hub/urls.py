from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<str:name>/', views.category_detail, name='category_detail'),
]
