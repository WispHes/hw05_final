from django import forms

from .models import Post, Comment


class BaseForm(forms.ModelForm):
    def __init__(self, *args, is_edit=False, **kwargs):
        super(). __init__(*args, **kwargs)
        self.is_edit = is_edit


class PostForm(BaseForm):
    def __init__(self, *args, is_edit=False, **kwargs):
        super(). __init__(*args, **kwargs)
        if is_edit:
            self.fields['text'].help_text = 'Текст редактируемого поста'

    class Meta():
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
