"""
This module contains the views for the post_hub app.
"""
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.conf import settings
from django.views import generic
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.urls import reverse, reverse_lazy

import cloudinary

from .models import Post, Comment, Category, Vote, UserGroup, User, Profile
from .forms import (
    CommentForm, PostForm, GroupForm,
    GroupAdminForm, ProfileForm
)


class PostList(generic.ListView):
    """
    A view that displays a list of approved posts, ordered by creation date.

    This view inherits from Django's generic ListView and is used to display
    a paginated list of posts that have been approved (status=1). The posts
    are ordered by their creation date in descending order.

    Attributes:
        queryset (QuerySet): The queryset to retrieve approved posts
                            ordered by creation date.
        template_name (str): The template to render the list of posts.
        paginate_by (int): The number of posts to display per page.

    Methods:
        get_context_data(**kwargs):
            Adds additional context data to the template,
            including top categories, top user groups,
            and suggested categories.
    """
    queryset = Post.objects.filter(status=1).order_by("-created_at")
    # This line of code tells Django to retrieve all posts with a status of 1
    # (approved) and order them by the created_on field in descending order.
    template_name = "post_hub/index.html"
    paginate_by = 8

    # django automatically sets the context_object_name attribute
    # to object_list. e.g "post_list" is the context_object_name,
    # this becomes our iterator in the templates to show all
    # published posts in order of date posted.

    def get_context_data(self, **kwargs):
        """
        Adds additional context data to the template.

        This method overrides the default get_context_data method to add
        top categories, top user groups, and suggested categories
        to the context.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data with additional information.
        """
        context = super().get_context_data(**kwargs)
        context['top_categories'] = Category.objects.annotate(
            post_count=Count('category_name')).order_by('post_count')
        context['top_groups'] = UserGroup.objects.annotate(
            num_members=Count('members')).order_by('num_members')[:8]
# The top 8 groups are retrieved and added to the context. The annotate method
# is used to add a num_members field to each UserGroup object
# which contains the count of members inside the group. Count is a django
# aggregation function often used in conjunction with annotate.
# Learned from =
# https://stackoverflow.com/questions/3606416/django-most-efficient-way-to-count-same-field-values-in-a-query#:~:text=You%20can%20use%20Django%27s%20Count%20aggregation%20on%20a,in%20queryset%3A%20print%20%22%25s%3A%20%25s%22%20%25%20%28each.my_charfield%2C%20each.count%29

        context['suggested_categories'] = Category.get_random_categories()
        return context
# By overriding the get_context_data method, you can add the categories
# to the context in a more standard and efficient way.
# This approach ensures that the categories are available in the template
# without creating a separate method for retrieving category data.


