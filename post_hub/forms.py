"""
This module defines the forms used in the application.

Forms:
    CommentForm: A form for creating and updating comments.
    PostForm: A form for creating and updating posts.
    GroupAdminForm: A form for managing user groups.
    ProfileForm: A form for updating user profiles.

Utilities:
    Handles image uploads to Cloudinary and integrates
    Summernote for rich text editing.
"""
from cloudinary.uploader import upload
from cloudinary.exceptions import Error
from spellchecker import SpellChecker

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_summernote.widgets import SummernoteWidget

from mptt.forms import TreeNodeChoiceField

from .models import Comment, Post, Category, UserGroup, Profile


class CommentForm(forms.ModelForm):
    """
    A form for creating and updating comments.

    Fields:
        parent (TreeNodeChoiceField): The parent comment,
                                allowing for nested comments (MPTT).
        group (ModelChoiceField): The group to which the comment belongs.
        content (Textarea): The main content of the comment.
        image (FileInput): The image associated with the comment.

    Meta:
        model (Comment): The model that this form is associated with.
        fields (tuple): The fields to include in the form.
        widgets (dict): Custom widgets for the form fields.

    Methods:
        save(*_args, **kwargs): Saves the comment instance,
                            handling image upload to Cloudinary.
    """
    parent = TreeNodeChoiceField(
        queryset=Comment.objects.all(),
        required=False, widget=forms.HiddenInput())
    group = forms.ModelChoiceField(
        queryset=UserGroup.objects.all(),
        required=False, widget=forms.HiddenInput())

    class Meta:
        """
        Meta options for the CommentForm.

        Attributes:
            model (Comment): The model that this form is associated with.
            fields (tuple): The fields to include in the form.
            widgets (dict): Custom widgets for the form fields.
        """
        model = Comment
        fields = ('parent', 'content', 'group', 'image')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def save(self, *_args, **kwargs):
        """
        Saves the comment instance, handling image upload to Cloudinary.

        Args:
            *_args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Comment: The saved comment instance.
        """
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
                    transformation={'quality': 'auto:good',
                                    'fetch_format': 'auto'},
                    eager=[{'width': 700, 'height': 700, 'crop': 'limit'}]
                )
                comment.image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        comment.save()
        Comment.objects.rebuild()
        return comment


class PostForm(forms.ModelForm):
    """
    A form for creating and updating posts.

    Fields:
        new_category (CharField): A field for entering a new category name.
        category (ModelChoiceField): A dropdown field for selecting
                                an existing category.
        group (ModelChoiceField): A dropdown field for selecting a user group.
        content (CharField): A field for entering the main content of the post.

    Meta:
        model (Post): The model that this form is associated with.
        fields (tuple): The fields to include in the form.
        widgets (dict): Custom widgets for the form fields.
        labels (dict): Custom labels for the form fields.

    Methods:
        clean(): Validates the form data and returns the cleaned data.
        save(commit=True): Saves the post instance, handling the new_category
                        field and image upload to Cloudinary.
    """
    new_category = forms.CharField(
        required=False, max_length=100, label='New Category')
    category = forms.ModelChoiceField(queryset=Category.objects.all(
    ), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(queryset=UserGroup.objects.all(
    ), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=SummernoteWidget())

    class Meta:
        """
        Meta options for the PostForm.

        Attributes:
            model (Post): The model that this form is associated with.
            fields (tuple): The fields to include in the form.
            widgets (dict): Custom widgets for the form fields.
            labels (dict): Custom labels for the form fields.
        """
        model = Post
        fields = ('title', 'blurb', 'banner_image', 'content',
                  'category', 'new_category', 'group')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'blurb': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'cols': 40}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Post Title',
            'blurb': 'Short Description',
            'banner_image': 'Upload Banner Image',
            'content': 'Post Content',
        }

    def clean(self):
        """
        Validates the form data and returns the cleaned data.

        This method checks if either a new category name or existing category
        is provided. It also checks for duplicate category names and performs
        spell checking on the new category name.

        Returns:
            dict: The cleaned data.
        """
        cleaned_data = super().clean()
