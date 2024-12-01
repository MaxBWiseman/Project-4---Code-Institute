"""
This module defines the database models for the application.

Models:
    UserGroup: Represents a user group with a name, slug, image, description,
               creation and update timestamps, admin, members, admin message.
    Category: Represents a category for posts with a unique name and slug.
    Post: Represents a post with a title, slug, blurb, banner image, content,
          status, author, category, group, and timestamps.
    Comment: Represents a comment on a post with a parent comment, image, and
             a tree structure for nested comments.
    Vote: Represents a vote on a post or comment with a user, upvote status,
          and relationships to posts and comments.
    Profile: Represents a user profile with a one-to-one relationship
            to the User model, including bio, location, image, privacy.

Signals:
    add_slug_to_group: Automatically generates a slug for a UserGroup
                    instance before saving.
    add_slug_to_category: Automatically generates a slug for a Category
                    instance before saving.
    add_slug_to_post: Automatically generates a slug for a Post
                    instance before saving.
    create_user_profile: Creates a Profile instance when a new User
                    instance is created.
    save_user_profile: Saves the Profile instance when a User
                    instance is saved.
"""
import random

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from cloudinary.models import CloudinaryField
from mptt.models import MPTTModel, TreeForeignKey


STATUS = ((0, "Blocked"), (1, "Approved"))


class UserGroup(models.Model):
    """
    Represents a user group with a name, slug, image, description,
    creation and update timestamps, admin, members, and an admin message.

    Attributes:
        name (CharField): The name of the group.
        slug (SlugField): The slug for the group, generated from the name.
        group_image (CloudinaryField): The image associated with the group.
        description (TextField): A description of the group.
        created_at (DateTimeField): Timestamp when the group was created.
        updated_at (DateTimeField): Timestamp when the group was last updated.
        admin (ForeignKey): The admin of the group, linked to the User model.
        members (ManyToManyField): Members of the group, linked to User model.
        admin_message (TextField): Message from admin to the group members.
        objects (Manager): The default manager for the model.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    group_image = CloudinaryField(
        'image', default=(
            'https://res.cloudinary.com/dbbqdfomn/image/upload/'
            'v1732040135/default.jpg')
        )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='admin_groups')
    members = models.ManyToManyField(
        User, related_name='groups_members', blank=True)
    admin_message = models.TextField(blank=True)
    objects = models.Manager()
# Group model has a many to many relationship with the User model,
# this is so groups can have multiple members, and users can be
# in multiple groups. The admin field is a foreign key to the User model,
# This is so the group has an admin.
# This relationship is one to many.

    def __str__(self):
        return str(self.name)


@receiver(pre_save, sender=UserGroup)
def add_slug_to_group(sender, instance, *_args, **_kwargs):
    """
    Automatically generates a slug for a UserGroup instance before saving.

    Args:
        sender (Model): The model class that sent the signal.
        instance (UserGroup): The actual instance being saved.
        *_args: Additional positional arguments.
        **_kwargs: Additional keyword arguments.
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)


class Category(models.Model):
    """
    Represents a category for posts with a unique name and slug.

    Attributes:
        category_name (CharField): The name of the category.
        slug (SlugField): The slug for the category, generated from the name.
        objects (Manager): The default manager for the model.
    """
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    objects = models.Manager()
# Category model is used to store the categories of the posts.
# Each Category has a unique name.
# This has a many to one relationship with the Post model.

    def __str__(self):
        return str(self.category_name)

    @staticmethod
    def get_random_categories(count=5):
        """
        Returns a list of random categories.

        Args:
            count (int): The number of random categories to return.

        Returns:
            list: A list of random categories.
        """
        categories = list(Category.objects.all())
        random.shuffle(categories)
        return categories[:count]


@receiver(pre_save, sender=Category)
def add_slug_to_category(sender, instance, *_args, **_kwargs):
    """
    Automatically generates a slug for a Category instance before saving.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Category): The actual instance being saved.
        *_args: Additional positional arguments.
        **_kwargs: Additional keyword arguments.
    """
    if not instance.slug:
        instance.slug = slugify(instance.category_name)


