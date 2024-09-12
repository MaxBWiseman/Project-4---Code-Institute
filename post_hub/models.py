from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
# Category model is used to store the categories of the posts.
# Each Category has a unique name.
# This has a many to one relationship with the Post model.

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    blurb = models.CharField(max_length=255)
    content = models.TextField()
    status = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# Post model has a many to one relationship with the User and Category models,
# this is to store the posts of the users in the categories.
# Each Post belongs to a single User and Category.
    
    def __str__(self):
        return self.title
    
    def total_upvotes(self):
        return self.votes.filter(is_upvote=True).count()
# I learned that count() is a method that returns the number of items in a queryset from
# https://docs.djangoproject.com/en/5.1/ref/models/querysets/#count
    
    def total_downvotes(self):
        return self.votes.filter(is_upvote=False).count()
# I dont include a is_downvote field in the Vote model as I can determine if a vote is a downvote
# by checking if is_upvote is False.
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# Comment model has a many to one relationship with the Post and User models,
# this is to store the comments of the users on the posts.
    
    def __str__(self):
        return self.content
    
class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_upvote = models.BooleanField()
# Vote model has a many to one relationship with the Post and User models,
# this is to store the votes of the users on the posts.
    
    def __str__(self):
        return self.post.title
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    location = models.CharField(max_length=30, blank=True)
    birthdate = models.DateField(null=True, blank=True)
# Profile model has a one to one relationship with the User model,
# this is to store additional information about the user.
    
    def __str__(self):
        return self.user.username
# Profile model added as I included it in my database diagram, this is a suggestion.