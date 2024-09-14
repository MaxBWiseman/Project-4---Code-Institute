from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Leave a comment here'}),
            'parent': forms.HiddenInput(),
        }
        labels = {
            'content': 'Comment',
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Leave a reply here'}),
        }
        labels = {
            'content': 'Reply',
        }