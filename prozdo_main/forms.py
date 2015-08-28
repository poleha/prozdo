from django import forms
from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('username', 'email', 'body','post_mark', 'consult_required', 'parent' )

    def __init__(self, *args, user=None, post=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['parent'].queryset = post.comments.all()

        if user.is_authenticated():
            self.fields['username'].widget = forms.HiddenInput()
            self.fields['username'].initial = user.username
            self.fields['email'].widget = forms.HiddenInput()
            self.fields['email'].initial = user.email



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