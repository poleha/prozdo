import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prozdo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)



from main import models
from super_model import models as super_models
import requests
from django.core.urlresolvers import reverse
import time
from django.conf import settings
from django.core.mail import mail_admins
from cache.decorators import construct_cached_view_key
from django.core.cache import cache
from main.views import PostDetail


def handle(**options):
    count = 0

    urls = tuple()
    urls += (reverse('blog-list'),)
    urls += (reverse('component-list'),)
    urls += (reverse('drug-list'),)
    urls += (reverse('cosmetics-list'),)
    urls += (reverse('main-page'),)
    urls += ('/sitemap.xml',)


    errors = []

    urls_len = len(urls) + models.Post.objects.filter(status=super_models.POST_STATUS_PUBLISHED).count()

    for url in urls:
        count += 1
        absolute_url = '{}{}'.format(settings.SITE_URL, url)
        try:
            res = requests.get(absolute_url)
            if not res.status_code == 200:
                errors.append('{0}-{1}'.format(url, res.status_code))
            if not options['no_sleep']:
                time.sleep(0.5)
            if options['show']:
                print('Visited url {}, {} of {}. Response code: {}'.format(absolute_url, count, urls_len, res.status_code))
        except:
            errors.append('{0}-{1}'.format(url, 'EXCEPTION'))

    for post in models.Post.objects.filter(status=super_models.POST_STATUS_PUBLISHED):
        if not(post.is_blog or post.is_drug or post.is_component or post.is_cosmetics):
            continue
        count += 1
        absolute_url = url='{}{}'.format(settings.SITE_URL, post.get_absolute_url())
        key = construct_cached_view_key(PostDetail.get, url=absolute_url)
        mobile_key = key.replace('flavour_None', 'flavour_mobile')
        full_key = key.replace('flavour_None', 'flavour_full')
        for key in (full_key, mobile_key):
            resp = cache.get(key)
            if resp is None or options['full']:
                headers = {}
                if key == mobile_key:
                    headers['user-agent'] = 'mobile'
                try:
                    res = requests.get(absolute_url, headers=headers)
                    if res.status_code != 200:
                        errors.append('{0}-{1}'.format(url, res.status_code))

                    if not options['no_sleep']:
                        time.sleep(0.5)
                    if options['show']:
                        print('Visited url {}, {} of {}. Response code: {}'.format(absolute_url, count, urls_len, res.status_code))
                except:
                    errors.append('{0}-{1}'.format(url, 'EXCEPTION'))

    if len(errors) > 0:
        mail_admins('Errors during crawling', '\n'.join(errors))

options = {
    'show': False,
    'no_sleep': False,
    'full': False
}
handle(**options)