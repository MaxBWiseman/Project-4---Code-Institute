from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from .models import Comment, Post, Category

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



# In Django forms, when you are dealing with model instances,
# you need to provide the primary key (ID) of the related objects
# rather than the objects themselves. This is because the form expects
# the ID to associate the form data with the correct database records.
        