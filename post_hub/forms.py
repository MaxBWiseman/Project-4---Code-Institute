from django import forms
from mptt.forms import TreeNodeChoiceField
from ckeditor.widgets import CKEditorWidget
from .models import Comment, Post, Category, UserGroup, Profile, User
from spellchecker import SpellChecker
import cloudinary
from cloudinary.uploader import upload
from cloudinary.exceptions import Error
from django.core.files.uploadedfile import InMemoryUploadedFile

class CommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all(), required=False, widget=forms.HiddenInput())
    group = forms.ModelChoiceField(queryset=UserGroup.objects.all(), required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Comment
        fields = ('parent', 'content', 'group', 'image')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def save(self, *args, **kwargs):
        author = kwargs.pop('author', None)
        comment = super().save(commit=False)
        if author:
            comment.author = author
        image = self.cleaned_data.get('image')

        # Handle comment image upload to cloudinary
        if image:
            try:
                upload_result = upload(
                    image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good', 'fetch_format': 'auto'},
                    eager=[{'width': 700, 'height': 700, 'crop': 'limit'}]
                )
                comment.image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        comment.save()
        Comment.objects.rebuild()
        return comment

class PostForm(forms.ModelForm):
    new_category = forms.CharField(required=False, max_length=100, label='New Category')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(queryset=UserGroup.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Post
        fields = ('title', 'blurb', 'banner_image', 'content', 'category', 'new_category', 'group')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'blurb': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 40}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Post Title',
            'blurb': 'Short Description',
            'banner_image': 'Upload Banner Image',
            'content': 'Post Content',
        }
        
    def clean(self):
        cleaned_data = super().clean()
# super is used to call the parent class (forms.ModelForm) and use its data.
# clean is used to validate the form data and return the cleaned data
        new_category_name = cleaned_data.get('new_category')
# I used the get method to get the value of the new_category field from the cleaned_data dictionary.
        category = cleaned_data.get('category')
# I used the get method to get the value of the category field from the cleaned_data dictionary.
        if not new_category_name and not category:
            raise forms.ValidationError('You must provide either a new category or select an existing category.')
# I raised a ValidationError with a message if both new_category_name and category are empty.
        if new_category_name:
            existing_categories = Category.objects.filter(category_name=new_category_name)
# I used the filter method to get all the categories with the same name as new_category_name.
            if existing_categories.count() >= 2:
                self.add_error('new_category', 'There cannot be more than 2 categories with the same name.')
# I raised a ValidationError with a message if there are more than two categories with the same name.
            spell = SpellChecker()
# I reasearched a way to spell check my categories and came across the spellchecker library.
# First, I imported the SpellChecker class from the spellchecker module.
# Then, I created a SpellChecker object called spell.
            misspelled = spell.unknown([new_category_name])
# I used the unknown method to check if the category name is misspelled.
            if misspelled:
                corrected = spell.correction(new_category_name)
# If the category name is misspelled, I used the correction method to get the correct spelling.
                self.add_error('new_category', f"Did you mean '{corrected}'?")
# I raised a ValidationError with a message that suggests the correct spelling.
        
        return cleaned_data
    
    def save(self, commit=True):
# I overrode the save method to handle the new_category field.
        post = super().save(commit=False)
# This line calls the save method of the parent class with super (forms.ModelForm) and use its data.
# and sets commit to False.
        new_category_name = self.cleaned_data.get('new_category')
# I used the get method to get the value of the new_category field from the cleaned_data dictionary.
        if new_category_name:
            category, created = Category.objects.get_or_create(category_name=new_category_name)
# get_or_create is a method that tries to get a Category object with the specified category_name.
# If the Category object does not exist, it creates a new one, if it does, it returns the existing one.
            post.category = category
# I set the category of the post to the newly created category.
        else:
            post.category = self.cleaned_data.get('category')
# If new_category_name is empty, I set the category of the post to the selected category in dropdown menu.

        # Handle banner image upload to Cloudinary
        banner_image = self.cleaned_data.get('banner_image')
        if banner_image and isinstance(banner_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    banner_image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good', 'fetch_format': 'auto'},
                )
                post.banner_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            post.save()
# If commit is True, I save the post object to the database.
        
        return post
# The code above checks if a new category name was provided. If so, it either gets the existing
# category or creates a new one and assigns it to the post.category field. If no new category
# name is provided, it assigns the selected category from the dropdown menu to the post.category field.

class GroupForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = UserGroup
        fields = ('name', 'description', 'group_image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'group_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Group Name',
            'description': 'Group Description',
            'group_image': 'Upload Group Image',
        }

    def save(self, commit=True):
        group = super().save(commit=False)
        group_image = self.cleaned_data.get('group_image')
        if group_image and isinstance(group_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    group_image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good', 'fetch_format': 'auto'},
                    eager=[{'width': 700, 'height': 700, 'crop': 'limit'}]
                )
                group.group_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            group.save()
        return group

class GroupAdminForm(forms.ModelForm):
    admin_message = forms.CharField(
        widget=CKEditorWidget(config_name='small_height'), required=False
    )
    description = forms.CharField(
        widget=CKEditorWidget(config_name='small_height'), required=False
    )
    group_image = forms.FileInput()

    class Meta:
        model = UserGroup
        fields = ('admin_message', 'description', 'group_image')
        labels = {
            'admin_message': 'Admin Message',
            'description': 'Update Group Description',
            'group_image': 'Upload New Group Image',
        }

    def save(self, commit=True):
        group = super().save(commit=False)
        group_image = self.cleaned_data.get('group_image')
        if group_image and isinstance(group_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    group_image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good', 'fetch_format': 'auto'},
                )
                group.group_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            group.save()
        return group
    
class ProfileForm(forms.ModelForm):
    location = forms.CharField(required=False)
    
    class Meta:
        model = Profile
        fields = ('bio', 'user_image', 'location', 'is_private')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'user_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'bio': 'Bio',
            'location': 'Location',
            'user_image': 'Upload Profile Image',
            'is_private': 'Private Account',
        }
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        user_image = self.cleaned_data.get('user_image')
        if user_image and isinstance(user_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    user_image,
                    resource_type='image',
                    folder='profiles/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good', 'fetch_format': 'auto'},
                )
                profile.user_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            profile.save()
        return profile