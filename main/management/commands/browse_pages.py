from django.core.management.base import BaseCommand
from main import models
from super_model import models as super_models
from urllib.request import urlopen
from django.core.urlresolvers import reverse
import time
from django.utils import timezone
from django.core.mail import mail_admins

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('poll_id', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument('--full',
            action='store_true',
            dest='full',
            default=False,
            help='Browse all pages')


    def handle(self, *args, **options):
        count = 0

        urls = tuple()
        urls += (reverse('blog-list'),)
        urls += (reverse('component-list'),)
        urls += (reverse('drug-list'),)
        urls += (reverse('cosmetics-list'),)
        urls += (reverse('main-page'),)
        urls += ('/sitemap.xml',)


        post_urls = ()
        for post in models.Post.objects.filter(status=super_models.POST_STATUS_PUBLISHED):
            if post.is_blog or post.is_drug or post.is_component or post.is_cosmetics:
                if not options['full'] and post.last_modified < (timezone.now() - timezone.timedelta(seconds=60 * 35)):
                    continue
                post_urls += (post.get_absolute_url(), )

        urls += tuple(post_urls)
        errors = []

        for url in urls:
            count += 1
            absolute_url = 'http://prozdo.ru{0}'.format(url)
            res = urlopen(absolute_url)
            if not res.code == 200:
                errors.append('{0}-{1}'.format(url, res.code))
            time.sleep(1)

        if len(errors) > 0:
            mail_admins('Errors during crawling', '\n'.join(errors))