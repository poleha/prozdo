#!/usr/bin/env python
import os
import sys
from django.utils import timezone
from datetime import date
from random import choice

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prozdo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from prozdo_main import models

"""
components = []
drug_dosage_forms = []
drug_usage_areas = []

models.Component.objects.all().delete()
models.DrugDosageForm.objects.all().delete()
models.DrugUsageArea.objects.all().delete()
models.Drug.objects.all().delete()

for n in range(10):


    component = models.Component.objects.create(
        body='body' + str(n),
        title = 'title_component' + str(n)
    )
    components.append(component)

    drug_dosage_form = models.DrugDosageForm.objects.create(
        title = 'title_drug_dosage_form' + str(n)
    )
    drug_dosage_forms.append(drug_dosage_form)

    drug_usage_area = models.DrugUsageArea.objects.create(
        title = 'title_drug_usage_area' + str(n)
    )
    drug_usage_areas.append(drug_usage_area)

    drug = models.Drug.objects.create(
        title='title_drug' + str(n),
        body='body' + str(n),

    )



from copy import deepcopy
d = models.Drug.objects.get(pk=8)

for i in range(15):
    d.title = 'Тестовый препарат к {0}'.format(str(i))
    d.alias = None
    d.pk = None
    d.id = None
    d.save()

"""

#for c in models.Comment.objects.all():
#    print(c.level)

#from django.utils.html import remove_tags

#txt = '<a href="www.aaa.ru">aaa</a><br><img></img>'

#print(remove_tags(txt, 'p img br'))

#u = models.User.objects.get(email='a.polekha@gmail.com')
#pu = models.ProzdoUser.objects.get(pk=u.pk)
#print(pu.cached_user_profile)
#pu.save()

from django.core import serializers

data = '[{"model": "socialaccount.socialapp", "pk": 1, "fields": {"sites": [], "client_id": "771139626663-800skijd1dkjem43dm66p2ltqvvjli34.apps.googleusercontent.com", "key": "", "name": "Google", "provider": "google", "secret": "lQrQkLZPFmFLi69oh32FBxzI"}}, {"model": "socialaccount.socialapp", "pk": 2, "fields": {"sites": [], "client_id": "5105342", "key": "", "name": "VK", "provider": "vk", "secret": "LA6KHXiHlwCaXsjVdIns"}}, {"model": "socialaccount.socialapp", "pk": 3, "fields": {"sites": [], "client_id": "1512092622435264", "key": "", "name": "Facebook", "provider": "facebook", "secret": "2fea43726ed1e66b116c6d84c3d1f7a8"}}]'

elems = serializers.deserialize("json", data)

for elem in elems:
    elem.save()


data = '[{"model": "sites.site", "pk": 1, "fields": {"domain": "prozdo.ru", "name": "prozdo.ru"}}]'

elems = serializers.deserialize("json", data)

for elem in elems:
    elem.save()