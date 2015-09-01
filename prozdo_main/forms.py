from django import forms
from . import models
import re, os
from django.forms import ValidationError
from allauth.account.forms import SignupForm
from django.utils.html import conditional_escape, format_html
from django.utils.translation import ugettext_lazy
from django.conf import settings
from django.core.files.storage import FileSystemStorage

class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('username', 'email', 'body','post_mark', 'consult_required', 'parent' )

    def __init__(self, *args, request=None, post=None, **kwargs):
        super().__init__(*args, **kwargs)
        user = request.user
        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['parent'].queryset = post.comments.all()

        if user.is_authenticated():
            self.fields['username'].widget = forms.HiddenInput()
            self.fields['username'].initial = user.username
            self.fields['email'].widget = forms.HiddenInput()
            self.fields['email'].initial = user.email

        if not user.is_regular:
            del self.fields['consult_required']

        if post.get_mark_by_request(request):
            del self.fields['post_mark']




COMMENTS_ORDER_BY_CREATED_DEC = 1
COMMENTS_ORDER_BY_CREATED_INC = 2


COMMENTS_ORDER_BY_CREATED_CHOICES = (
    (COMMENTS_ORDER_BY_CREATED_DEC, 'Последние отзывы сверху'),
    (COMMENTS_ORDER_BY_CREATED_INC, 'Последние отзывы снизу'),

)

COMMENTS_SHOW_TYPE_PLAIN = 1
COMMENTS_SHOW_TYPE_TREE = 2

COMMENTS_SHOW_TYPE_CHOICES = (
    (COMMENTS_SHOW_TYPE_PLAIN, 'Простой'),
    (COMMENTS_SHOW_TYPE_TREE, 'Деревом'),
)


class CommentsOptionsForm(forms.Form):
    order_by_created = forms.ChoiceField(choices=COMMENTS_ORDER_BY_CREATED_CHOICES, initial=COMMENTS_ORDER_BY_CREATED_DEC, label='Упорядочить по дате добавления', required=False)
    show_type= forms.ChoiceField(choices=COMMENTS_SHOW_TYPE_CHOICES, label='Вид показа отзывов', initial=COMMENTS_SHOW_TYPE_PLAIN, required=False)




class KulikImageClearableFileInput(forms.FileInput):
    initial_text = ''
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')

    template_with_initial = '<div class="image-initial-block">%(initial)s </div> <div class="image-input-block">%(clear_template)s<label class="image-input-label">%(input_text)s:</label> %(input)s</div>'

    #template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    url_markup_template = '<img src="{0}" id="{1}">' #1191

    def __init__(self, thumb_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thumb_name = thumb_name

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': '', #self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super().render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html(self.url_markup_template, getattr(value, self._thumb_name), name + '-image') #1191
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = forms.CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return forms.widgets.mark_safe(template % substitutions)


def validate_first_is_letter(value):
    if re.search('^[a-zA-Z0-9]+', value) is None:
        raise ValidationError('Имя пользователя должно начинаться с английской буквы или цифры')

def validate_contains_russian(value):
    if re.search('[а-яА-Я]+', value) is not None:
        raise ValidationError('Имя пользователя содержит русские буквы. Допустимо использовать только английские')

def validate_username(value):
    if re.fullmatch('^[a-zA-Z0-9-_\.]*$', value) is None:
        raise ValidationError('Ошибка в имени пользователя.'
                              ' Допустимо использовать только английские буквы, цифры и символы -  _  .')



from multi_image_upload.models import save_thumbs
"""
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ('image',)
"""

class ProzdoSignupForm(SignupForm):
    required_css_class = 'required'
    image = forms.ImageField(label='Изображение', widget=KulikImageClearableFileInput(thumb_name='thumb100', attrs={'class': 'image-input'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].validators.append(validate_first_is_letter)
        self.fields['username'].validators.append(validate_contains_russian)
        self.fields['username'].validators.append(validate_username)

    def save(self, request, *args, **kwargs):
        user = super().save(request, *args, **kwargs)
        if 'image' in self.cleaned_data:
            user_profile = user.user_profile
            user_profile.image = self.cleaned_data['image']
            user_profile.save()
            save_path = os.path.join(settings.MEDIA_ROOT)
            storage = FileSystemStorage(save_path)
            path = user_profile.image.path
            name = os.path.split(path)[-1]
            save_thumbs(storage, settings.USER_PROFILE_THUMB_SETTINGS, path, 'discount_shop',  name)
        return user

