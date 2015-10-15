from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import User
from django.core.exceptions import ValidationError
from .forms import validate_contains_russian, validate_first_is_letter, validate_username
from django.conf import settings


#I could do it with a signal, but it looks more convenient to store apapter here
class ProzdoSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if not request.user.is_authenticated():
            email_adress = None
            for email in sociallogin.email_addresses:
                if email.verified:
                    email_adress = email.email
                    break
            if email_adress:
                try:
                    user = User.objects.get(email=email_adress)
                    sociallogin.connect(request, user)
                except:
                    pass
        super().pre_social_login(request, sociallogin)


    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        name = data.get('name')

        user.username = None
        for username_variant in (name, first_name, last_name, "{0}-{1}".format(first_name, last_name), username):
            if self.username_valid(username_variant):
                user.username = username_variant
                break

        if not user.username:
            user.username = 'social-auth-user'



    @staticmethod
    def username_valid(username):
        if username:
            min_length_ok = len(username) > settings.ACCOUNT_USERNAME_MIN_LENGTH
            exists = User.objects.filter(username=username).exists()

            for validator in (validate_contains_russian, validate_first_is_letter, validate_username):
                try:
                    validator(username)
                except ValidationError:
                    return False

            if min_length_ok and not exists:
                return True
            else:
                return False
        else:
            return False


