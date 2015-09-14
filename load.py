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
from django.conf import settings
#from django.core.exceptions import MultipleObjectsReturned
from django.utils.timezone import get_default_timezone


tz = get_default_timezone()
def date_from_timestamp(ts):
    if not ts:
        return None
    else:
        return datetime.datetime.fromtimestamp(ts, tz)


#models.Post.objects.all().delete()
#models.User.objects.all().exclude(username='kulik').delete()
#EmailAddress.objects.all().delete()
#EmailConfirmation.objects.all().delete()
#models.Comment.objects.all().delete()



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




posts = {}

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
        edited=date_from_timestamp(post_row['update_time']),
        component_type=component_type,
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    component.old_id = post_row['id']
    posts[post_row['id']] = component

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 8').fetchall()
for post_row in post_rows:
    drug_dosage_form, created = models.DrugDosageForm.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    drug_dosage_form.old_id = post_row['id']
    posts[post_row['id']] = drug_dosage_form

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 9').fetchall()
for post_row in post_rows:
    drug_usage_area, created = models.DrugUsageArea.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    drug_usage_area.old_id = post_row['id']
    posts[post_row['id']] = drug_usage_area

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 12').fetchall()
for post_row in post_rows:
    if post_row['parent_id']:
        parent_category = posts[post_row['parent_id']]
    else:
        parent_category = None
    category, created = models.Category.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
        parent=parent_category,
    )
    category.old_id = post_row['id']
    posts[post_row['id']] = category

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 14').fetchall()
for post_row in post_rows:
    cosmetics_dosage_form, created = models.CosmeticsDosageForm.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    cosmetics_dosage_form.old_id = post_row['id']
    posts[post_row['id']] = cosmetics_dosage_form

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 15').fetchall()
for post_row in post_rows:
    cosmetics_usage_area, created = models.CosmeticsUsageArea.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    cosmetics_usage_area.old_id = post_row['id']
    posts[post_row['id']] = cosmetics_usage_area

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 16').fetchall()
for post_row in post_rows:
    line, created = models.CosmeticsLine.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    line.old_id = post_row['id']
    posts[post_row['id']] = line

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 17').fetchall()
for post_row in post_rows:
    brand, created = models.Brand.objects.get_or_create(
    title=post_row['title'],
    created=date_from_timestamp(post_row['create_time']),
    edited=date_from_timestamp(post_row['update_time']),
    status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    brand.old_id = post_row['id']
    posts[post_row['id']] = brand

post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 1').fetchall()
for post_row in post_rows:
    params = (post_row['id'], )
    alias_row = c.execute('SELECT * FROM alias a WHERE a.entity_id = ?', params).fetchone()
    alias = alias_row['alias']
    drug, created = models.Drug.objects.get_or_create(
        title=post_row['title'],
        body=post_row['content'],
        alias=alias,
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        indications=post_row['pokaz'] if post_row['pokaz'] else '',
        features=post_row['osob'] if post_row['osob'] else '',
        application_scheme=post_row['priem'] if post_row['priem'] else '',
        dosage_form=post_row['form_vip_text'] if post_row['form_vip_text'] else '',
        contra_indications=post_row['prot'] if post_row['prot'] else '',
        side_effects=post_row['side_effects'] if post_row['side_effects'] else '',
        compound=post_row['sostav'] if post_row['sostav'] else '',
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    params = (post_row['id'], )
    relation_rows = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
    for relation_row in relation_rows:
        params = (relation_row['id'], )
        related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
        related = posts[related_post_row['id']]
        if relation_row['type'] in [4, 5, 6, 7]:
            drug.components.add(related)
        elif relation_row['type'] == 9:
            drug.usage_areas.add(related)
        elif relation_row['type'] == 8:
            drug.dosage_forms.add(related)
        elif relation_row['type'] == 12:
            drug.category.add(related)

    posts[post_row['id']] = drug
        
post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 18').fetchall()
for post_row in post_rows:
    params = (post_row['id'], )
    alias_row = c.execute('SELECT * FROM alias a WHERE a.entity_id = ?', params).fetchone()
    alias = alias_row['alias']
    params = (post_row['id'], )
    brand_row = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE p1.type=17 AND r.id1=?', params).fetchone()
    brand = models.Brand.objects.get(title=brand_row['title'])
    try:
        line_row = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE p1.type=16 AND r.id1=?', params).fetchone()
        line = models.CosmeticsLine.objects.get(title=line_row['title'])
    except:
        line = None
    cosmetics, created = models.Cosmetics.objects.get_or_create(
        title=post_row['title'],
        body=post_row['content'],
        alias=alias,
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
        brand=brand,
        line=line,
    )
    params = (post_row['id'], )
    relation_rows = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
    for relation_row in relation_rows:
        params = (relation_row['id'], )
        related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
        related = posts[related_post_row['id']]
        if relation_row['type'] == 14:
            cosmetics.dosage_forms.add(related)
        elif relation_row['type'] == 15:
            cosmetics.usage_areas.add(related)
        elif relation_row['type'] == 12:
            cosmetics.category.add(related)

    posts[post_row['id']] = cosmetics


post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 2').fetchall()
for post_row in post_rows:
    params = (post_row['id'], )
    alias_row = c.execute('SELECT * FROM alias a WHERE a.entity_id = ?', params).fetchone()
    alias = alias_row['alias']
    blog, created = models.Blog.objects.get_or_create(
        title=post_row['title'],
        body=post_row['content'],
        alias=alias,
        created=date_from_timestamp(post_row['create_time']),
        edited=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
    )
    params = (post_row['id'], )
    relation_rows = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
    for relation_row in relation_rows:
        params = (relation_row['id'], )
        related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
        related = posts[related_post_row['id']]
        if relation_row['type'] == 12:
            blog.category.add(related)
    posts[post_row['id']] = blog

comments = {}

comment_rows = c.execute('SELECT * FROM comment c ORDER BY c.create_time').fetchall()
for comment_row in comment_rows:
    if comment_row['parent_id']:
        parent = comments[comment_row['parent_id']]
    else:
        parent = None


    if comment_row['author_id']:
        params = (comment_row['author_id'], )
        user_row = c.execute('SELECT u.username FROM users u WHERE u.id=?', params).fetchone()
        user = models.User.objects.get(username=user_row['username'])
    else:
        user = None

    if comment_row['editor_id']:
        params = (comment_row['editor_id'], )
        user_row = c.execute('SELECT u.username FROM users u WHERE u.id=?', params).fetchone()
        updater = models.User.objects.get(username=user_row['username'])
    else:
        updater = None

    post = posts[comment_row['post_id']]
    comment, created = models.Comment.objects.get_or_create(
        post=post,
        username=comment_row['author'],
        email=comment_row['email'] if comment_row['email'] else '',
        post_mark=comment_row['mark'],
        body=comment_row['content'],
        ip=comment_row['ip'],
        consult_required=comment_row['consult'],
        created=date_from_timestamp(comment_row['create_time']),
        updated=date_from_timestamp(comment_row['update_time']),
        status=models.COMMENT_STATUS_PUBLISHED if comment_row['status'] == 2 else models.COMMENT_STATUS_PENDING_APPROVAL,
        user=user,
        updater=updater,
        key=comment_row['activkey'],
        approved=comment_row['approved'],
        parent=parent,
    )
    comments[comment_row['id']] = comment



