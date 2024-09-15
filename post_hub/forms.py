from django import forms
from mptt.forms import TreeNodeChoiceField
from .models import Comment

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