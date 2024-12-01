"""
This module contains the unit tests for the application.

Tests:
    PostFormTest4SpellChecker: Tests the spell checker functionality
                            in the PostForm.

Utilities:
    Uses Django's TestCase for setting up and tearing down tests.
    Utilizes Django's Client for simulating HTTP requests.
    Employs SimpleUploadedFile for testing file uploads.
    Leverages PIL for image creation in tests.
"""
import json
import tempfile

from PIL import Image

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, Profile, UserGroup, Vote


class PostFormTest4SpellChecker(TestCase):
    """
    Tests the spell checker functionality in the PostForm.

    Methods:
        test_spell_checker(): Tests the spell checker with
                        various category names.
    """
    def test_spell_checker(self):
        """
        Tests the spell checker with various category names.

        This method tests the PostForm with both correctly spelled and
        intentionally misspelled category names to ensure that
        the spell checker suggests the correct spelling for misspelled
        names and validates correctly spelled names.

        The test cases include:
            - A misspelled category name "technology".
            - A correctly spelled category name "technology".
            - A misspelled category name "development".
            - A correctly spelled category name "development".
        """
        # Test with a misspelled category name "technology"
        form_data = {
            'title': 'Test Post',
            'blurb': 'This is a test post.',
            'content': 'Content of the test post.',
            'new_category': 'tehcnology'  # Intentionally misspelled
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_category', form.errors)
        self.assertTrue(any(
            "Did you mean 'technology'?" in error for error in form.errors[
                'new_category']))

        # Test with a correctly spelled category name "technology"
        form_data['new_category'] = 'technology'
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test with a misspelled category name "development"
        form_data['new_category'] = 'develpoment'  # Intentionally misspelled
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_category', form.errors)
        self.assertTrue(any(
            "Did you mean 'development'?" in error for error in form.errors[
                'new_category']))

        # Test with a correctly spelled category name "development"
        form_data['new_category'] = 'development'
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())


