from django import forms
from . import models
import re, os
from django.forms import ValidationError
from allauth.account.forms import SignupForm
from django.utils.html import conditional_escape, format_html
from django.utils.translation import ugettext_lazy
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from multi_image_upload.models import save_thumbs


class CommentForm(forms.ModelForm):
    required_css_class = 'required'
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



class CommentUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('body', )

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




class ProzdoImageClearableFileInput(forms.ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s: <img src="%(initial_url)s"> '
        '%(clear_template)s<br />%(input_text)s: %(input)s'
    )

    def get_template_substitution_values(self, value):
        """
        Return value-related substitutions.
        """
        return {
            'initial': conditional_escape(value),
            'initial_url': conditional_escape(getattr(value.instance, self._thumb_name)),
        }


    def __init__(self, thumb_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thumb_name = thumb_name



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




"""
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ('image',)
"""

class ProzdoSignupForm(SignupForm):
    required_css_class = 'required'
    image = forms.ImageField(label='Изображение', required=False)
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



#alphabet = (('а', 'а'), )


class PostFilterForm(forms.Form):
    alphabet = forms.MultipleChoiceField(choices=(), label='По первой букве', required=False, widget=forms.CheckboxSelectMultiple())
    title = forms.CharField(label='Название', required=False)

    def __init__(self, *args, **kwargs):
        from string import digits, ascii_lowercase
        super().__init__(*args, **kwargs)
        if isinstance(self, DrugFilterForm):
            post_type = models.POST_TYPE_DRUG
            #url = models.Drug.get_list_url()
        elif isinstance(self, CosmeticsFilterForm):
            post_type = models.POST_TYPE_COSMETICS
            #url = models.Cosmetics.get_list_url()
        elif isinstance(self, ComponentFilterForm):
            post_type = models.POST_TYPE_COMPONENT
            #url = models.Component.get_list_url()
        alph = ()
        letters = digits + ascii_lowercase + 'абвгдеёжзийклмнопрстуфхцчшщъыбэюя'
        for letter in letters:
            posts = models.Post.objects.filter(post_type=post_type, title__istartswith=letter)
            count = posts.count()
            if count > 0:
                alph += ((letter, '{0}({1})'.format(letter, count)), )
        self.fields['alphabet'] = forms.MultipleChoiceField(choices=alph, label='По первой букве', required=False, widget=forms.CheckboxSelectMultiple())


class DrugFilterForm(PostFilterForm):
    dosage_forms = forms.ModelMultipleChoiceField(queryset=models.DrugDosageForm.objects.all(), label='Форма выпуска', widget=forms.CheckboxSelectMultiple(), required=False)
    usage_areas = forms.ModelMultipleChoiceField(queryset=models.DrugUsageArea.objects.all(), label='Область применения', widget=forms.CheckboxSelectMultiple(), required=False)

class ComponentFilterForm(PostFilterForm):
    component_type = forms.MultipleChoiceField(choices=models.COMPONENT_TYPES, label='Тип компонента', widget=forms.CheckboxSelectMultiple(), required=False)

class CosmeticsFilterForm(PostFilterForm):
    brands = forms.ModelMultipleChoiceField(queryset=models.Brand.objects.all(), label='Бренд', widget=forms.CheckboxSelectMultiple(), required=False)
    lines = forms.ModelMultipleChoiceField(queryset=models.CosmeticsLine.objects.all(), label='Линия', widget=forms.CheckboxSelectMultiple(), required=False)
    usage_areas = forms.ModelMultipleChoiceField(queryset=models.CosmeticsUsageArea.objects.all(), label='Область применения', widget=forms.CheckboxSelectMultiple(), required=False)
    dosage_forms = forms.ModelMultipleChoiceField(queryset=models.CosmeticsDosageForm.objects.all(), label='Форма выпуска', widget=forms.CheckboxSelectMultiple(), required=False)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        exclude = ('role', 'user' )

    image = forms.ImageField(label='Изображение', widget=ProzdoImageClearableFileInput(thumb_name='thumb100'), required=False)

class DrugForm(forms.ModelForm):
    class Meta:
        model = models.Drug
        exclude = ('post_type', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dosage_forms'].widget = forms.CheckboxSelectMultiple(choices=self.fields['dosage_forms'].widget.choices)
        self.fields['usage_areas'].widget = forms.CheckboxSelectMultiple(choices=self.fields['usage_areas'].widget.choices)
        self.fields['components'].widget = forms.CheckboxSelectMultiple(choices=self.fields['components'].widget.choices)
        self.fields['category'].widget = forms.CheckboxSelectMultiple(choices=self.fields['category'].widget.choices)
        self.fields['image'].widget = ProzdoImageClearableFileInput(thumb_name='thumb110')

class CosmeticsForm(forms.ModelForm):
    class Meta:
        model = models.Cosmetics
        exclude = ('post_type', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dosage_forms'].widget = forms.CheckboxSelectMultiple(choices=self.fields['dosage_forms'].widget.choices)
        self.fields['usage_areas'].widget = forms.CheckboxSelectMultiple(choices=self.fields['usage_areas'].widget.choices)
        self.fields['image'].widget = ProzdoImageClearableFileInput(thumb_name='thumb110')


class BlogForm(forms.ModelForm):
    class Meta:
        model = models.Blog
        exclude = ('post_type', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget = ProzdoImageClearableFileInput(thumb_name='thumb110')
        self.fields['category'].widget = forms.CheckboxSelectMultiple(choices=self.fields['category'].widget.choices)


class ComponentForm(forms.ModelForm):
    class Meta:
        model = models.Component
        exclude = ('post_type', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['component_type'].widget = forms.CheckboxSelectMultiple(choices=self.fields['component_type'].widget.choices)
