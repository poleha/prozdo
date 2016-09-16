import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prozdo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)



from main import models
from super_model import models as super_models
import requests
import time
from django.conf import settings
from django.core.mail import mail_admins
from cache.decorators import construct_cached_view_key
from django.core.cache import cache
from main.views import PostDetail
from main.models import Post

def handle(**options):
    count = 0
    errors = []
    urls_len = models.Post.objects.filter(status=super_models.POST_STATUS_PUBLISHED).count()
    posts = list(models.Post.objects.filter(status=super_models.POST_STATUS_PUBLISHED))
    #shuffle(posts)
    for post in posts:
        if not (post.is_blog or post.is_drug or post.is_component or post.is_cosmetics):
            continue
        count += 1
        absolute_url = url = '{}{}'.format(settings.SITE_URL, post.get_absolute_url())
        alias = getattr(post, 'alias', None)
        if alias:
            original_key = construct_cached_view_key(PostDetail.get, url=absolute_url, model_class=Post, kwarg='alias',
                                                     alias=post.alias)
        else:
            original_key = construct_cached_view_key(PostDetail.get, url=absolute_url, model_class=Post, kwarg='pk',
                                                     pk=post.pk)
        mobile_key = original_key.replace('flavour_None', 'flavour_mobile')
        full_key = original_key.replace('flavour_None', 'flavour_full')
        for key in (full_key, mobile_key, original_key):
            resp = cache.get(key)
            if resp is None or options['full']:
                headers = {}
                if key == mobile_key:
                    headers['user-agent'] = 'mobile'
                try:
                    res = requests.get(absolute_url, headers=headers)
                    if res.status_code != 200:
                        errors.append('{0}-{1}'.format(url, res.status_code))

                    if options['show']:
                        print(
                            'Visited url {}, {} of {}. Response code: {}'.format(absolute_url, count, urls_len,
                                                                                 res.status_code))
                except:
                    errors.append('{0}-{1}'.format(url, 'EXCEPTION'))


options = {
    'show': True,
    'full': False,
    'sleep_time': 0.1,


}
handle(**options)