# super is used to call the parent class (forms.ModelForm) and use its data.
# clean is used to validate the form data and return the cleaned data
        new_category_name = cleaned_data.get('new_category')
# I used the get method to get the value of the new_category field
# from the cleaned_data dictionary.
        category = cleaned_data.get('category')
# I used the get method to get the value of the category field from
# the cleaned_data dictionary.
        if not new_category_name and not category:
            raise forms.ValidationError(
                'You must provide either a new category or'
                ' select an existing category.')
# I raised a ValidationError with a message if both
# new_category_name and category are empty.
        if new_category_name:
            existing_categories = Category.objects.filter(
                category_name=new_category_name)
# I used the filter method to get all the categories with
# the same name as new_category_name.
            if existing_categories.count() >= 2:
                self.add_error(
                    'new_category', 'There cannot be more than 2'
                    ' categories with the same name.')
# I raised a ValidationError with a message if there are
# more than two categories with the same name.
            spell = SpellChecker()
# I reasearched a way to spell check my categories and came
# across the spellchecker library. First, I imported the
# SpellChecker class from the spellchecker module.
# Then, I created a SpellChecker object called spell.
            misspelled = spell.unknown([new_category_name])
# I used the unknown method to check if the category name is misspelled.
            if misspelled:
                corrected = spell.correction(new_category_name)
# If the category name is misspelled, I used the correction
# method to get the correct spelling.
                self.add_error('new_category', f"Did you mean '{corrected}'?")
# I raised a ValidationError with a message that suggests the correct spelling.

        return cleaned_data

    def save(self, commit=True):
        """
        Saves the post instance, handling the new_category field and
        image upload to Cloudinary.

        Args:
            commit (bool): Whether to save the instance to the database.

        Returns:
            Post: The saved post instance.
        """
        # I overrode the save method to handle the new_category field.
        post = super().save(commit=False)
# This line calls the save method of the parent class with
# super (forms.ModelForm) and use its data. and sets commit to False.
        new_category_name = self.cleaned_data.get('new_category')
# I used the get method to get the value of the new_category
# field from the cleaned_data dictionary.
        if new_category_name:
            category, _created = Category.objects.get_or_create(
                category_name=new_category_name)
# get_or_create is a method that tries to get a Category
# object with the specified category_name.
# If the Category object does not exist, it creates a new one,
# if it does, it returns the existing one.
            post.category = category
# I set the category of the post to the newly created category.
        else:
            post.category = self.cleaned_data.get('category')
# If new_category_name is empty, I set the category of the post
# to the selected category in dropdown menu.

        # Handle banner image upload to Cloudinary
        banner_image = self.cleaned_data.get('banner_image')
        if banner_image and isinstance(banner_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    banner_image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good',
                                    'fetch_format': 'auto'},
                )
                post.banner_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            post.save()
# If commit is True, I save the post object to the database.

        return post
# The code above checks if a new category name was provided.
# If so, it either gets the existing category or creates a
# new one and assigns it to the post.category field. If no new category
# name is provided, it assigns the selected category from
# the dropdown menu to the post.category field.


class GroupForm(forms.ModelForm):
    """
    A form for creating and updating user groups.

    Fields:
        description (CharField): A field for entering the group description.

    Meta:
        model (UserGroup): The model that this form is associated with.
        fields (tuple): The fields to include in the form.
        widgets (dict): Custom widgets for the form fields.
        labels (dict): Custom labels for the form fields.

    Methods:
        save(commit=True): Saves the group instance,
                        handling image upload to Cloudinary.
    """
    description = forms.CharField(widget=SummernoteWidget())

    class Meta:
        """
        Meta options for the GroupForm.

        Attributes:
            model (UserGroup): The model that this form is associated with.
            fields (tuple): The fields to include in the form.
            widgets (dict): Custom widgets for the form fields.
            labels (dict): Custom labels for the form fields.
        """
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
        """
        Saves the group instance, handling image upload to Cloudinary.

        Args:
            commit (bool): Whether to save the instance to the database.

        Returns:
            UserGroup: The saved group instance.
        """
        group = super().save(commit=False)
        group_image = self.cleaned_data.get('group_image')
        if group_image and isinstance(group_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    group_image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good',
                                    'fetch_format': 'auto'},
                    eager=[{'width': 700, 'height': 700, 'crop': 'limit'}]
                )
                group.group_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            group.save()
        return group