@login_required
def vote(request):
    """
    Handle voting on posts and comments.

    This view function interacts with the Vote model to
    create, update, or delete vote records in the database
    based on the data received from AJAX requests. It supports
    voting on both posts and comments.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the vote data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of
                    the vote operation.

    Raises:
        ObjectDoesNotExist: If the post or comment does not exist.
        IntegrityError: If there is a database integrity error.
        ValueError: If an invalid value is provided.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        # The data from the request is loaded into a JSON object.
        post_id = data.get('post_id')
        comment_id = data.get('comment_id')
        is_upvote = data.get('is_upvote')
        user = request.user
# post_id, comment_id, and is_upvote are retrieved from the JSON object.
# comment_id is retrieved using the get method to handle when the request
# isnt for a comment. Updated all to .get to avoid keyError
        if is_upvote is None:
            messages.error(request, 'A vote choice is required')
            return JsonResponse({'success': False})
# If is_upvote is not provided, a JSON response is returned to
# indicate that the request has failed.
        try:
            with transaction.atomic():
                # The transaction.atomic() method is used to ensure
                # that either all of the code in this view succeeds or none of
                # it does. This ensures that all operations are either
                # committed or rolled back together. If an error occurs
                # during the view function, the transaction is rolled
                # back and the database is restored to its previous state.
                # This ensures data integrity.
                if post_id:
                    # If post_id exists, the vote is for a post.
                    post = get_object_or_404(Post, id=post_id)
# The post object to associate with is retrieved from the
# database using the post_id.
                    user_vote, created = Vote.objects.get_or_create(
                        user=user, post=post, defaults={
                            'is_upvote': is_upvote})
# The vote object is retrieved from the database using the post_id.
# The get_or_create method is used to retrieve the vote object for the user
# because there should only be one vote per user.
                elif comment_id:
                    # If comment_id exists, the vote is for a comment.
                    comment = get_object_or_404(Comment, id=comment_id)
                    user_vote, created = Vote.objects.get_or_create(
                        user=user, comment=comment, defaults={
                            'is_upvote': is_upvote})
# The vote object is retrieved from the database using the comment_id.
                else:
                    return JsonResponse(
                        {'success': False, 'error': 'Invalid request'})
# If neither post_id nor comment_id exists, a JSON response is returned
# to indicate that the request has failed.

                if not created:
                    # The vote we grabbed above
                    if user_vote.is_upvote == is_upvote:
                        user_vote.delete()
# If the vote exists and the is_upvote field is the same as the request,
# the vote is deleted.
                    else:
                        user_vote.is_upvote = is_upvote
                        user_vote.save()
# If the vote exists and the is_upvote field is different from the request,
# the is_upvote field is updated. This is for if the user wants
# to change their vote.
                messages.success(request, 'Your vote has been recorded.')
                return JsonResponse({'success': True})
            # A JSON response is returned to indicate that
            # the vote was successful.
        except ObjectDoesNotExist:
            messages.error(request, 'The object does not exist.')
            return JsonResponse({'success': False})
        except IntegrityError:
            messages.error(request, 'Database integrity error.')
            return JsonResponse({'success': False})
        except ValueError:
            messages.error(request, 'Invalid value provided.')
            return JsonResponse({'success': False})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
    # If the request method is not POST, a JSON response is returned
    # to indicate that the request is invalid.


def post_detail(request, slug):
    """
    Display the details of a specific post, including its comments.

    This view function retrieves a post based on its slug and
    displays its details, including paginated comments. It also handles
    the submission of new comments.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the post to be retrieved.

    Returns:
        HttpResponse: The rendered template displaying the post
                    details and comments.

    Raises:
        Http404: If the post with the given slug does not exist.
    """
    post = get_object_or_404(Post, slug=slug, status=True)
# Grab all comments related to the post with status approved

    allcomments = post.comments.filter(status=True)
# The comments are filtered to only include approved comments.
# "comments" is the related name of the ForeignKey in the Comment model.
    page = request.GET.get('page', 1)
# This line of code retrieves the page number from the GET request.
# Djangos pagination system includes the page paramenter in the URL,
# so the page number can be retrieved
    paginator = Paginator(allcomments, 10)
# The comments are paginated with 10 comments per page.
# Using the Paginator class from Django.
    try:
        comments = paginator.page(page)
# The page method is called on the paginator object to retrieve the
# comments for the requested page.
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
# The PageNotAnInteger and EmptyPage exceptions are handled to ensure
# that the page number is valid.
    user_comment = None
# this is to store the comment that the user is going to post

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to post a comment.')
            return redirect('account_login')
        comment_form = CommentForm(request.POST, request.FILES)
# The data from the form is retrieved and stored in the comment_form variable.
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False, author=request.user)
# The comment is saved to the database but not committed.
# so we may manipulate the comment before saving it to the database
            user_comment.post = post
# This is to associate the comment with the post.
            user_comment.save()
            messages.success(
                request, 'Your comment has been posted successfully!')
            return HttpResponseRedirect(
                reverse('post_detail', args=[post.slug]))
        else:
            print(comment_form.errors)
            messages.error(
                request, 'There was an error posting your comment.'
                ' Please try again.')
            return HttpResponseRedirect(
                reverse('post_detail', args=[post.slug]))
# We use args to pass the slug of the post to the URL pattern.
# To redirect to the correct post detail page.
    else:
        comment_form = CommentForm()
# If there is no POST request, an empty comment form is created.
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'allcomments': allcomments,
        'total_upvotes': post.total_upvotes(),
        'total_downvotes': post.total_downvotes(),
        'comment_votes': {comment.id: {'upvotes': comment.total_upvotes(),
                                       'downvotes': comment.total_downvotes()}
                          for comment in allcomments}
    }
    return render(request, 'post_hub/post_detail.html', context)
# total_upvotes and total_downvotes are added to the context to display
# the total number of upvotes and downvotes for the post.
# comment_votes is added to the context to display the total number of upvotes
# and downvotes for each comment using a dictionary comprehension.

# Exempt view from cross sit request forgery protection


def edit_comment(request, comment_id):
    """
    Edit an existing comment.

    This view function allows a user to edit their own comment. It updates the
    content and optionally the image of the comment based on the data received
    from the request. The function handles both adding a new image and removing
    an existing image.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the comment data.
        comment_id (int): The ID of the comment to be edited.

    Returns:
        JsonResponse: A JSON response indicating the success or failure
                    of the edit operation.

    Raises:
        ObjectDoesNotExist: If the comment does not exist or the user is
                        not authorized to edit it.
    """
    if request.method == 'POST':
        try:
            comment = Comment.objects.get(id=comment_id, author=request.user)
# The comment the user is trying to edit is retrieved from the database.
            comment.content = request.POST.get('content', comment.content)
# Comment content is updated with the new content from the request.

            if 'image' in request.FILES:
                # If an image is in the request
                image = request.FILES['image']
                # image is retrieved from the request and stored in a variable.
                upload_result = cloudinary.uploader.upload(
                    # Use cloudinary api to upload the image
                    image,
                    resource_type='image',
                    folder='comments/',
                )
                comment.image = upload_result['url']
                # Take the url of the upload_result and store
                # it in the comment object.
            elif (
                'remove_image' in request.POST and
                request.POST['remove_image'] == 'true'
            ):
                comment.image = None
                # If the user wants to remove the image,
                # the image field is set to None.

            comment.save()
            return JsonResponse({'success': True, 'image': comment.image})
# A JSON response is returned to indicate that
# the comment was updated successfully.
        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'error': (
                'Comment not found or not authorized')})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
# If the request method is not POST, a JSON response is returned to indicate
# that the request is invalid. I chose to use JSON responses for this view
# because it is an AJAX request and JSON is a common format for AJAX responses.


class DeletePost(DeleteView):
    """
    View to handle the deletion of a post.

    This view allows users to delete their own posts.
    Superusers can delete any post. Upon successful deletion,
    a JSON response indicating success is returned.

    Attributes:
        model (Model): The model to be deleted (Post).
        success_url (str): The URL to redirect to upon successful deletion.

    Methods:
        get_queryset():
            Returns the queryset of posts that the user is allowed to delete.
            Superusers can delete any post, while regular users can
            only delete their own posts.

        __init__(*args, **kwargs):
            Initializes the DeletePost view.

        delete(request, *args, **kwargs):
            Deletes the specified post and returns a JSON response
            indicating success.
    """
    model = Post
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """
        Returns the queryset of posts that the user is allowed to delete.

        Superusers can delete any post, while regular users can only delete
        their own posts.

        Returns:
            QuerySet: The queryset of posts the user is allowed to delete.
        """
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(auther=self.request.user)

    def __init__(self, *args, **kwargs):
        """
        Initializes the DeletePost view.
        """
        super().__init__(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Deletes the specified post and returns a JSON response
        indicating success.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            JsonResponse: A JSON response indicating the success
            of the deletion.
        """
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'success': True})


