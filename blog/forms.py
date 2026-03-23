"""
blog/forms.py
"""
from django import forms
from .models import Post


class PostEditorForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'excerpt', 'categories', 'body', 'cover_image',
            'key_takeaways', 'status', 'is_featured', 'published_at',
        ]
        widgets = {
            'body': forms.HiddenInput(),
            'title': forms.TextInput(attrs={'placeholder': 'Post title...'}),
            'excerpt': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Brief description shown in the article list…',
            }),
            'key_takeaways': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'One takeaway per line…',
            }),
            'categories': forms.CheckboxSelectMultiple(),
            'cover_image': forms.FileInput(attrs={'accept': 'image/*'}),
            'status': forms.Select(),
            'published_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow body to be empty from POST — JS always sets it before submit,
        # but we validate it in clean() only when there is actual content.
        self.fields['body'].required = False
        # Format published_at for datetime-local input
        if self.instance and self.instance.published_at:
            self.initial['published_at'] = self.instance.published_at.strftime(
                '%Y-%m-%dT%H:%M'
            )

    def clean_body(self):
        body = self.cleaned_data.get('body', '').strip()
        # Only require body content when publishing
        status = self.data.get('status', 'draft')
        if status == 'published' and not body:
            raise forms.ValidationError(
                'Post body cannot be empty when publishing.'
            )
        return body