class CommentFormTest(TestCase):
    """
    Tests the CommentForm functionality.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_comment_form_valid(): Tests the form with valid data.
        test_comment_form_no_parent(): Tests the form with valid
                                    data but no parent.
        test_comment_form_empty_content(): Tests the form with empty content.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a user, a category, a post, and a parent comment
        to be used in the tests.
        """
        # Create a user for the author
        self.user = User.objects.create_user(
            username='testuser', password='12345')

        # Create a Category for the post
        self.category = Category.objects.create(category_name='Test Category')

        # Create a post for the comment
        self.post = Post.objects.create(
            title='Test Post', blurb='Test Blurb',
            content='Test Content', category=self.category, author=self.user)

        # Create a parent comment for testing
        self.parent_comment = Comment.objects.create(
            content="Parent comment", author=self.user, post=self.post)

    def test_comment_form_valid(self):
        """
        Tests the form with valid data.

        This method tests the CommentForm with valid data to ensure that
        the form is valid.
        """
        # Test with valid data
        form_data = {
            'content': 'This is a test comment.',
            'parent': self.parent_comment.id,
            'author': self.user.id,
            'post': self.post.id
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_no_parent(self):
        """
        Tests the form with valid data but no parent.

        This method tests the CommentForm with valid data but without a parent
        comment to ensure that the form is still valid.
        """
        # Test with valid data but no parent
        form_data = {
            'content': 'This is a test comment without parent.',
            'author': self.user.id,
            'post': self.post.id
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_empty_content(self):
        """
        Tests the form with empty content.

        This method tests the CommentForm with empty content to ensure that
        the form is invalid and raises the appropriate validation error.
        """
        # Test with empty content
        form_data = {
            'content': '',
            'parent': self.parent_comment.id,
            'author': self.user.id,
            'post': self.post.id
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)


class PostFormTest(TestCase):
    """
    Tests the PostForm functionality.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_post_form_get(): Tests the GET request for the post form.
        test_post_form_valid(): Tests the form with valid data.
        test_post_form_no_category(): Tests the form with valid data
                                    but no category.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user,
        and a category to be used in the tests.
        """
        self.client = Client()
# I created a Client object called self.client to simulate a user
# interacting with the application. The Client object allows me to
# make requests to the views and test the responses.

        # Create a user for the author
        self.user = User.objects.create_user(
            username='testuser', password='12345')

        # Create a Category for the post
        self.category = Category.objects.create(category_name='Test Category')

    def test_post_form_get(self):
        """
        Tests the GET request for the post form.

        This method tests the GET request for the create_post view to ensure
        that the response status code is 200 and the correct template is used.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('create_post'))
# response is the response from the view function when
# it is called with a GET request. We use the reverse function
# to get the URL of the create_post view.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/create_post.html')
# assertTemplateUsed checks if the response uses the specified template.

    def test_post_form_valid(self):
        """
        Tests the form with valid data.

        This method tests the PostForm with valid data to ensure that
        the form submission is successful and the response status code is 302.
        """
        self.client.login(username='testuser', password='12345')
        # Test with valid data
        form_data = {
            'title': 'Test Post',
            'blurb': 'This is a test post.',
            'content': 'Content of the test post.',
            'category': self.category.id,
            'author': self.user.id
        }
        response = self.client.post(reverse('create_post'), data=form_data)
# This is a better way to test the form submission because it simulates
# a real user interaction with the application.
        self.assertEqual(response.status_code, 302)

    def test_post_form_no_category(self):
        """
        Tests the form with valid data but no category.

        This method tests the PostForm with valid data but without a category
        to ensure that the form is invalid and raises the
        appropriate validation error.
        """
        self.client.login(username='testuser', password='12345')
        # Test with valid data but no category
        form_data = {
            'title': 'Test Post',
            'blurb': 'This is a test post.',
            'content': 'Content of the test post.',
            'author': self.user.id,
            'category': '',
            'new_category': '',
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())  # Form should be invalid
        # Check that the error is in the __all__ key
        self.assertIn('__all__', form.errors)
        self.assertIn(
            'You must provide either a new category'
            ' or select an existing category.', form.errors['__all__'])
# I used the assertIn method to check if the error message is in the __all__
# key of the errors dictionary. I learned that errors are stored in __all__
# key when they are not associated with a specific field.


class PostDetailViewTest(TestCase):
    """
    Tests the PostDetailView functionality.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_post_detail_page(): Tests the post detail page.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, a category,
        and a post to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(title='Test Post', blurb='Test Blurb',
                                        content='Test Content',
                                        category=self.category,
                                        author=self.user)

    def test_post_detail_page(self):
        """
        Tests the post detail page.

        This method tests the post detail page to ensure that
        the response status code is 200, the correct template is used,
        and the response contains the post title and content.
        """
        url = reverse('post_detail', args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/post_detail.html')
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)


class CommentModelTest(TestCase):
    """
    Tests the Comment model functionality.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a user, a category, a post,
        and a comment to be used in the tests.
        """
        # Create a user
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')

        # Create a category
        self.category = Category.objects.create(category_name='Test Category')

        # Create a post
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            author=self.user,
            category=self.category,
            status=1
        )

        # Create a comment
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment.',
            status=True
        )

    def test_comment_creation(self):
        """
        Tests that the comment was created successfully.

        This method checks that the comment's content, author, post, and status
        are correctly set.
        """
        # Test that the comment was created successfully
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertEqual(self.comment.author.username, 'testuser')
        self.assertEqual(self.comment.post.title, 'Test Post')
        self.assertTrue(self.comment.status)

    def test_comment_str_method(self):
        """
        Tests the __str__ method of the Comment model.

        This method checks that the __str__ method of the Comment model
        returns the expected string representation.
        """
        # Test the __str__ method of the Comment model
        self.assertEqual(str(self.comment), f'Comment by {
                         self.user} on {self.post}')


# In Django forms, when you are dealing with model instances,
# you need to provide the primary key (ID) of the related objects
# rather than the objects themselves. This is because the form expects
# the ID to associate the form data with the correct database records.

# FIXED - ALL UNITTEST IS BROKEN DUE TO THIS ERROR =
# gitpod /workspace/Project-4---Code-Institute (main) $ $ pyth manage.py test
# Found 8 test(s).
# Creating test database for alias 'default'...
# Got an error creating the test database: permission denied to create database

