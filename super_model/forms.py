from django import forms
from django.utils.html import conditional_escape
from haystack.forms import SearchForm

class SuperImageClearableFileInput(forms.ClearableFileInput):
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


class SuperSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['placeholder'] = 'Поиск по сайту'
        self.fields['q'].widget.attrs['autocomplete'] = 'Off'

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super().search()

        return sqs