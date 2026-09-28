from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'preview', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
        