class DeleteComment(DeleteView):
    """
    View to handle the deletion of a comment.

    This view allows users to delete their own comments. Superusers
    can delete any comment. Upon successful deletion, a JSON response
    indicating success is returned.

    Attributes:
        model (Model): The model to be deleted (Comment).
        success_url (str): The URL to redirect to upon successful deletion.

    Methods:
        get_queryset():
            Returns the queryset of comments that the user is
            allowed to delete. Superusers can delete any comment,
            while regular users can only delete their own comments.

        __init__(*args, **kwargs):
            Initializes the DeleteComment view.

        delete(request, *args, **kwargs):
            Deletes the specified comment and returns a JSON
            response indicating success.
    """
    model = Comment
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """
        Returns the queryset of comments that the user is allowed to delete.

        Superusers can delete any comment, while regular users can only delete
        their own comments.

        Returns:
            QuerySet: The queryset of comments the user is allowed to delete.
        """
        queryset = super().get_queryset()
# This line of code calls the get_queryset method of
# the parent class to retrieve the queryset.
# The queryset is used to filter the comments to only
# include comments by the current user.
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(author=self.request.user)
# The author field of the comment is compared to the
# current user to filter the comments.
# The current user is retrieved from the request object
# and compared to the author field of the comment.
# This ensures that only the comments by the current user can be deleted.

    def __init__(self, *args, **kwargs):
        """
        Initializes the DeleteComment view.
        """
        super().__init__(*args, **kwargs)
        self.object = None

    def delete(self, request, *args, **kwargs):
        """
        Deletes the specified comment and returns a JSON response
        indicating success.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            JsonResponse: A JSON response indicating the success
            of the deletion.
        """
        self.object = self.get_object()
