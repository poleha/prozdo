from django import forms
from haystack.forms import SearchForm
from allauth.account.forms import SignupForm
from . import fields
from django.contrib.auth.models import User
from django.utils.module_loading import import_string
from .app_settings import settings

UserProfile = import_string(settings.BASE_USER_PROFILE_CLASS)


class SuperSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['placeholder'] = 'Поиск по сайту'
        self.fields['q'].widget.attrs['autocomplete'] = 'Off'

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super().search()

        return sqs

class SuperSignupForm(SignupForm):
    required_css_class = 'required'
    image = forms.ImageField(label='Изображение', required=False)
    username = fields.UserNameField()

    def save(self, request, *args, **kwargs):
        user = super().save(request, *args, **kwargs)
        if 'image' in self.cleaned_data:
            user_profile = user.user_profile
            user_profile.image = self.cleaned_data['image']
            user_profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('image', 'receive_messages')

    image = forms.ImageField(label='Изображение', widget=fields.SuperImageClearableFileInput(thumb_name='thumb100'), required=False)


class UserForm(forms.ModelForm):
    username = fields.UserNameField()
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')