class GroupAdminForm(forms.ModelForm):
    """
    A form for managing user groups by the admin.

    Fields:
        admin_message (CharField): A field for entering a message
                                to the group members.
        description (CharField): A field for updating the group description.
        group_image (FileField): A field for uploading a new group image.

    Meta:
        model (UserGroup): The model that this form is associated with.
        fields (tuple): The fields to include in the form.

    Methods:
        save(commit=True): Saves the group instance,
                        handling image upload to Cloudinary.
    """
    admin_message = forms.CharField(
        label='A message to your group members',
        widget=SummernoteWidget(attrs={'class': 'my-5'}),
        required=False
    )
    description = forms.CharField(
        label='Update group description',
        widget=SummernoteWidget(attrs={'class': 'my-5'}),
        required=False
    )
    group_image = forms.FileField(
        label='Upload new group image',
        widget=forms.FileInput(attrs={'class': 'my-5'}),
        required=False
    )

    class Meta:
        """
        Meta options for the GroupAdminForm.

        Attributes:
            model (UserGroup): The model that this form is associated with.
            fields (tuple): The fields to include in the form.
        """
        model = UserGroup
        fields = ('admin_message', 'description', 'group_image')

    def save(self, commit=True):
        """
        Saves the group instance, handling image upload to Cloudinary.

        Args:
            commit (bool): Whether to save the instance to the database.

        Returns:
            UserGroup: The saved group instance.
        """
        group = super().save(commit=False)
        group_image = self.cleaned_data.get('group_image')
        if group_image and isinstance(group_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    group_image,
                    resource_type='image',
                    folder='groups/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good',
                                    'fetch_format': 'auto'},
                )
                group.group_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            group.save()
        return group


class ProfileForm(forms.ModelForm):
    """
    A form for updating user profiles.

    Fields:
        location (CharField): A field for entering the user's location.
        bio (CharField): A field for entering the user's biography.

    Meta:
        model (Profile): The model that this form is associated with.
        fields (tuple): The fields to include in the form.
        widgets (dict): Custom widgets for the form fields.
        labels (dict): Custom labels for the form fields.

    Methods:
        save(commit=True): Saves the profile instance,
                        handling image upload to Cloudinary.
    """
    location = forms.CharField(required=False)
    bio = forms.CharField(
        widget=SummernoteWidget, required=False
    )

    class Meta:
        """
        Meta options for the ProfileForm.

        Attributes:
            model (Profile): The model that this form is associated with.
            fields (tuple): The fields to include in the form.
            widgets (dict): Custom widgets for the form fields.
            labels (dict): Custom labels for the form fields.
        """
        model = Profile
        fields = ('bio', 'user_image', 'location', 'is_private')
        widgets = {
            'bio': SummernoteWidget(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'user_image': forms.FileInput(
                attrs={'class': 'form-control', 'style': 'width:30%;'
                       'display:inline-block;'}),
            'is_private': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
        }
        labels = {
            'bio': 'Bio',
            'location': 'Location',
            'user_image': 'Upload Profile Image',
            'is_private': 'Private Account',
        }

    def save(self, commit=True):
        """
        Saves the profile instance, handling image upload to Cloudinary.

        Args:
            commit (bool): Whether to save the instance to the database.

        Returns:
            Profile: The saved profile instance.
        """
        profile = super().save(commit=False)
        user_image = self.cleaned_data.get('user_image')
        if user_image and isinstance(user_image, InMemoryUploadedFile):
            try:
                upload_result = upload(
                    user_image,
                    resource_type='image',
                    folder='profiles/',
                    allowed_formats=['jpg', 'jpeg', 'png'],
                    transformation={'quality': 'auto:good',
                                    'fetch_format': 'auto'},
                )
                profile.user_image = upload_result['url']
            except Error as e:
                print(f'Error uploading image: {e}')
        if commit:
            profile.save()
        return profile
