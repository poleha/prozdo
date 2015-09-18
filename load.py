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
from django.utils.timezone import get_default_timezone, now
from prozdo_main.helper import make_alias
from django.contrib.redirects.models import Redirect
from django.db.models import Q

try:
    last_hist_pk = models.History.objects.latest('created').pk
except:
    last_hist_pk = None

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
#models.History.objects.all().delete()
#Redirect.objects.all().delete()

load_users = False
load_posts = False
load_comments = False
load_history = False
load_images = False
create_redirects = False
fix_aliases = True

conn = sqlite3.connect('prozdo.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()

#users = {}

if load_users:
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
        user_profile.old_id = user_row['id']
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
        #users[user_row] = user


#posts = {}

if load_posts:
    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type > 3 AND p.type < 8').fetchall()
    for post_row in post_rows:
        params = (post_row['id'], )
        alias_row = c.execute('SELECT * FROM alias a WHERE a.route="post/view" AND a.entity_id = ?', params).fetchone()
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
            updated=date_from_timestamp(post_row['update_time']),
            component_type=component_type,
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        component.old_id = post_row['id']
        #posts[post_row['id']] = component

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 8').fetchall()
    for post_row in post_rows:
        drug_dosage_form, created = models.DrugDosageForm.objects.get_or_create(
            title=post_row['title'],
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        drug_dosage_form.old_id = post_row['id']
        #posts[post_row['id']] = drug_dosage_form

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 9').fetchall()
    for post_row in post_rows:
        drug_usage_area, created = models.DrugUsageArea.objects.get_or_create(
            title=post_row['title'],
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        drug_usage_area.old_id = post_row['id']
        #posts[post_row['id']] = drug_usage_area

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 12').fetchall()
    for post_row in post_rows:
        if post_row['parent_id']:
            parent_category = models.Category.objects.get(old_id=post_row['parent_id']) #posts[post_row['parent_id']]
        else:
            parent_category = None
        category, created = models.Category.objects.get_or_create(
            title=post_row['title'],
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            parent=parent_category,
            old_id=post_row['id'],
        )
        category.old_id = post_row['id']
        #posts[post_row['id']] = category

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 14').fetchall()
    for post_row in post_rows:
        cosmetics_dosage_form, created = models.CosmeticsDosageForm.objects.get_or_create(
            title=post_row['title'],
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        cosmetics_dosage_form.old_id = post_row['id']
        #posts[post_row['id']] = cosmetics_dosage_form

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 15').fetchall()
    for post_row in post_rows:
        cosmetics_usage_area, created = models.CosmeticsUsageArea.objects.get_or_create(
            title=post_row['title'],
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        cosmetics_usage_area.old_id = post_row['id']
        #posts[post_row['id']] = cosmetics_usage_area

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 16').fetchall()
    for post_row in post_rows:
        line, created = models.CosmeticsLine.objects.get_or_create(
            title=post_row['title'],
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        line.old_id = post_row['id']
        #posts[post_row['id']] = line

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 17').fetchall()
    for post_row in post_rows:
        brand, created = models.Brand.objects.get_or_create(
        title=post_row['title'],
        created=date_from_timestamp(post_row['create_time']),
        updated=date_from_timestamp(post_row['update_time']),
        status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
        old_id=post_row['id'],
        )
        brand.old_id = post_row['id']
        #posts[post_row['id']] = brand

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 1').fetchall()
    for post_row in post_rows:
        params = (post_row['id'], )
        alias_row = c.execute('SELECT * FROM alias a WHERE a.route="post/view" AND a.entity_id = ?', params).fetchone()
        alias = alias_row['alias']
        drug, created = models.Drug.objects.get_or_create(
            title=post_row['title'],
            body=post_row['content'],
            alias=alias,
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            indications=post_row['pokaz'] if post_row['pokaz'] else '',
            features=post_row['osob'] if post_row['osob'] else '',
            application_scheme=post_row['priem'] if post_row['priem'] else '',
            dosage_form=post_row['form_vip_text'] if post_row['form_vip_text'] else '',
            contra_indications=post_row['prot'] if post_row['prot'] else '',
            side_effects=post_row['side_effects'] if post_row['side_effects'] else '',
            compound=post_row['sostav'] if post_row['sostav'] else '',
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        params = (post_row['id'], )
        relation_rows = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
        for relation_row in relation_rows:
            params = (relation_row['id'], )
            related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()

            if relation_row['type'] in [4, 5, 6, 7]:
                component = models.Component.objects.get(old_id=related_post_row['id'])
                drug.components.add(component)
            elif relation_row['type'] == 9:
                drug_usage_area = models.DrugUsageArea.objects.get(old_id=related_post_row['id'])
                drug.usage_areas.add(drug_usage_area)
            elif relation_row['type'] == 8:
                drug_dosage_form = models.DrugDosageForm.objects.get(old_id=related_post_row['id'])
                drug.dosage_forms.add(drug_dosage_form)
            elif relation_row['type'] == 12:
                category = models.Category.objects.get(old_id=related_post_row['id'])
                drug.category.add(category)

        #posts[post_row['id']] = drug

    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 18').fetchall()
    for post_row in post_rows:
        params = (post_row['id'], )
        alias_row = c.execute('SELECT * FROM alias a WHERE a.route="post/view" AND a.entity_id = ?', params).fetchone()
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
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            brand=brand,
            line=line,
            old_id=post_row['id'],
        )
        params = (post_row['id'], )
        relation_rows = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
        for relation_row in relation_rows:
            params = (relation_row['id'], )
            related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
            #related = models.Post.objects.get(old_id=related_post_row['id'])#posts[related_post_row['id']]
            if relation_row['type'] == 14:
                cosmetics_dosage_form = models.CosmeticsDosageForm.objects.get(old_id=related_post_row['id'])
                cosmetics.dosage_forms.add(cosmetics_dosage_form)
            elif relation_row['type'] == 15:
                cosmetics_dosage_form = models.CosmeticsUsageArea.objects.get(old_id=related_post_row['id'])
                cosmetics.usage_areas.add(cosmetics_dosage_form)
            elif relation_row['type'] == 12:
                category = models.Category.objects.get(old_id=related_post_row['id'])
                cosmetics.category.add(category)

        #posts[post_row['id']] = cosmetics


    post_rows = c.execute('SELECT * FROM post p LEFT JOIN product_fields pf ON p.id = pf.post_id WHERE p.type = 2').fetchall()
    for post_row in post_rows:
        params = (post_row['id'], )
        alias_row = c.execute('SELECT * FROM alias a WHERE a.route="post/view" AND a.entity_id = ?', params).fetchone()
        alias = alias_row['alias']
        blog, created = models.Blog.objects.get_or_create(
            title=post_row['title'],
            body=post_row['content'],
            alias=alias,
            created=date_from_timestamp(post_row['create_time']),
            updated=date_from_timestamp(post_row['update_time']),
            status=models.POST_STATUS_PUBLISHED if post_row['status'] == 2 else models.POST_STATUS_PROJECT,
            old_id=post_row['id'],
        )
        params = (post_row['id'], )
        relation_rows = c.execute('SELECT p1.id, p1.title, p1.type FROM relation r LEFT JOIN post p ON r.id1 = p.id LEFT JOIN post p1 ON r.id2=p1.id WHERE r.id1=?', params).fetchall()
        for relation_row in relation_rows:
            params = (relation_row['id'], )
            related_post_row = c.execute('SELECT * FROM post p WHERE p.id = ?', params).fetchone()
            #related = models.Post.objects.get(old_id=related_post_row['id']) #posts[related_post_row['id']]
            if relation_row['type'] == 12:
                category = models.Category.objects.get(old_id=related_post_row['id'])
                blog.category.add(category)
        #posts[post_row['id']] = blog

#comments = {}
if load_comments:
    comment_rows = c.execute('SELECT * FROM comment c JOIN post p on c.post_id = p.id WHERE p.type <> 11 ORDER BY c.create_time').fetchall()
    for comment_row in comment_rows:
        if comment_row['parent_id']:
            try:
                parent = models.Comment.objects.get(old_id=comment_row['parent_id']) #comments[comment_row['parent_id']]
            except:
                parent = None
                print('Parent comment not found for {0} - {1}'.format(comment_row['id'], comment_row['parent_id']))
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

        try:
            post = models.Post.objects.get(old_id=comment_row['post_id'])#posts[comment_row['post_id']]
        except:
            print('Post not found for {0} - {1}'.format(comment_row['id'], comment_row['post_id']))
            continue
        comment, created = models.Comment.objects.get_or_create(
            post=post,
            username=comment_row['author'],
            email=comment_row['email'] if comment_row['email'] else '',
            post_mark=comment_row['mark'] if comment_row['mark'] else None,
            body=comment_row['content'],
            ip=comment_row['ip'],
            consult_required=comment_row['consult'] if comment_row['consult'] else False,
            created=date_from_timestamp(comment_row['create_time']),
            updated=date_from_timestamp(comment_row['update_time']),
            status=models.COMMENT_STATUS_PUBLISHED if comment_row['status'] == 2 else models.COMMENT_STATUS_PENDING_APPROVAL,
            user=user,
            updater=updater,
            key=comment_row['activkey'],
            confirmed=comment_row['approved'] if comment_row['approved'] else False,
            parent=parent,
            old_id=comment_row['id'],
        )
        #comments[comment_row['id']] = comment



#*********************History
if load_history:
    if last_hist_pk:
        models.History.objects.filter(pk__gt=last_hist_pk).delete()

    history_rows = c.execute('SELECT * FROM history h '
                             'LEFT JOIN post p on h.post_id = p.id '
                             'LEFT JOIN comment c ON h.comment_id = c.id '
                             'WHERE p.type <> 11 AND h.type <> 4 AND h.type <> 5 AND h.type <> 7 AND h.type <> 8 AND'
                             ' h.type <> 11 ORDER BY h.create_time').fetchall()

    hist_type_dict = {
        1: 3,
        2: 1,
        3: 6,
        4: None,
        5: None,
        6: 5,
        7: None,
        8: None,
        9: 2,
        10: 7,
        11: None,
    }



    for history_row in history_rows:
        try:
            h, created = models.History.objects.get_or_create(
            post=models.Post.objects.get(old_id=history_row['post_id']),
            history_type = hist_type_dict[int(history_row['type'])],
            author=models.User.objects.get(user_profile__old_id=history_row['auser_id']) if history_row['auser_id'] else None,
            user=models.User.objects.get(user_profile__old_id=history_row['user_id']) if history_row['user_id'] else None,
            comment=models.Comment.objects.get(old_id=history_row['comment_id']) if history_row['comment_id'] else None,
            user_points=history_row['user_points'],
            created=date_from_timestamp(history_row['create_time']),
            ip=history_row['ip'],
            mark=history_row['points'],
            old_id=history_row['id'],
            )
        except:
            print(dict(history_row))

if load_images:
    #from multi_image_upload.models import save_thumbs, generate_filenames
    from django.core.files.storage import FileSystemStorage
    base_image_path = os.path.join(settings.MEDIA_ROOT, 'load_images')

    save_path = os.path.join(settings.MEDIA_ROOT, 'drug')
    for drug in models.Drug.objects.all():
        try:
            image_path = os.path.join(save_path, drug.image.name)
            image = open(image_path, 'r')
        except:
            image = None

        if image is None:
            params = (drug.old_id, )
            image_row = c.execute('SELECT i.document FROM post p LEFT JOIN image i ON p.image_id = i.id WHERE p.id=?', params).fetchone()
            image_name = image_row['document']
            if not image_name:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!image not found', drug)
                continue

            ext = image_name.split('.')[-1]
            storage = FileSystemStorage(save_path)
            new_name = make_alias(drug.title) + '.' + ext

            file = os.path.join(base_image_path, image_name)

            try:
                f = open(file, 'rb')
            except:
                #print(file)
                continue
            storage.save(new_name, f)
            #name = os.path.split(name_jpg)[-1]

            #save_thumbs(storage, thumb_settings, image, upload_to, name):
            #save_thumbs(storage, settings.DRUG_THUMB_SETTINGS, file, '', name)

            drug.image = 'drug/' + new_name
            drug.save()
            print(drug)

    save_path = os.path.join(settings.MEDIA_ROOT, 'blog')
    for blog in models.Blog.objects.all():
        try:
            image_path = os.path.join(save_path, blog.image.name)
            image = open(image_path, 'r')
        except:
            image = None

        if image is None:
            params = (blog.old_id, )
            image_row = c.execute('SELECT i.document FROM post p LEFT JOIN image i ON p.image_id = i.id WHERE p.id=?', params).fetchone()
            image_name = image_row['document']
            if not image_name:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!image not found', blog)
                continue

            ext = image_name.split('.')[-1]
            storage = FileSystemStorage(save_path)
            new_name = make_alias(blog.title) + '.' + ext

            try:
                file = os.path.join(base_image_path, image_name)
            except:
                #print(file)
                continue

            f = open(file, 'rb')
            storage.save(new_name, f)
            #name = os.path.split(name_jpg)[-1]

            #save_thumbs(storage, thumb_settings, image, upload_to, name):
            #save_thumbs(storage, settings.BLOG_THUMB_SETTINGS, file, '', name)

            blog.image = 'blog/' + new_name
            blog.save()
            print(blog)

    save_path = os.path.join(settings.MEDIA_ROOT, 'cosmetics')
    for cosmetics in models.Cosmetics.objects.all():
        try:
            image_path = os.path.join(save_path, cosmetics.image.name)
            image = open(image_path, 'r')
        except:
            image = None

        if image is None:
            params = (cosmetics.old_id, )
            image_row = c.execute('SELECT i.document FROM post p LEFT JOIN image i ON p.image_id = i.id WHERE p.id=?', params).fetchone()
            image_name = image_row['document']
            if not image_name:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!image not found', cosmetics)
                continue

            ext = image_name.split('.')[-1]
            storage = FileSystemStorage(save_path)
            new_name = make_alias(cosmetics.title) + '.' + ext

            file = os.path.join(base_image_path, image_name)

            try:
                f = open(file, 'rb')
            except:
                #print(file)
                continue
            storage.save(new_name, f)
            #name = os.path.split(name_jpg)[-1]

            #save_thumbs(storage, thumb_settings, image, upload_to, name):
            #save_thumbs(storage, settings.COSMETICS_THUMB_SETTINGS, file, '', name)

            cosmetics.image = 'cosmetics/' + new_name
            cosmetics.save()
            print(cosmetics)

    base_image_path = os.path.join(settings.MEDIA_ROOT, 'load_images_user')
    save_path = os.path.join(settings.MEDIA_ROOT, 'user_profile')
    for user_profile in models.UserProfile.objects.all():
        try:
            image_path = os.path.join(save_path, user_profile.image.name)
            image = open(image_path, 'r')
        except:
            image = None

        if image is None:
            if not user_profile.old_id:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!user old_id not found', user_profile)
                continue
            params = (user_profile.old_id, )
            image_row = c.execute('SELECT i.document FROM users u LEFT JOIN image i ON u.image_id = i.id WHERE u.id=?', params).fetchone()
            image_name = image_row['document']
            if not image_name:
                print('!!!!!!!!!!!!!!!!!!!!!!!!!image not found', user_profile)
                continue

            ext = image_name.split('.')[-1]
            storage = FileSystemStorage(save_path)
            new_name = str(user_profile.user.id) + '.' + ext

            file = os.path.join(base_image_path, image_name)

            try:
                f = open(file, 'rb')
            except:
                #print(file)
                continue
            storage.save(new_name, f)
            #name = os.path.split(name_jpg)[-1]

            #save_thumbs(storage, thumb_settings, image, upload_to, name):
            #save_thumbs(storage, settings.USER_PROFILE_THUMB_SETTINGS, file, '', name)

            user_profile.image = 'user_profile/' + new_name
            user_profile.save()
            print(user_profile)

if create_redirects:
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    posts = models.Post.objects.filter(Q(alias__contains='bad/')|Q(alias__contains='vitamin/'))
    #print(list(posts))
    for post in posts:
        alias = make_alias(post.title)
        Redirect.objects.get_or_create(
            site=current_site,
            old_path='/' + post.alias,
            new_path='/' + alias
        )
        obj = post.obj
        obj.alias = alias
        obj.save()

if fix_aliases:
    import re
    for post in models.Post.objects.filter(~Q(alias='')):
        result = re.match('[a-z0-9_\-]{1,}', post.alias)
        unicode_error = False
        try:
            post.alias.encode('ascii')
        except:
            unicode_error = True
        if not result or unicode_error:

            obj = post.obj
            obj.title = post.title.encode('utf8').replace('и'.encode('utf8') + b'\xcc\x86', 'й'.encode('utf8')).decode('utf8')
            obj.alias = make_alias(obj.title)
            obj.save()
            print(obj.title, obj.alias)

