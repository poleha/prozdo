from django.core.management.base import BaseCommand
from prozdo_main import models
import os
from django.conf import settings

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('poll_id', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete images')

    def handle(self, *args, **options):
        count = 0
        for content_type, model in (('blog', models.Blog), ('drug', models.Drug), ('cosmetics', models.Cosmetics), ('user_profile', models.UserProfile)):

            dir = os.path.join(settings.MEDIA_ROOT, content_type)
            for fn in os.listdir(dir):
                file_name = content_type + '/' + fn
                exist = model.objects.filter(image=file_name)
                if not exist:
                    print('deleted', fn)
                    if options['delete']:
                        os.remove(os.path.join(dir, fn))

            ms = model.objects.all()
            for m in ms:
                image_name = os.path.join(settings.MEDIA_ROOT, str(m.image))
                exists = os.path.exists(image_name)
                if not exists:
                    count += 1
                    print('not_found', m, m.pk)

        print(count)