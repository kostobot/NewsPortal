from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    required_css_class = 'my-custom-class'
    title = forms.CharField(max_length=500)
    url_img = forms.URLField(max_length=500)

    class Meta:
        model = Post
        fields = ['title', 'author', 'category', 'text', 'url_img']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': "form-control"})
        self.fields['title'].label = "Заголовок публикации"
        self.fields['title'].widget.attrs.update({'placeholder': "Введите название"})
        self.fields['text'].label = "Текст публикации"
        self.fields['text'].widget.attrs.update({'placeholder': "Введите текст здесь"})
        self.fields['url_img'].label = "Ссылка на картинку"
        self.fields['url_img'].widget.attrs.update({'placeholder': "Пример: https://cdn.fishki.net/upload/post/201603/19/1889496/1_bezymjannyj5.jpg"})

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        text = cleaned_data.get("text")

        if title == text:
            raise ValidationError(
                "Текст статьи не должен быть идентичен заголовку."
            )
        return cleaned_data