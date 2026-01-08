from django import forms
from .models import Post, Comment, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Явно указываем все нужные поля вместо exclude
        fields = [
            'title',
            'text',
            'category',
            'location',
            'pub_date',
            'is_published',
            'image'
        ]
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }
        help_texts = {
            'is_published': 'Отметьте, чтобы опубликовать пост',
        }

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text='Загрузите изображение (JPG, PNG, GIF)'
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')