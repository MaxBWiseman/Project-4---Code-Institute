from django import forms
from mptt.forms import TreeNodeChoiceField
from .models import Comment, Post

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
    class Meta:
        model = Post
        fields = ('title', 'blurb', 'banner_image', 'content', 'category', 'new_category')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'blurb': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 40}),
            'banner_image': forms.FileInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }