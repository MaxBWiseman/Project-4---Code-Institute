from django import forms
from mptt.forms import TreeNodeChoiceField
from .models import Comment, Post, Category
from spellchecker import SpellChecker

class CommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].widget.attrs.update({'class': 'd-none'})
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Comment
        fields = ('parent', 'content')  # Only include the fields you want to display in the form

        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, *args, **kwargs):
        Comment.objects.rebuild()
        return super(CommentForm, self).save(*args, **kwargs)
    
class PostForm(forms.ModelForm):
    new_category = forms.CharField(required=False, max_length=100, label='New Category')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Post
        fields = ('title', 'blurb', 'banner_image', 'content', 'category', 'new_category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'blurb': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 40}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
        
    def clean_new_category(self):
        new_category_name = self.cleaned_data.get('new_category')
        if new_category_name:
            existing_categories = Category.objects.filter(category_name=new_category_name)
            if existing_categories.count() >= 2:
                raise forms.ValidationError('There cannot be more than 2 categories with the same name.')
            
            spell = SpellChecker()
# I reasearched a way to spell check my categories and came across the spellchecker library.
# First, I imported the SpellChecker class from the spellchecker module.
# Then, I created a SpellChecker object called spell.
            misspelled = spell.unknown([new_category_name])
# I used the unknown method to check if the category name is misspelled.
            if misspelled:
                corrected = spell.correction(new_category_name)
# If the category name is misspelled, I used the correction method to get the correct spelling.
                raise forms.ValidationError(f"Did you mean '{corrected}'?")
# I raised a ValidationError with a message that suggests the correct spelling.
        return new_category_name