# The get_object method is called to retrieve the comment to
# be deleted when the view is called.
        self.object.delete()
# The delete method is called on the comment object to delete
# the comment from the database.
        return JsonResponse({'success': True})


@login_required
def create_post(request):
    """
    Handle the creation of a new post.

    This view function allows authenticated users to create a new post.
    It handles both the form submission and image uploads. If a new
    category is specified and does not already exist, it is created.

    Args:
        request (HttpRequest): The HTTP request object containing
        the post data.

    Returns:
        HttpResponse: The rendered template for creating a post or a redirect
                    to the post detail page upon successful creation.

    Raises:
        ValidationError: If the form data is invalid.
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        # The data from the form is retrieved and stored in the form variable.
        # The request.FILES attribute is used to handle image uploads.

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            new_category_name = form.cleaned_data.get('new_category')
# The new_category field is retrieved from the
# cleaned_data attribute of the form.
# The new_category field is used to create a new category if
# it does not already exist. cleaned_data attribute is used to
# retrieve the form data after it has been cleaned and validated.
# Django forms automatically clean and validate the data
# when the is_valid method is called.
            if new_category_name:
                category, created = Category.objects.get_or_create(
                    category_name=new_category_name)
# This line of code retrieves the category object from the database or
# creates a new category if it does not already exist.
                post.category = category
                if created:
                    messages.success(request, f"A new category '{
                                     new_category_name}' was created.")
            post.group = form.cleaned_data.get('group')
            post.save()
            messages.success(
                request, 'Your post has been tooted out successfully!')
            return redirect('post_detail', slug=post.slug)
            # The user is redirected to the post detail
            # page for the newly created post.
        else:
            messages.error(
                request, 'There was an error creating your post.'
                ' Please try again.')
            # If the form is not valid, an error message
            # is displayed to the user.
            return redirect('create_post')
    else:
        form = PostForm()
        # If there is no POST request, an empty form is created.
    return render(request, 'post_hub/create_post.html', {'form': form})


def category_list(request):
    """
    Display a list of categories, including top categories, top user groups,
    and suggested categories.

    This view function retrieves and displays a list of categories. If a
    search query is provided via the GET request, it filters the categories
    based on the query. It also retrieves the top categories, top user groups,
    and suggested categories to be displayed in the context.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the search query.

    Returns:
        HttpResponse: The rendered template displaying the list of categories
                    and additional context data.
    """
    query = request.GET.get('q')
    if query:
        categories = Category.objects.filter(category_name__icontains=query)
    else:
        categories = Category.objects.all()

    top_categories = Category.objects.annotate(
        post_count=Count('category_name')).order_by('post_count')
    top_groups = UserGroup.objects.annotate(
        num_members=Count('members')).order_by('num_members')[:8]
    suggested_categories = Category.get_random_categories()

    context = {
        'categories': categories,
        'top_categories': top_categories,
        'top_groups': top_groups,
        'suggested_categories': suggested_categories,
    }
    return render(request, 'post_hub/category_list.html', context)


def edit_post(request, slug):
    """
    Handle the editing of an existing post.

    This view function allows the author of a post to edit their post.
    It retrieves the post based on the provided slug and checks if
    the current user is the author. If the user is not the author,
    they are redirected to the post detail page. If the user is the
    author, the function handles the form submission to update the post.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the post data.
        slug (str): The slug of the post to be edited.

    Returns:
        HttpResponse: The rendered template for editing the post or a
                    redirect to the post detail page upon successful update.
    """
    post = get_object_or_404(Post, slug=slug)
# I used the get_object_or_404 function to retrieve the
# post object from the database or 404 if not.
    if request.user != post.author:
        return redirect('post_detail', slug=slug)
# If user is not the author of the post,
# they are redirected to the post detail page.

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
# The data from the form is retrieved and stored in the form variable.
# request.FILES attribute is used to handle image uploads.
# instance=post is used to update the existing post object
# because the user is editing an existing post.
        if form.is_valid():
            form.save()
# The form is saved to update the post object in the database.
            messages.success(
                request, 'Your post has been updated successfully!')
            return redirect('post_detail', slug=slug)
        else:
            messages.error(
                request, 'There was an error updating your post.'
                ' Please try again.')
    else:
        form = PostForm(instance=post)
# If no POST request is made, the form is
# created with the existing post object.

    return render(request, 'post_hub/edit_post.html', {
        'form': form, 'post': post})
# We need to pass the post object to the template so that the user can
# see the current posts content and make their edits.


@login_required
def create_group(request):
    """
    Handle the creation of a new user group.

    This view function allows authenticated users to create a new group.
    It handles both the form submission and image uploads. Users are
    limited to creating a maximum of 2 groups. If the form is valid,
    the group is created, and the user is added as a member and
    admin of the group.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the group data.

    Returns:
        HttpResponse: The rendered template for creating a group or a
                    redirect to the group detail page upon successful creation.
    """
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            user_group_count = UserGroup.objects.filter(
                admin=request.user).count()
            if user_group_count >= 2:
                messages.error(request, 'You can only create up to 2 groups.')
# Limit users to 2 groups each
            else:
                group = form.save(commit=False)
                group.admin = request.user
# Admin is set to group creator
                group.save()
                group.members.add(request.user)
                messages.success(
                    request, 'Your group has been created successfully!')
                return redirect('group_detail', slug=group.slug)
        else:
            messages.error(
                request, 'There was an error creating your group.'
                ' Please try again.')
    else:
        form = GroupForm()
    return render(request, 'post_hub/create_group.html', {'form': form})


def group_detail(request, slug):
    """
    Display the details of a specific user group, including its
    posts and comments.

    This view function retrieves a user group based on its slug and displays
    its details, including paginated posts and comments. It also handles
    the submission of new comments and updates to the group details
    by the group admin.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the group to be retrieved.

    Returns:
        HttpResponse: The rendered template displaying the group details,
                    posts, comments, and forms for posting comments and
                    updating group details.
    """
    group = get_object_or_404(UserGroup, slug=slug)
    posts = group.group_posts.filter(status=1).order_by("-created_at")
# Using the group model and the post models related name group_posts to
# retrieve the posts in the group from the post model.
    comments = Comment.objects.filter(group=group, post__isnull=True)
# Only comments that are related to the group and not to a specific
# post are retrieved. post__isnull=True can be used to filter comments
# that are not related to a post. This is useful for comments that
# are related to a group or a category. this is part of the Django
# ORM and is used to filter objects based on the presence or
# absence of a related object. In this case, it is used to
# filter comments that are not related to a post.

    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    comment_form = CommentForm()
    admin_form = GroupAdminForm(instance=group)

    if request.method == 'POST':
        # if a post request is made whilst a user is
        # using the group detail view,
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to post a comment.')
            return redirect('account_login')

        if 'form_type' in request.POST:
            form_type = request.POST['form_type']
            if form_type == 'admin_form' and request.user == group.admin:
                admin_form = GroupAdminForm(
                    request.POST, request.FILES, instance=group)
                if admin_form.is_valid():
                    admin_form.save()
                    messages.success(
                        request, 'Group details updated successfully!')
                    return redirect('group_detail', slug=slug)
                else:
                    messages.error(
                        request, 'There was an error updating the group'
                        ' details. Please try again.')
            elif form_type == 'comment_form':
                comment_form = CommentForm(request.POST, request.FILES)
                if comment_form.is_valid():
                    user_comment = comment_form.save(
                        commit=False, author=request.user)
                    user_comment.group = group
                    user_comment.save()
                    messages.success(
                        request, 'Your comment has been posted successfully!')
                    return redirect('group_detail', slug=slug)
                else:
                    messages.error(
                        request, 'There was an error posting your comment.'
                        ' Please try again.')

    context = {
        'usergroup': group,
        'group_only_post': posts,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'comments': comments,
        'comment_form': comment_form,
        'admin_form': admin_form,
        'allcomments': comments,
    }
# A context dicitonary is used to pass what is needed to the
# template for rendering to the user.
    return render(request, 'post_hub/group_detail.html', context)


@login_required
def join_group(request, slug):
    """
    Handle the joining of a user to a group.

    This view function allows an authenticated user to join a group. It checks
    if the user is already a member of the group. If not, the user is added
    to the group's members. Appropriate success or info messages are displayed
    based on the user's membership status.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the group to be joined.

    Returns:
        HttpResponse: A redirect to the group detail page.
    """
    group = get_object_or_404(UserGroup, slug=slug)
    if request.user not in group.members.all():
        # The user is added to the group if they are not
        # already a member if a join request is made.
        group.members.add(request.user)
        messages.success(request, f'You have joined the group {group.name}!')
    else:
        messages.info(
            request, f'You are already a member of the group {group.name}.')
    return redirect('group_detail', slug=slug)


def group_index(request):
    """
    Display a list of user groups and their latest posts.

    This view function retrieves all user groups and their latest posts.
    It also handles search functionality to filter user groups based on a
    query string provided in the URL.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the search query.

    Returns:
        HttpResponse: The rendered template displaying the list of user groups
                    and their latest posts.
    """
    groups = UserGroup.objects.all()
    group_posts = []
    query = request.GET.get('q')
# When a form is sent by the user with "GET" , the data is stored in the URL
# as a query string. Example : http://example.com/search?q=search_term
# The query string is retrieved from the URL using GET, this is a dictionary
# that containes the paramters from the URL. Then the value assocciated with
# the key 'q' is stored in the request.GET dictionary.

    if query:
        usergroups = UserGroup.objects.filter(name__icontains=query)
# *my_field*__icontains is a field lookup that is used to perform
# case-insensitive containment test. This is used to filter the usergroups
# based on the query string from the URL.
# learned from =
# https://docs.djangoproject.com/en/3.2/ref/models/querysets/#icontains
    else:
        usergroups = UserGroup.objects.none()

    for group in groups:
        post = group.group_posts.filter(
            status=1).order_by('-created_at').first()
        group_posts.append((group, post))

    return render(request, 'post_hub/group_index.html', {
        'group_posts': group_posts, 'usergroups': usergroups})


def remove_member(request, slug, user_id):
    """
    Handle the removal of a member from a group.

    This view function allows the admin of a group to remove a member
    from the group. It checks if the current user is the admin of the group.
    If not, an error message is displayed. If the user is the admin,
    the specified member is removed from the group.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the group from which the member
                    is to be removed.
        user_id (int): The ID of the user to be removed from the group.

    Returns:
        HttpResponse: A redirect to the group detail page.
    """
    group = get_object_or_404(UserGroup, slug=slug)
    if request.user != group.admin:
        messages.error(
            request, 'You are not authorized to remove members from this'
            ' group.')
        return redirect('group_detail', slug=slug)

    user_remove = get_object_or_404(User, id=user_id)
    group.members.remove(user_remove)
    messages.success(
        request, f'{user_remove.username} has been removed from the group.')
    return redirect('group_detail', slug=slug)


class CategoryDetailView(DetailView):
    """
    Display the details of a specific category, including its posts.

    This view class retrieves a category based on its slug and displays
    its details, including the posts in the category. It also adds
    suggested categories to the context.

    Attributes:
        model (Model): The model to be retrieved (Category).
        template_name (str): The template to render the category details.
        context_object_name (str): The context variable name for
                                the category object.

    Methods:
        get_object(queryset=None):
            Retrieves the category object based on the slug provided
            in the URL.

        get_context_data(**kwargs):
            Adds additional context data to the template, including the posts
            in the category and suggested categories.
    """
    model = Category
    template_name = 'post_hub/category_detail.html'
    context_object_name = 'category'

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Category, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
# The get_context_data method is overridden to add
# the posts in the category to the context.
        category = self.get_object()
# The category object is retrieved from the context.
        context['posts'] = Post.objects.filter(
            category=category, status=1).order_by("-created_at")
# The posts in the category are retrieved and added to the context.
        context['suggested_categories'] = Category.get_random_categories()
        return context


@login_required
def view_profile(request, username):
    """
    Display the profile of a user.

    This view function retrieves and displays the profile of a user based
    on their username. It handles private profiles and paginates the user's
    posts and comments. It also calculates user statistics and assigns grades
    based on the number of posts and comments.

    Args:
        request (HttpRequest): The HTTP request object.
        username (str): The username of the user whose profile is to be viewed.

    Returns:
        HttpResponse: The rendered template displaying the user's profile,
                    posts, comments, groups, and statistics.
    """
    user = get_object_or_404(User, username=username)
    # The user object is retrieved from the database using the username.
    profile = user.user_profile
    # The profile object is retrieved from the user object.
    if profile.is_private and request.user != user:
        # If the profile is private and the current user is not
        # the user whose profile is being viewed,
        return render(request, 'post_hub/private_profile.html')

    user_posts = profile.get_user_posts().order_by('-created_at')
    user_comments = profile.get_user_comments().order_by('created_at')
    user_groups = profile.get_user_groups().order_by('name')

    # User stats
    post_count = user_posts.count()
    comment_count = user_comments.count()

    # A fun grade system
    if post_count < 1:
        post_grade = 'Newbie'
    elif post_count < 10:
        post_grade = 'Regular'
    elif post_count < 20:
        post_grade = 'Veteran'
    else:
        post_grade = 'Elite'

    if comment_count < 5:
        comment_grade = 'Newbie'
    elif comment_count < 15:
        comment_grade = 'Regular'
    elif comment_count < 35:
        comment_grade = 'Veteran'
    else:
        comment_grade = 'Elite'

    stat_tuple = (post_count, comment_count, post_grade, comment_grade)

    # Paginate user posts
    post_paginator = Paginator(user_posts, 3)
    post_page_number = request.GET.get('post_page')
    post_page_obj = post_paginator.get_page(post_page_number)

    # Paginate user comments
    comment_paginator = Paginator(user_comments, 3)
    comment_page_number = request.GET.get('comment_page')
    comment_page_obj = comment_paginator.get_page(comment_page_number)

    return render(request, 'post_hub/profile.html', {
        'profile': profile,
        'post_page_obj': post_page_obj,
        'comment_page_obj': comment_page_obj,
        'user_groups': user_groups,
        'stat_tuple': stat_tuple,
    })


@login_required
def edit_profile(request):
    """
    Handle the editing of a user's profile.

    This view function allows authenticated users to edit their profile.
    It handles form submission and image uploads. If the form is valid,
    the profile is updated.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for editing the profile or a
                    redirect to the profile view page upon successful update.
    """
    user = request.user
    profile = Profile.objects.get(user=user)
    # 'created' variable is required, false-positive PEP8 error

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your profile has been updated successfully!')
            return redirect('view_profile', username=user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'post_hub/edit_profile.html', {'form': form})


def terms_conditions(request):
    """
    Display the terms and conditions page.

    This view function renders the terms and conditions page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for the terms and conditions page.
    """
    return render(request, 'post_hub/terms_conditions.html')


def contact(request):
    """
    Display the contact page.

    This view function renders the contact page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for the contact page.
    """
    return render(request, 'post_hub/contact.html')

def security(request):
    """
    Display the security page.

    This view function renders the security page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template for the security page.
    """
    return render(request, 'post_hub/security.html')


def send_email(request):
    """
    Handle the sending of an email from the contact form.

    This view function processes the contact form submission and sends an email
    with the provided details. If the email is sent successfully, a success
    message is displayed.

    Args:
        request (HttpRequest): The HTTP request object containing
                            the form data.

    Returns:
        HttpResponse: The rendered template for the contact page.
    """
    if request.method == 'POST':
        name = request.POST('name')
        email = request.POST('email')
        subject = request.POST('subject')
        message = request.POST('message')

        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            ['maxwise70@hotmail.co.uk'],
        )
        messages.success(request, 'Your email has been sent successfully!')
    return render(request, 'post_hub/contact.html')
