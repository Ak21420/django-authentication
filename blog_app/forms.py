from django import forms
from .models import Post, Comment
from django.core.exceptions import ValidationError

class PostForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['image_link'].required = False
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'image_link']

        widgets = {
            'content': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        image_link = cleaned_data.get("image_link")

        if image and image_link:
            raise ValidationError("Only one field can be fill at a time.")
        elif not image and not image_link:
            raise ValidationError("Fill a Image link or upload a Image/Gif/Video")

class PostDeleteForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['delete_status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text')