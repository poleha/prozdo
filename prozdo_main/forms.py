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

