from django import forms
from . import models
from django.conf import settings
from super_model import forms as super_forms
from super_model import fields as super_fields


class CommentForm(super_forms.SuperCommentForm):
    class Meta:
        model = models.Comment
        fields = ('username', 'email', 'body','post_mark', 'consult_required', 'parent' )

    def __init__(self, *args, request=None, post=None, **kwargs):
        super().__init__(*args, request=request, post=post, **kwargs)
        user = request.user

        if not user.is_regular:
            del self.fields['consult_required']

        if post.get_mark_by_request(request):
            del self.fields['post_mark']


class CommentUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('body', )

class CommentOptionsForm(super_forms.SuperCommentOptionsForm):
        show_type_label = 'Вид показа отзывов'


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
    brand = forms.ModelMultipleChoiceField(queryset=models.BrandModel.objects.all(), label='Бренд', widget=forms.CheckboxSelectMultiple(), required=False)
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


