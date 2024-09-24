from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from mptt.models import MPTTModel, TreeForeignKey


STATUS = ((0, "Blocked"), (1, "Approved"))
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
# Category model is used to store the categories of the posts.
# Each Category has a unique name.
# This has a many to one relationship with the Post model.

    def __str__(self):
        return self.category_name

@receiver(pre_save, sender=Category)
def add_slug_to_category(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.category_name)

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    blurb = models.TextField(blank=True)
    banner_image = CloudinaryField('image', default='placeholder')
    content = models.TextField()
    status = models.IntegerField(choices=STATUS, default=1)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_posts', null=True, blank=True)
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

@receiver(pre_save, sender=Post)
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

class Comment(MPTTModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commenter')
    content = models.TextField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
# The parent field references the comment model iteself, the related name allowes to access child comments
# MPTTModel is used to create a tree structure for the comments. This allows for easy retrieval of the comments
# and their children. Making easy nesting of comments. Here where i learnt it - 
# https://blog.martinfitzpatrick.com/django-threaded-comments/
# Comment model has a many to one relationship with the Post and User models,
# this is to store the comments of the users on the posts.
    
    class MPTTMeta:
        order_insertion_by = ['created_at']
        
    def total_upvotes(self):
        return self.votes.filter(is_upvote=True).count()
    
    def total_downvotes(self):
        return self.votes.filter(is_upvote=False).count()
    
    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
    
class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voter')
    is_upvote = models.BooleanField()
# Vote model has a many to one relationship with the Post and User models,
# this is to store the votes of the users on the posts.
    
    class Meta:
        unique_together = (('user', 'post'), ('user', 'comment'))
# I learned that unique_together is a class Meta option, this is used to ensure that the combination of the user and post
# or the user and comment is unique. This is to help prevent a user from voting on a post or comment more than once.
    
    def __str__(self):
        return f"Vote by {self.user} on {self.post or self.comment}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    bio = models.TextField()
    location = models.CharField(max_length=30, blank=True)
    birthdate = models.DateField(null=True, blank=True)
# Profile model has a one to one relationship with the User model,
# this is to store additional information about the user.
    
    def __str__(self):
        return self.user.username
# Profile model added as I included it in my database diagram, this is a suggestion.

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    group_image = CloudinaryField('image', default='placeholder')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups')
    members = models.ManyToManyField(User, related_name='groups', blank=True)
# Group model has a many to many relationship with the User model, this is so groups can have multiple members,
# and users can be in multiple groups.
# The admin field is a foreign key to the User model, this is so the group has an admin. this relationship is one to many.
    
    def __str__(self):
        return self.name
    
@receiver(pre_save, sender=Group)
def add_slug_to_group(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)