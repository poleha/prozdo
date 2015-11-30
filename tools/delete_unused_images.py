#!/var/www/prozdo/venv/bin
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prozdo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from prozdo_main import models


import os
from django.conf import settings
count = 0
for content_type, model in (('blog', models.Blog), ('drug', models.Drug), ('cosmetics', models.Cosmetics), ('user_profile', models.UserProfile)):

    dir = os.path.join(settings.MEDIA_ROOT, content_type)
    for fn in os.listdir(dir):
        file_name = content_type + '/' + fn
        exist = model.objects.filter(image=file_name)
        if not exist:
            print('deleted', fn)
            os.remove(os.path.join(dir, fn))
            #pass

    ms = model.objects.all()
    for m in ms:
        image_name = os.path.join(settings.MEDIA_ROOT, str(m.image))
        exists = os.path.exists(image_name)
        if not exists:
            count += 1
            print('not_found', m, m.pk)

print(count)



