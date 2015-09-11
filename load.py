#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prozdo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from prozdo_main import models
import sqlite3
from allauth.account.models import EmailAddress, EmailConfirmation
import datetime


def date_from_timestamp(ts):
    if not ts:
        return None
    else:
        return datetime.datetime.fromtimestamp(ts)


models.Post.objects.all().delete()
#models.User.objects.all().exclude(username='kulik').delete()
#EmailAddress.objects.all().delete()
#EmailConfirmation.objects.all().delete()

conn = sqlite3.connect('prozdo.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()


user_rows = c.execute('SELECT * FROM users u LEFT JOIN profiles p ON u.id = p.user_id ').fetchall()
for user_row in user_rows:
    user, created = models.User.objects.get_or_create(
    username=user_row['username'],
    password=user_row['password'],
    email=user_row['email'],
    is_staff=False,
    )

    user_profile = user.user_profile
    if user_row['role'] == 1:
        role = models.USER_ROLE_REGULAR
    elif user_row['role'] == 2:
        role = models.USER_ROLE_ADMIN
    elif user_row['role'] == 3:
        role = models.USER_ROLE_AUTHOR
    elif user_row['role'] == 4:
        role = models.USER_ROLE_DOCTOR
    else:
        role = models.USER_ROLE_REGULAR
    user_profile.role = role
    user_profile.receive_messages = user_row['recive_message_own_reply']
    user_profile.first_name = user_row['firstname']
    user_profile.last_name = user_row['lastname']
    user_profile.save()
    #if user_row['status'] == 1:
    email_adress, created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        verified=True if user_row['status'] == 1 else False,
        primary=True,
    )
    if email_adress.verified:
        if not EmailConfirmation.objects.filter(email_address=email_adress).exists():
            email_confirmation = EmailConfirmation.create(email_adress)




drugs = []
components = []
cosmeticss = []
blogs = []
categories = []
brands = []
lines = []
drug_dosage_forms = []
cosmetics_usage_areas = []
drug_usage_areas = []
cosmetics_dosage_forms = []

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type > 3 AND p.type < 8').fetchall()
for post_row in post_rows:
    params = (post_row['id'], )
    alias_row = c.execute('SELECT * FROM alias a WHERE a.entity_id = ?', params).fetchone()
    try:
        alias = alias_row['alias']
    except:
        alias = ''

    if post_row['type'] == 4:
        component_type = models.COMPONENT_TYPE_VITAMIN
    elif post_row['type'] == 5:
        component_type = models.COMPONENT_TYPE_MINERAL
    elif post_row['type'] == 6:
        component_type = models.COMPONENT_TYPE_PLANT
    elif post_row['type'] == 7:
        component_type = models.COMPONENT_TYPE_OTHER

    component, created = models.Component.objects.get_or_create(
        title=post_row['title'],
        body=post_row['content'],
        alias=alias,
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        component_type=component_type,
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        components.append(component)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 8').fetchall()
for post_row in post_rows:
    drug_dosage_form, created = models.DrugDosageForm.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        drug_dosage_forms.append(drug_dosage_form)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 9').fetchall()
for post_row in post_rows:
    drug_usage_area, created = models.DrugUsageArea.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        drug_usage_areas.append(drug_usage_area)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 12').fetchall()
for post_row in post_rows:
    category, created = models.Category.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        categories.append(category)

        if post_row['parent_id']:
            parent_category_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
            parent_category, created = models.Category.objects.get_or_create(
            title=parent_category_row['title'],
            created=date_from_timestamp(parent_category_row['create_time']),
            edited=date_from_timestamp(parent_category_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if parent_category_row['status'] == 2 else models.POST_STATUS_PROJECT,
        )
            category.parent = parent_category
            category.save()
            if created:
                categories.append(parent_category_row)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 14').fetchall()
for post_row in post_rows:
    cosmetics_dosage_form, created = models.CosmeticsDosageForm.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        cosmetics_dosage_forms.append(cosmetics_dosage_form)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 15').fetchall()
for post_row in post_rows:
    cosmetics_usage_area, created = models.CosmeticsUsageArea.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        cosmetics_usage_areas.append(cosmetics_usage_area)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 16').fetchall()
for post_row in post_rows:
    line, created = models.CosmeticsLine.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        lines.append(line)

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 17').fetchall()
for post_row in post_rows:
    brand, created = models.Brand.objects.get_or_create(
    title=post_row['title'],
    created=date_from_timestamp(post_row['create_time']),
    edited=date_from_timestamp(post_row['create_time']),
    status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    if created:
        brands.append(brand)


post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 1').fetchall()
for post_row in post_rows:
    params = (post_row['id'], )
    alias_row = c.execute('SELECT * FROM alias a WHERE a.entity_id = ?', params).fetchone()
    try:
        alias = alias_row['alias']
    except:
        alias = ''
    drug, created = models.Drug.objects.get_or_create(
        title=post_row['title'],
        body=post_row['content'],
        alias=alias,
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['create_time']),
        indications=post_row['pokaz'],
        features=post_row['osob'],
        application_scheme=post_row['priem'],
        dosage_form=post_row['form_vip_text'],
        contra_indications=post_row['prot'],
        side_effects=post_row['side_effects'],
        compound=post_row['sostav'],
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    params = (post_row['id'], )
    relation_rows = c.execute('SELECT p1.id, p1.title, r.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
    for relation_row in relation_rows:
        params = (relation_row['id'], )
        related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
        if relation_row['type'] == 1:
            related = models.Component.objects.get(title=related_post_row['title'])
            drug.components.add(related)
        elif relation_row['type'] == 2:
            related = models.DrugUsageArea.objects.get(title=related_post_row['title'])
            drug.usage_areas.add(related)
        elif relation_row['type'] == 3:
            related = models.DrugDosageForm.objects.get(title=related_post_row['title'])
            drug.dosage_forms.add(related)
        elif relation_row['type'] == 5:
            related = models.Category.objects.get(title=related_post_row['title'])
            drug.category.add(related)
    drugs.append(drug)
        

