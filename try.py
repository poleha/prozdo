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

h = models.History.objects.latest('created')
pk = h.pk
h.delete()


h1 = models.History.objects.get(pk=pk)
print(h1.pk == pk)