class Post(models.Model):
    """
    Represents a post with a title, slug, blurb, banner image, content,
    status, author, category, group, and timestamps.

    Attributes:
        title (CharField): The title of the post.
        slug (SlugField): The slug for the post, generated from the title.
        blurb (TextField): A short description or blurb for the post.
        banner_image (CloudinaryField): The banner image associated with post.
        content (TextField): The main content of the post.
        status (IntegerField): The status of the post (blocked or approved).
        author (ForeignKey): The author of the post, linked to the User model.
        category (ForeignKey): Category of post, linked to the Category model.
        group (ForeignKey): The group to which the post belongs,
                        linked to the UserGroup model.
        created_at (DateTimeField): Timestamp when the post was created.
        updated_at (DateTimeField): Timestamp when the post was last updated.
        objects (Manager): The default manager for the model.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    blurb = models.TextField(blank=True)
    banner_image = CloudinaryField(
        'image', default=(
            'https://res.cloudinary.com/dbbqdfomn/image'
            '/upload/v1732040135/default.jpg'))
    content = models.TextField()
    status = models.IntegerField(choices=STATUS, default=1)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_posts')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category')
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE,
                              related_name='group_posts',
                              null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
# Post model has a many to one relationship with the User and Category models,
# this is to store the posts of the users in the categories.
# Each Post belongs to a single User and Category.
# The group field is a foreign key to the UserGroup model,
# this is so the post can belong to a group. This relationship is many to one.

    def __str__(self):
        return f"{self.title} by {self.author}"

    # pylint: disable=no-member
    def total_upvotes(self):
        """
        Returns the total number of upvotes for the post.

        Returns:
            Integer: The total number of upvotes for the post.
        """
        return self.votes.filter(is_upvote=True).count()
    # Pylint false positive with 'self.votes',
    # this works as its a related model.

# I learned that count() is a method that returns
# the number of items in a queryset from
# https://docs.djangoproject.com/en/5.1/ref/models/querysets/#count
# "votes" is the related name of the ForeignKey in the Vote model.

    def total_downvotes(self):
        """
        Returns the total number of downvotes for the post.

        Returns:
            Integer: The total number of downvotes for the post.
        """
        return self.votes.filter(is_upvote=False).count()
    # pylint: disable=no-member
# I dont include a is_downvote field in the Vote model as I can
# determine if a vote is a downvote by checking if is_upvote is False.


@receiver(pre_save, sender=Post)
def add_slug_to_post(sender, instance, *_args, **_kwargs):
    """
    Automatically generates a slug for a Post instance before saving.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Post): The actual instance being saved.
        *_args: Additional positional arguments.
        **_kwargs: Additional keyword arguments.
    """
    if not instance.slug:
        instance.slug = slugify(instance.title)
# This automatically generates a slug for the post when it is created.
# Just before the post is saved, the title of the post is slugified and
# saved as the slug. "sender" means this should only be called for Post
# model instances. args and kwargs are used to get any additional arguments
# that may be passed. "instance" is the instance of the model that is
# being saved. I learned that that signals can be used to perform actions when
# certain events occur, for this case, I used the pre_save signal, this signal
# is sent just before the object is saved. This decorator is used to connect
# the function to the signal.
# https://stackoverflow.com/questions/8170704/execute-code-on-model-creation-in-django#:~:text=You%20can%20use%20django%20signals%20%27%20post_save%3A%20%23,MyModel%28models.Model%29%3A%20pass%20def%20my_model_post_save%28sender%2C%20instance%2C%20created%2C%20%2Aargs%2C%20%2A%2Akwargs%29%3A


class Comment(MPTTModel):
    """
    Represents a comment on a post with a parent comment, image, and
    a tree structure for nested comments.

    Attributes:
        post (ForeignKey): The post to which the comment belongs,
                        linked to the Post model.
        author (ForeignKey): The author of the comment, linked to User model.
        content (TextField): The main content of the comment.
        status (BooleanField): The status of the comment (active or inactive).
        created_at (DateTimeField): Timestamp when comment was created.
        updated_at (DateTimeField): Timestamp when comment was last updated.
        group (ForeignKey): The group to which the comment belongs,
                        linked to the UserGroup model.
        parent (TreeForeignKey): Parent comment, allowing for nested comments.
        image (CloudinaryField): The image associated with the comment.
        objects (Manager): The default manager for the model.
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
        null=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='commenter')
    content = models.TextField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE,
                              related_name='group_comments',
                              null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    image = CloudinaryField('image', blank=True, null=True)
