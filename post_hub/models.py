from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
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
        return f"{self.title} by {self.author.username}"

    
    def total_upvotes(self):
        return self.votes.filter(is_upvote=True).count()
# I learned that count() is a method that returns the number of items in a queryset from
# https://docs.djangoproject.com/en/5.1/ref/models/querysets/#count
# "votes" is the related name of the ForeignKey in the Vote model.
    
    def total_downvotes(self):
        return self.votes.filter(is_upvote=False).count()
# I dont include a is_downvote field in the Vote model as I can determine if a vote is a downvote
# by checking if is_upvote is False.

@reciever(pre_save, sender=Post)
def add_slug_to_post(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
# This automatically generates a slug for the post when it is created. Just before
# the post is saved, the title of the post is slugified and saved as the slug.
# "sender" means this should only be called for Post model instances.
# args and kwargs are used to get any additional arguments that may be passed.
# "instance" is the instance of the model that is being saved.
# I learned that that signals can be used to perform actions when certain events occur,
# for this case, I used the pre_save signal, this signal is sent just before the object is saved.
# This decorator is used to connect the function to the signal.
# https://stackoverflow.com/questions/8170704/execute-code-on-model-creation-in-django#:~:text=You%20can%20use%20django%20signals%20%27%20post_save%3A%20%23,MyModel%28models.Model%29%3A%20pass%20def%20my_model_post_save%28sender%2C%20instance%2C%20created%2C%20%2Aargs%2C%20%2A%2Akwargs%29%3A

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