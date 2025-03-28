from django import forms
from django.core.exceptions import ValidationError
from recipes.models import Category, Recipes


class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='Категория не выбрана', label='Категории')

    class Meta:
        model = Recipes
        fields = ['title', 'content', 'photo', 'is_published', 'cat', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        labels = {'slug': 'URL'}


    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise ValidationError("Длина превышает 20 символов")

        return title

class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Файл")


class PostFilterForm(forms.Form):
    order = forms.ChoiceField(
        choices=[
            ('with_photo', 'с фото'),
            ('without_photo', 'без фото'),
            ('new', 'новые'),
            ('old', 'старые')
        ],
        label='Сортировка',
        required=False
    )