# The parent field references the comment model iteself, the related
# name allowes to access child comments, MPTTModel is used to create a tree
# structure for the comments. This allows for easy retrieval of the comments
# and their children. Making easy nesting of comments. Here where i learnt it -
# https://blog.martinfitzpatrick.com/django-threaded-comments/
# Comment model has a many to one relationship with the Post and User models,
# this is to store the comments of the users on the posts.

    class MPTTMeta:
        """
        Meta options for the MPTTModel.

        Attributes:
            order_insertion_by (list): Specifies the field(s) by which nodes
                                    are ordered when they are inserted.
        """
        order_insertion_by = ['created_at']

    def total_upvotes(self):
        """
        Returns the total number of upvotes for the post.

        Returns:
            Integer: The total number of upvotes for the post.
        """
        return self.votes.filter(is_upvote=True).count()
    # Pylint false positive with 'self.votes',
    # this works as its a related model.

    def total_downvotes(self):
        """
        Returns the total number of downvotes for the post.

        Returns:
            Integer: The total number of downvotes for the post.
        """
        return self.votes.filter(is_upvote=False).count()

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class Vote(models.Model):
    """
    Represents a vote on a post or comment with a user and upvote status.

    Attributes:
        post (ForeignKey): The post to which the vote belongs,
                        linked to the Post model.
        comment (ForeignKey): The comment to which the vote belongs,
                        linked to the Comment model.
        user (ForeignKey): The user who cast the vote, linked to User model.
        is_upvote (BooleanField): Indicates whether the vote is an upvote
                        (True) or downvote (False).
        objects (Manager): The default manager for the model.
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='votes',
        null=True, blank=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='votes',
        null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='voter')
    is_upvote = models.BooleanField()
    objects = models.Manager()
# Vote model has a many to one relationship with the Post and User models,
# this is to store the votes of the users on the posts.

    class Meta:
        """
        Meta options for the Vote model.

        Attributes:
            unique_together (tuple): Ensures that the combination of user and
            post, or user and comment, is unique. This prevents a user from
            voting on the same post or comment more than once.
        """
        unique_together = (('user', 'post'), ('user', 'comment'))
# I learned that unique_together is a class Meta option, this is used to
# ensure that the combination of the user and post or the user and
# comment is unique. This is to help prevent a user from voting on
# a post or comment more than once.

    def __str__(self):
        return f"Vote by {self.user} on {self.post or self.comment}"


class Profile(models.Model):
    """
    Represents a user profile with a one-to-one relationship to the User model,
    including bio, location, image, and privacy settings.

    Attributes:
        user (OneToOneField): The user associated with the profile,
                        linked to the User model.
        bio (TextField): A short biography of the user.
        location (CharField): The location of the user.
        user_image (CloudinaryField): The profile image of the user.
        is_private (BooleanField): Indicates whether the profile is private.
        objects (Manager): The default manager for the model.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='user_profile')
    bio = models.TextField()
    location = models.CharField(max_length=30, blank=True)
    user_image = CloudinaryField(
        'image', default='https://res.cloudinary.com/dbbqdfomn/image/'
        'upload/v1732040135/default_profile.png')
    is_private = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.user.username

    def get_user_posts(self):
        """
        Retrieves all posts created by the user.

        Returns:
            QuerySet: A queryset containing all posts created by the user.
        """
        return self.user.user_posts.all()

    def get_user_comments(self):
        """
        Retrieves all comments made by the user.

        Returns:
            QuerySet: A queryset containing all comments made by the user.
        """
        return self.user.commenter.all()

    def get_user_groups(self):
        """
        Retrieves all groups the user is a member of.

        Returns:
            QuerySet: A queryset containing all groups the user is a member of.
        """
        return self.user.groups_members.all()

    # All these methods are pylint false positives, they work as intended.


@receiver(post_save, sender=User)
# I learned that signals can be used to perform actions when
# certain events occur, for this case, I used the post_save signal,
# this signal is sent just after the object is saved.
def create_user_profile(sender, instance, created, **_kwargs):
    """
    Creates a Profile instance when a new User instance is created.

    This signal handler is triggered by the post_save signal, which is sent
    just after a User instance is saved. If a new User instance is created,
    this function creates a corresponding Profile instance for the user.

    Args:
        sender (Model): The model class that sent the signal (User model).
        instance (User): The instance of the User model that is being saved.
        created (bool): A boolean indicating whether a new record was created.
        **_kwargs: Additional keyword arguments.
    """
    if created:
        # If a new user is created, a new profile is created for the user.
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **_kwargs):
    """
    Saves the Profile instance when a User instance is saved.

    This signal handler is triggered by the post_save signal, which is sent
    just after a User instance is saved. This function ensures that the
    corresponding Profile instance is also saved.

    Args:
        sender (Model): The model class that sent the signal (User model).
        instance (User): The instance of the User model that is being saved.
        **_kwargs: Additional keyword arguments.
    """
    instance.user_profile.save()
