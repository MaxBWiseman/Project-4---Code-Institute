from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from .models import Comment, Post, Category, Vote, UserGroup
import json

class PostFormTest4SpellChecker(TestCase):
    def test_spell_checker(self):
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
        self.assertTrue(any("Did you mean 'technology'?" in error for error in form.errors['new_category']))
        
        # Test with a correctly spelled category name "technology"
        form_data['new_category'] = 'technology'
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test with a misspelled category name "development"
        form_data['new_category'] = 'develpoment'  # Intentionally misspelled
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_category', form.errors)
        self.assertTrue(any("Did you mean 'development'?" in error for error in form.errors['new_category']))
        
        # Test with a correctly spelled category name "development"
        form_data['new_category'] = 'development'
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

class CommentFormTest(TestCase):
    def setUp(self):
        # Create a user for the author
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a Category for the post
        self.category = Category.objects.create(category_name='Test Category')

         # Create a post for the comment
        self.post = Post.objects.create(title='Test Post', blurb='Test Blurb', content='Test Content', category=self.category , author=self.user)
        
         # Create a parent comment for testing
        self.parent_comment = Comment.objects.create(content="Parent comment", author=self.user, post=self.post)
        
    def test_comment_form_valid(self):
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
        # Test with valid data but no parent
        form_data = {
            'content': 'This is a test comment without parent.',
            'author': self.user.id,
            'post': self.post.id
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_empty_content(self):
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
    def setUp(self):
        
        self.client = Client()
# I created a Client object called self.client to simulate a user interacting with the application.
# The Client object allows me to make requests to the views and test the responses.
        
        # Create a user for the author
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a Category for the post
        self.category = Category.objects.create(category_name='Test Category')
        
        
    def test_post_form_get(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('create_post'))
# response is the response from the view function when it is called with a GET request.
# we use the reverse function to get the URL of the create_post view.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/create_post.html')
#assertTemplateUsed checks if the response uses the specified template.
    
    
    def test_post_form_valid(self):
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
# This is a better way to test the form submission because it simulates a real user interaction with the application.
        self.assertEqual(response.status_code, 302)
        
    def test_post_form_no_category(self):
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
        self.assertIn('__all__', form.errors)  # Check that the error is in the __all__ key
        self.assertIn('You must provide either a new category or select an existing category.', form.errors['__all__'])
# I used the assertIn method to check if the error message is in the __all__ key of the errors dictionary.
# I learned that errors are stored in __all__ key when they are not associated with a specific field.

class PostDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(category_name='Test Category')
        self.post = Post.objects.create(title='Test Post', blurb='Test Blurb', content='Test Content', category=self.category, author=self.user)

    def test_post_detail_page(self):
        url = reverse('post_detail', args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/post_detail.html')
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        
        
class CommentModelTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

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
        # Test that the comment was created successfully
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertEqual(self.comment.author.username, 'testuser')
        self.assertEqual(self.comment.post.title, 'Test Post')
        self.assertTrue(self.comment.status)

    def test_comment_str_method(self):
        # Test the __str__ method of the Comment model
        self.assertEqual(str(self.comment), f'Comment by {self.user} on {self.post}')


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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345') 
        self.category = Category.objects.create(category_name='test category')
        self.author = User.objects.create_user(username='author', password='12345')
        self.post = Post.objects.create(title='Test Post', blurb='Test Blurb', content='Test Content', category=self.category, author=self.author)
        self.comment = Comment.objects.create(post=self.post, author=self.user, content='Test Comment')
        self.client.login(username='testuser', password='12345')
        
    def test_vote_post(self):
        url = reverse('vote')
        data = {
            'post_id': self.post.id,
            'is_upvote': True
        }
        
        json_data = json.dumps(data)
        # json.dumps() is used to convert a python dictionary to a JSON string.
        
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote.objects.filter(post=self.post, user=self.user).exists())
        # Check if the vote was created successfully
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vote.objects.filter(post=self.post, user=self.user).exists())
        # Check if the vote was deleted successfully, this works as the view functionality
        # is set to delete the vote if it already exists in the same vote category
        
    def test_vote_comment(self):
        url = reverse('vote')
        data = {
            'comment_id': self.comment.id,
            'is_upvote': True
        }
        
        json_data = json.dumps(data)
        
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote.objects.filter(comment=self.comment, user=self.user).exists())
        
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vote.objects.filter(comment=self.comment, user=self.user).exists())
        
class EditPostTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = UserGroup.objects.create(name='Test Group', slug='test-group', admin=self.user)
        self.client.login(username='testuser', password='12345')

    def test_join_group(self):
        url = reverse('join_group', args=[self.group.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, self.group.members.all())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), f'You have joined the group {self.group.name}!')


class CategoryDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(category_name='Test Category', slug='test-category')
        self.post = Post.objects.create(
            title='Test Post', 
            blurb='Test Blurb', 
            content='Test Content', 
            category=self.category, 
            author=self.user
        )

    def test_category_detail_view(self):
        url = reverse('category_detail', args=[self.category.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_hub/category_detail.html')
        self.assertContains(response, self.category.category_name)
        self.assertContains(response, self.post.title)