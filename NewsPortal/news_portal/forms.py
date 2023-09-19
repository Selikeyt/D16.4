from django import forms
from django.core.exceptions import ValidationError
from .models import Post

class NewsForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'title',
            'post_text',
            'category',
            'author',
         ]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        post_text = cleaned_data.get('post_text')

        if title == post_text:
            raise ValidationError(
                "Название не должно быть идентично тексту"
            )
        return cleaned_data

