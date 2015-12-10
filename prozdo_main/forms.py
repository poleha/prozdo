from django import forms
from . import models
from django.conf import settings
from super_model import forms as super_forms
from super_model import fields as super_fields


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


class DrugFilterForm(super_forms.PostFilterForm):
    class Meta:
        post_type = settings.POST_TYPE_DRUG
    dosage_forms = forms.ModelMultipleChoiceField(queryset=models.DrugDosageForm.objects.all(), label='Форма выпуска', widget=forms.CheckboxSelectMultiple(), required=False)
    usage_areas = forms.ModelMultipleChoiceField(queryset=models.DrugUsageArea.objects.all(), label='Область применения', widget=forms.CheckboxSelectMultiple(), required=False)

class ComponentFilterForm(super_forms.PostFilterForm):
    class Meta:
        post_type = settings.POST_TYPE_COMPONENT
    component_type = forms.MultipleChoiceField(choices=models.COMPONENT_TYPES, label='Тип компонента', widget=forms.CheckboxSelectMultiple(), required=False)

class CosmeticsFilterForm(super_forms.PostFilterForm):
    class Meta:
        post_type = settings.POST_TYPE_COSMETICS
    brand = forms.ModelMultipleChoiceField(queryset=models.Brand.objects.all(), label='Бренд', widget=forms.CheckboxSelectMultiple(), required=False)
    line = forms.ModelMultipleChoiceField(queryset=models.CosmeticsLine.objects.all(), label='Линия', widget=forms.CheckboxSelectMultiple(), required=False)
    usage_areas = forms.ModelMultipleChoiceField(queryset=models.CosmeticsUsageArea.objects.all(), label='Область применения', widget=forms.CheckboxSelectMultiple(), required=False)
    dosage_forms = forms.ModelMultipleChoiceField(queryset=models.CosmeticsDosageForm.objects.all(), label='Форма выпуска', widget=forms.CheckboxSelectMultiple(), required=False)


class DrugForm(forms.ModelForm):
    class Meta:
        model = models.Drug
        exclude = ('post_type', 'old_id', 'created', 'updated', 'published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dosage_forms'].widget = forms.CheckboxSelectMultiple(choices=self.fields['dosage_forms'].widget.choices)
        self.fields['usage_areas'].widget = forms.CheckboxSelectMultiple(choices=self.fields['usage_areas'].widget.choices)
        self.fields['components'].widget = forms.CheckboxSelectMultiple(choices=self.fields['components'].widget.choices)
        self.fields['category'].widget = forms.CheckboxSelectMultiple(choices=self.fields['category'].widget.choices)
        self.fields['image'].widget = super_fields.SuperImageClearableFileInput(thumb_name='thumb110')

class CosmeticsForm(forms.ModelForm):
    class Meta:
        model = models.Cosmetics
        exclude = ('post_type', 'old_id', 'created', 'updated', 'published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dosage_forms'].widget = forms.CheckboxSelectMultiple(choices=self.fields['dosage_forms'].widget.choices)
        self.fields['usage_areas'].widget = forms.CheckboxSelectMultiple(choices=self.fields['usage_areas'].widget.choices)
        self.fields['image'].widget = super_fields.SuperImageClearableFileInput(thumb_name='thumb110')


class BlogForm(forms.ModelForm):
    class Meta:
        model = models.Blog
        exclude = ('post_type', 'old_id', 'created', 'updated', 'published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget = super_fields.SuperImageClearableFileInput(thumb_name='thumb110')
        self.fields['category'].widget = forms.CheckboxSelectMultiple(choices=self.fields['category'].widget.choices)


class ComponentForm(forms.ModelForm):
    class Meta:
        model = models.Component
        exclude = ('post_type', 'old_id', 'created', 'updated', 'published')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['component_type'].widget = forms.CheckboxSelectMultiple(choices=self.fields['component_type'].widget.choices)


class CommentConfirmForm(forms.Form):
    email = forms.EmailField(label='Электронный адрес')
    comment = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=models.Comment.objects.all())

BOOL_CHOICE_DEFAULT = 0
BOOL_CHOICE_NO = 1
BOOL_CHOICE_YES =2


BOOL_CHOICES = (
    (BOOL_CHOICE_DEFAULT, 'Не выбрано'),
    (BOOL_CHOICE_YES, 'Да'),
    (BOOL_CHOICE_NO, 'Нет'),
)

class CommentDoctorListFilterForm(forms.Form):
    consult_required = forms.ChoiceField(label='Нужна консультация', required=False, choices=BOOL_CHOICES)
    consult_done = forms.ChoiceField(label='Консультация оказана', required=False, choices=BOOL_CHOICES)
    start_date = forms.DateField(label='Дата начала', required=False, widget=forms.DateInput(attrs={'class':'date-input'}))
    end_date = forms.DateField(label='Дата окончания', required=False, widget=forms.DateInput(attrs={'class':'date-input'}))
    consult_only = forms.BooleanField(label='Только консультации', required=False)