class VoteFunctionalityTest(TestCase):
    """
    Tests the voting functionality for posts and comments.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_vote_post(): Tests the voting functionality for a post.
        test_vote_comment(): Tests the voting functionality for a comment.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, a category, a post,
        and a comment to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(category_name='test category')
        self.author = User.objects.create_user(
            username='author', password='12345')
        self.post = Post.objects.create(title='Test Post', blurb='Test Blurb',
                                        content='Test Content',
                                        category=self.category,
                                        author=self.author)
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content='Test Comment')
        self.client.login(username='testuser', password='12345')

    def test_vote_post(self):
        """
        Tests the voting functionality for a post.

        This method tests the voting functionality for a post
        by sending a POST request to the vote view with the post ID
        and upvote status. It checks if the vote is created
        and then deleted successfully.
        """
        url = reverse('vote')
        data = {
            'post_id': self.post.id,
            'is_upvote': True
        }

        json_data = json.dumps(data)
        # json.dumps() is used to convert a python dictionary to a JSON string.

        response = self.client.post(
            url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote.objects.filter(
            post=self.post, user=self.user).exists())
        # Check if the vote was created successfully

        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vote.objects.filter(
            post=self.post, user=self.user).exists())
        # Check if the vote was deleted successfully,
        # this works as the view functionality is set to delete
        # the vote if it already exists in the same vote category

    def test_vote_comment(self):
        """
        Tests the voting functionality for a comment.

        This method tests the voting functionality for a comment
        by sending a POST request to the vote view with the comment ID
        and upvote status. It checks if the vote is created and
        then deleted successfully.
        """
        url = reverse('vote')
        data = {
            'comment_id': self.comment.id,
            'is_upvote': True
        }

        json_data = json.dumps(data)

        response = self.client.post(
            url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote.objects.filter(
            comment=self.comment, user=self.user).exists())

        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vote.objects.filter(
            comment=self.comment, user=self.user).exists())


class EditPostTest(TestCase):
    """
    Tests the functionality of editing a post.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_edit_post(): Tests the editing functionality for a post.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, a category,
        and a post to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(category_name='test category')
        self.post = Post.objects.create(
            title='Test Post',
            blurb='Test Blurb',
            content='Test Content',
            category=self.category,
            author=self.user
        )
        self.client.login(username='testuser', password='12345')

    def test_edit_post(self):
        """
        Tests the editing functionality for a post.

        This method tests the editing functionality for
        a post by sending a POST request to the edit_post
        view with the post data. It checks if the post is updated
        successfully and the response status code is 302.
        """
        url = reverse('edit_post', args=[self.post.slug])
        data = {
            'title': 'Edited Post',
            'blurb': 'Edited Blurb',
            'content': 'Edited Content',
            'category': self.category.id
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Edited Post')
        self.assertEqual(self.post.blurb, 'Edited Blurb')
        self.assertEqual(self.post.content, 'Edited Content')
        self.assertEqual(self.post.category, self.category)


class UserGroupTest(TestCase):
    """
    Tests the functionality of user groups.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_join_group(): Tests the functionality of joining a group.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user,
        and a user group to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.group = UserGroup.objects.create(
            name='Test Group', slug='test-group', admin=self.user)
        self.client.login(username='testuser', password='12345')

    def test_join_group(self):
        """
        Tests the functionality of joining a group.

        This method tests the functionality of joining a group
        by sending a POST request to the join_group view with the group slug.
        It checks if the user is added to the group's members and if the
        appropriate success message is displayed.
        """
        url = reverse('join_group', args=[self.group.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, self.group.members.all())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), f'You have joined the group {
                         self.group.name}!')


class CategoryDetailViewTest(TestCase):
    """
    Tests the CategoryDetailView functionality.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_category_detail_view(): Tests the category detail view.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, a category,
        and a post to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(
            category_name='Test Category', slug='test-category')
        self.post = Post.objects.create(
            title='Test Post',
            blurb='Test Blurb',
            content='Test Content',
            category=self.category,
            author=self.user
        )

    def test_category_detail_view(self):
        """
        Tests the category detail view.

        This method tests the category detail view to ensure that
        the response status code is 200, the correct template is used,
        and the response contains the category name and post title.
        """
        url = reverse('category_detail', args=[self.category.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/category_detail.html')
        self.assertContains(response, self.category.category_name)
        self.assertContains(response, self.post.title)


class CloudinaryImageUploadTest(TestCase):
    """
    Tests the functionality of image uploads to Cloudinary for comments.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        create_temp_image(): Creates a temporary image file for testing.
        test_image_upload_on_post_comment(): Tests image upload on
                                        a post comment.
        test_image_upload_on_group_comment(): Tests image upload on a
                                        group comment.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, a category, a post,
        and a user group to be used in the tests.
        """
        # Create a sample user, post, category, and user group for testing
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(
            title='Test Post', content='Test content',
            author=self.user, category=self.category)
        self.group = UserGroup.objects.create(
            name='Test Group', slug='test-group', admin=self.user)
        self.client.login(username='testuser', password='12345')

    def create_temp_image(self):
        """
        Creates a temporary image file for testing.

        This method creates a temporary image file with a
        red background and returns it.

        Returns:
            NamedTemporaryFile: A temporary image file.
        """
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        return temp_file

    def test_image_upload_on_post_comment(self):
        """
        Tests image upload on a post comment.

        This method tests the image upload functionality for a comment
        on a post by creating a temporary image file, submitting the comment
        form with the image, and verifying that the image URL is not empty.
        """
        # Create a sample image file
        temp_image = self.create_temp_image()
        image = SimpleUploadedFile(
            name=temp_image.name,
            content=temp_image.read(),
            content_type='image/jpeg'
        )

        # Create a comment with the image on a post
        form_data = {
            'parent': '',
            'content': 'Test comment with image on post',
            'group': '',
            'image': image
        }
        form = CommentForm(data=form_data, files={'image': image})
        print(form.errors)  # Print form errors for debugging
        self.assertTrue(form.is_valid())
        if form.is_valid():
            comment = form.save(commit=False, author=self.user)
            comment.post = self.post  # Set the post field
            comment.save()

            # Print the image URL for debugging
            print(f"Image URL: {comment.image}")

            # Verify that the image URL is not empty
            self.assertTrue(comment.image)

    def test_image_upload_on_group_comment(self):
        """
        Tests image upload on a group comment.

        This method tests the image upload functionality for a comment
        on a group by creating a temporary image file, submitting the
        comment form with the image, and verifying that the
        image URL is not empty.
        """
        # Create a sample image file
        temp_image = self.create_temp_image()
        image = SimpleUploadedFile(
            name=temp_image.name,
            content=temp_image.read(),
            content_type='image/jpeg'
        )

        # Create a comment with the image on a group
        form_data = {
            'parent': '',
            'content': 'Test comment with image on group',
            'group': self.group.id,
            'image': image
        }
        form = CommentForm(data=form_data, files={'image': image})
        print(form.errors)  # Print form errors for debugging
        self.assertTrue(form.is_valid())
        if form.is_valid():
            comment = form.save(commit=False, author=self.user)
            comment.post = None  # Ensure post is None for group comment
            comment.group = self.group
            print(f"Author: {comment.author}, Group: {
                  comment.group}")  # Debug print
            comment.save()

            # Print the image URL for debugging
            print(f"Image URL: {comment.image}")

            # Verify that the image URL is not empty
            self.assertTrue(comment.image)

# This test is sometimes commented out as to not
# send too many images to cloudinary


class ProfileModelTest(TestCase):
    """
    Tests the Profile model functionality.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_profile_creation(): Tests the creation of a profile.
        test_profile_str_method(): Tests the __str__ method of Profile model.
        test_get_user_posts(): Tests the retrieval of user posts.
        test_get_user_comments(): Tests the retrieval of user comments.
        test_get_user_groups(): Tests the retrieval of user groups.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a user and retrieves the associated
        profile to be used in the tests.
        """
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_creation(self):
        """
        Tests the creation of a profile.

        This method checks that the profile's user, bio, location,
        and privacy status are correctly set upon creation.
        """
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, '')
        self.assertEqual(self.profile.location, '')
        self.assertFalse(self.profile.is_private)

    def test_profile_str_method(self):
        """
        Tests the __str__ method of the Profile model.

        This method checks that the __str__ method of the Profile model
        returns the expected string representation.
        """
        self.assertEqual(str(self.profile), 'testuser')

    def test_get_user_posts(self):
        """
        Tests the retrieval of user posts.

        This method checks that the get_user_posts method returns the posts
        created by the user.
        """
        post = Post.objects.create(title='Test Post', content='Test Content',
                                   author=self.user,
                                   category=Category.objects.create(
                                       category_name='Test Category'))
        self.assertIn(post, self.profile.get_user_posts())

    def test_get_user_comments(self):
        """
        Tests the retrieval of user comments.

        This method checks that the get_user_comments method
        returns the comments made by the user.
        """
        post = Post.objects.create(title='Test Post', content='Test Content',
                                   author=self.user,
                                   category=Category.objects.create(
                                       category_name='Test Category'))
        comment = Comment.objects.create(
            post=post, author=self.user, content='Test Comment')
        self.assertIn(comment, self.profile.get_user_comments())

    def test_get_user_groups(self):
        """
        Tests the retrieval of user groups.

        This method checks that the get_user_groups method returns the groups
        the user is a member of.
        """
        group = UserGroup.objects.create(name='Test Group', admin=self.user)
        group.members.add(self.user)
        self.assertIn(group, self.profile.get_user_groups())


class ViewProfileTest(TestCase):
    """
    Tests the functionality of viewing user profiles.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        test_view_profile(): Tests viewing a public profile.
        test_view_private_profile(): Tests viewing a private profile.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, and retrieves the
        associated profile to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.profile = Profile.objects.get(user=self.user)
        self.client.login(username='testuser', password='12345')

    def test_view_profile(self):
        """
        Tests viewing a public profile.

        This method tests viewing a public profile by sending a GET request
        to the view_profile view with the user's username.
        It checks if the response status code is 200, the correct template
        is used, and the response contains the user's username,
        bio, and location.
        """
        url = reverse('view_profile', args=[self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/profile.html')
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.profile.bio)
        self.assertContains(response, self.profile.location)

    def test_view_private_profile(self):
        """
        Tests viewing a private profile.

        This method tests viewing a private profile by setting
        the profile to private, logging out the current user, creating and
        logging in with a different test account, and sending a GET request
        to the view_profile view with the original user's username. It checks
        if the response status code is 200 and the correct template is used.
        """
        self.profile.is_private = True
        self.profile.save()
        self.client.logout()

        # Create and log in with a different test account
        User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')

        url = reverse('view_profile', args=[self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/private_profile.html')


class EditProfileTest(TestCase):
    """
    Tests the functionality of editing a user profile.

    Methods:
        setUp(): Sets up the test environment by creating necessary objects.
        create_temp_image(): Creates a temporary image file for testing.
        test_edit_profile(): Tests the editing functionality for user profiles.
    """
    def setUp(self):
        """
        Sets up the test environment by creating necessary objects.

        This method creates a client, a user, and retrieves the
        associated profile to be used in the tests.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        self.profile = Profile.objects.get(user=self.user)
        self.client.login(username='testuser', password='12345')

    def create_temp_image(self):
        """
        Creates a temporary image file for testing.

        This method creates a temporary image file with a red background and
        returns it.

        Returns:
            NamedTemporaryFile: A temporary image file.
        """
        # Create a temporary image file
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        return temp_file

    def test_edit_profile(self):
        """
        Tests the editing functionality for a user profile.

        This method tests the editing functionality for a user profile by
        sending a POST request to the edit_profile view with the profile data,
        including a temporary image file. It checks if the profile is updated
        successfully and the response status code is 302.
        """
        url = reverse('edit_profile')
        temp_image = self.create_temp_image()
        image = SimpleUploadedFile(
            name=temp_image.name,
            content=temp_image.read(),
            content_type='image/jpeg'
        )
        data = {
            'bio': 'Updated bio',
            'location': 'Updated location',
            'user_image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertEqual(self.profile.location, 'Updated location')
        self.assertTrue(self.profile.user_image)
