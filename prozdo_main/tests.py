from django_webtest import WebTest
from . import models
from django.core.urlresolvers import reverse
from django.conf import settings
from allauth.account.models import EmailAddress, EmailConfirmation
from django.core.cache import cache
from super_model import models as super_models
#from cacheops import invalidate_all
from django.core.exceptions import ValidationError
from haystack.management.commands import rebuild_index, update_index
#from django.test.client import Client
#c = Client()

class BaseTest(WebTest):
    def setUp(self):
        cache.clear()
        self.user = models.User.objects.create(username='asdgsdfhhfgdjfh', password='1234567', email='sdfgsdfg@sdfsdg.ru')

        self.email_adress = EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True,
        )

        self.email_confirmation = EmailConfirmation.create(self.email_adress)



        self.user2 = models.User.objects.create(username='asssdfdsgdfg', password='1234567', email='dsgdfsgsdfg@dsfgsdg.ru')

        self.email_adress2= EmailAddress.objects.create(
            user=self.user2,
            email=self.user2.email,
            verified=False,
            primary=True,
        )



        self.component = models.Component.objects.create(
            body='body',
            title = 'title_component',
            component_type = models.COMPONENT_TYPE_MINERAL,
        )


        self.drug_dosage_form = models.DrugDosageForm.objects.create(
            title = 'title_drug_dosage_form',
        )


        self.drug_usage_area = models.DrugUsageArea.objects.create(
            title = 'title_drug_usage_area',
        )


        self.drug = models.Drug.objects.create(
            title='title_drug',
            body='body',

        )

        self.blog = models.Blog.objects.create(
            title='title_blog',
            body='body_blog',

        )

    def tearDown(self):
        cache.clear()


class CommentAntispanTests(BaseTest):
    def test_comment_antispan_normal_comment_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)

    def test_comment_antispan_comment_with_bad_word_in_body_not_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        bad_words = settings.BAD_WORDS
        for bad_word in bad_words:
            bad_body = body + bad_word
            form['email'] = email
            form['username'] = username
            form['body'] = bad_body
            page = form.submit()
            self.assertEqual(page.status_code, 302)
            comment = models.Comment.objects.all().latest('created')
            self.assertEqual(comment.body, bad_body)
            self.assertEqual(comment.username, username)
            self.assertEqual(comment.email, email)
            self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)

    def test_comment_antispan_comment_with_bad_word_in_username_not_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'

        bad_words = settings.BAD_WORDS
        for bad_word in bad_words:
            bad_username = username + bad_word
            form['email'] = email
            form['username'] = bad_username
            body += 'а'
            form['body'] = body
            page = form.submit()
            self.assertEqual(page.status_code, 302)
            comment = models.Comment.objects.all().latest('created')
            self.assertEqual(comment.body, body)
            self.assertEqual(comment.username, bad_username)
            self.assertEqual(comment.email, email)
            self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)

    def test_comment_antispan_comment_with_too_much_digits_in_body_not_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв123456789012345678901234567890123456789'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)

    def test_comment_antispan_comment_with_not_too_much_digits_in_body_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв12345678901267890125678901234567'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)

    def test_comment_antispan_comment_with_too_much_eng_in_body_not_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзывzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)

    def test_comment_antispan_comment_with_not_too_much_eng_in_body_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзывzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)

    def test_comment_antispan_comment_with_errors_not_published_for_user(self):
        drug = self.drug
        u = self.user
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u)
        form = page.forms['comment-form']
        body = 'zzzzzzzz1111'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = settings.BAD_WORDS[0]
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)


    def test_comment_antispan_comment_with_errors_published_for_user_with_karm_above_9(self):
        drug = self.drug
        u = self.user
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u)
        form = page.forms['comment-form']
        body = 'zzzzzzzz1111'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = settings.BAD_WORDS[0]
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)
        comment.status = super_models.COMMENT_STATUS_PUBLISHED
        comment.save()
        for k in range(settings.PUBLISH_COMMENT_WITHOUT_APPROVE_KARM):
            models.History.save_history(post=comment.post, comment=comment, history_type=super_models.HISTORY_TYPE_COMMENT_RATED, ip='1.2.3.{0}'.format(k), session_key='fsdfsdfsdfsd34{0}'.format(k))

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u)
        form = page.forms['comment-form']
        username = settings.BAD_WORDS[0]
        form['email'] = email
        form['username'] = username
        body += 'а'
        form['body'] = body
        self.assertEqual(u.karm, settings.PUBLISH_COMMENT_WITHOUT_APPROVE_KARM)
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)

    def test_comment_antispan_comment_with_errors_published_for_doctor(self):
        drug = self.drug
        u = self.user
        u.user_profile.role = super_models.USER_ROLE_DOCTOR
        u.user_profile.save()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u)
        form = page.forms['comment-form']
        body = 'zzzzzzzz1111'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        #username = settings.BAD_WORDS[0]
        form['email'] = email
        #form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        #self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)


class HistoryTests(BaseTest):
    def test_comment_create_without_mark_for_drug(self):
        drug = self.drug
        user = self.user
        start_hist_count = models.History.objects.filter(deleted=False).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        result_hist_count = models.History.objects.filter(deleted=False).count()
        comment = models.Comment.objects.latest('created')

        self.assertEqual(start_hist_count + 1, result_hist_count)
        h = models.History.objects.latest('created')
        self.assertEqual(h.user, comment.user)
        self.assertEqual(h.user, user)
        self.assertEqual(h.author, None)
        self.assertEqual(h.post, drug.post_ptr)
        self.assertEqual(h.comment, comment)
        self.assertEqual(h.mark, None)
        self.assertEqual(comment.post_mark, None)
        self.assertEqual(h.history_type, super_models.HISTORY_TYPE_COMMENT_CREATED)


    def test_comment_create_and_save_and_post_mark_for_drug(self):
        drug = self.drug
        user = self.user
        start_hist_count = models.History.objects.filter(deleted=False).count()


        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        form['post_mark'] = 4
        page = form.submit()

        result_hist_count = models.History.objects.filter(deleted=False).count()

        self.assertEqual(start_hist_count + 1, result_hist_count)

        comment = models.Comment.objects.latest('created')

        h = models.History.objects.latest('created')
        self.assertEqual(h.post, drug.post_ptr)
        self.assertEqual(h.comment, comment)
        self.assertEqual(h.mark, 4)
        self.assertEqual(comment.post_mark, 4)
        self.assertEqual(h.history_type, super_models.HISTORY_TYPE_COMMENT_CREATED)



class HistoryAjaxSaveTests(BaseTest):
    def setUp(self):
        super().setUp()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=self.user2)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        self.comment = models.Comment.objects.latest('created')
        self.comment_actions = (
            ('comment-mark', 'comment-unmark', super_models.HISTORY_TYPE_COMMENT_RATED),
            ('comment-complain', 'comment-uncomplain', super_models.HISTORY_TYPE_COMMENT_COMPLAINT)
        )


    def test_user_and_guest_cannot_mark_or_complain_own_comment(self):
        comment = self.comment

        users = (self.user2, None)
        for user in users:
            self.renew_app()
            for action, cancel, history_type in self.comment_actions:
                params= {
                    'action': action,
                    'pk': comment.pk,
                }
                start_hist_count = models.History.objects.filter(deleted=False).count()
                page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user2)
                result_hist_count = models.History.objects.filter(deleted=False).count()
                self.assertEqual(start_hist_count, result_hist_count)

    def test_user_and_guest_comment_mark_and_comment_unmark_and_comment_complain_and_comment_uncomplain(self):
        drug = self.drug
        users = (self.user, None)
        comment = self.comment

        for user in users:
            for action, cancel, history_type in self.comment_actions:
                start_hist_count = models.History.objects.filter(deleted=False).count()

                params= {
                    'action': action,
                    'pk': comment.pk,
                }
                page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
                h_mark = models.History.objects.latest('created')
                self.assertEqual(h_mark.post, drug.post_ptr)
                self.assertEqual(h_mark.comment, comment)
                self.assertEqual(h_mark.history_type, history_type)
                result_hist_count = models.History.objects.filter(deleted=False).count()
                self.assertEqual(start_hist_count + 1, result_hist_count)

                params= {
                    'action': cancel,
                    'pk': comment.pk,
                }
                page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
                result_hist_count = models.History.objects.filter(deleted=False).count()
                self.assertEqual(start_hist_count, result_hist_count)

    def test_user_cant_unmark_and_uncomplain_not_his_comment(self):
        drug = self.drug
        comment = self.comment
        user = self.user
        for action, cancel, history_type in self.comment_actions:
            start_hist_count = models.History.objects.filter(deleted=False).count()

            params= {
                'action': action,
                'pk': comment.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            h_mark = models.History.objects.latest('created')
            self.assertEqual(h_mark.post, drug.post_ptr)
            self.assertEqual(h_mark.comment, comment)
            self.assertEqual(h_mark.history_type, history_type)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

            params= {
                'action': cancel,
                'pk': comment.pk,
            }
            self.renew_app()
            page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user2)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

    def test_guest_cant_unmark_and_uncomplain_not_his_comment(self):
        drug = self.drug
        comment = self.comment
        comment.ip = '111.222.333.444'
        comment.save()
        user = self.user
        for action, cancel, history_type in self.comment_actions:
            start_hist_count = models.History.objects.filter(deleted=False).count()

            params= {
                'action': action,
                'pk': comment.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            h_mark = models.History.objects.latest('created')
            self.assertEqual(h_mark.post, drug.post_ptr)
            self.assertEqual(h_mark.comment, comment)
            self.assertEqual(h_mark.history_type, history_type)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

            params= {
                'action': cancel,
                'pk': comment.pk,
            }
            self.renew_app()
            page = self.app.post(reverse('history-ajax-save'), params=params)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count + 1, result_hist_count)



    def test_user_and_guest_can_mark_and_unmark_drug(self):
        drug = self.drug

        users = (self.user, None)

        for user in users:
            self.renew_app()
            start_hist_count = models.History.objects.filter(deleted=False).count()

            params= {
                'action': 'post-mark',
                'pk': drug.pk,
                'mark': 5,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            h = models.History.objects.latest('created')
            self.assertEqual(h.post, drug.post_ptr)
            self.assertEqual(h.comment, None)
            self.assertEqual(h.mark, 5)
            self.assertEqual(h.history_type, super_models.HISTORY_TYPE_POST_RATED)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

            params= {
                'action': 'post-unmark',
                'pk': drug.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count, result_hist_count)


    def test_doctor_can_mark_and_unmark_comment_for_delete(self):
        start_hist_count = models.History.objects.filter(deleted=False).count()
        comment = self.comment
        user = self.user
        up = user.user_profile
        up.role = super_models.USER_ROLE_DOCTOR
        up.save()
        params= {
                'action': 'comment-delete',
                'pk': comment.pk,
            }
        page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
        h = models.History.objects.latest('created')
        self.assertEqual(h.post, comment.post)
        self.assertEqual(h.comment, comment)
        self.assertEqual(h.mark, None)
        self.assertEqual(h.history_type, super_models.HISTORY_TYPE_COMMENT_SAVED)
        result_hist_count = models.History.objects.filter(deleted=False).count()
        self.assertEqual(start_hist_count + 1, result_hist_count)
        comment = comment.saved_version
        self.assertEqual(comment.delete_mark, True)

        params= {
            'action': 'comment-undelete',
            'pk': comment.pk,
        }
        page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
        result_hist_count = models.History.objects.filter(deleted=False).count()
        self.assertEqual(start_hist_count + 2, result_hist_count)
        comment = comment.saved_version
        self.assertEqual(comment.delete_mark, False)


    def test_guest_and_regular_user_cant_mark_for_delete(self):


        comment = self.comment
        user = self.user2

        for user in (user, None):
            self.renew_app()
            params= {
                    'action': 'comment-delete',
                    'pk': comment.pk,
                }
            comment.delete_mark = False
            comment.save()
            start_hist_count = models.History.objects.filter(deleted=False).count()
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            h = models.History.objects.latest('created')
            self.assertEqual(h.post, comment.post)
            self.assertEqual(h.comment, comment)
            self.assertEqual(h.mark, None)
            self.assertEqual(h.history_type, super_models.HISTORY_TYPE_COMMENT_SAVED)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count, result_hist_count)
            comment = comment.saved_version
            self.assertEqual(comment.delete_mark, False)
            comment.delete_mark = True
            comment.save()
            start_hist_count = models.History.objects.filter(deleted=False).count()
            params= {
                'action': 'comment-undelete',
                'pk': comment.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            result_hist_count = models.History.objects.filter(deleted=False).count()
            self.assertEqual(start_hist_count, result_hist_count)

    def test_session_key_is_applied_to_comment_without_session_key_on_comment_delete(self):
        comment = self.comment
        type(comment).objects.filter(pk=comment.pk).update(session_key=None, delete_mark=False)
        #comment.session_key = None
        comment = comment.saved_version
        user = self.user
        up = user.user_profile
        up.role = super_models.USER_ROLE_DOCTOR
        up.save()
        self.assertEqual(comment.session_key, None)

        params= {
                'action': 'comment-delete',
                'pk': comment.pk,
            }

        page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
        comment = comment.saved_version

        comment = comment.saved_version
        self.assertNotEqual(comment.session_key, None)

    def test_history_ajax_save_works_fine_without_pk(self):
        page = self.app.post(reverse('history-ajax-save'))
        self.assertEqual(page.status_code, 200)



class PostPagesTest(BaseTest):
    def setUp(self):
        super().setUp()
        comments0 = []
        comments1 = []
        comments2 = []
        self.drug.alias = 'fsdsdfgsdfgshgfd'
        self.drug.save()
        for k in range(settings.POST_COMMENTS_PAGE_SIZE * 2 + 1):

            comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпиорвполривапрва-level0-{0}'.format(k),
                status=super_models.COMMENT_STATUS_PUBLISHED,

            )
            comments0.append(comment)

        for k in range(settings.POST_COMMENTS_PAGE_SIZE * 2 + 1):
            comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпиорвполривапрва-level1-{0}'.format(k),
                status=super_models.COMMENT_STATUS_PUBLISHED,
                parent=comments0[k]

            )
            comments1.append(comment)

        for k in range(settings.POST_COMMENTS_PAGE_SIZE * 2 + 1):
            comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпиорвполривапрва-level2-{0}'.format(k),
                status=super_models.COMMENT_STATUS_PUBLISHED,
                parent=comments1[k]

            )
            comments2.append(comment)
            self.comments0 = comments0
            self.comments1 = comments1
            self.comments2 = comments2

    def test_comment_is_found_on_proper_page_for_alias_and_pk(self):
        for k in range(settings.POST_COMMENTS_PAGE_SIZE * 2 + 1):
            self.renew_app()
            comment = self.comments0[k]
            page = self.app.get(reverse('post-detail-pk-comment', kwargs={'pk': comment.post.pk, 'comment_pk': comment.pk}))
            self.assertIn('авырлпоырваыпиорвполривапрва-level0-{0}'.format(k), page)

            comment = self.comments1[k]
            page = self.app.get(reverse('post-detail-pk-comment', kwargs={'pk': comment.post.pk, 'comment_pk': comment.pk}))
            self.assertIn('авырлпоырваыпиорвполривапрва-level1-{0}'.format(k), page)

            comment = self.comments2[k]
            page = self.app.get(reverse('post-detail-pk-comment', kwargs={'pk': comment.post.pk, 'comment_pk': comment.pk}))
            self.assertIn('авырлпоырваыпиорвполривапрва-level2-{0}'.format(k), page)

            comment = self.comments0[k]
            page = self.app.get(reverse('post-detail-alias-comment', kwargs={'alias': comment.post.drug.alias, 'comment_pk': comment.pk}))
            self.assertIn('авырлпоырваыпиорвполривапрва-level0-{0}'.format(k), page)

            comment = self.comments1[k]
            page = self.app.get(reverse('post-detail-alias-comment', kwargs={'alias': comment.post.drug.alias, 'comment_pk': comment.pk}))
            self.assertIn('авырлпоырваыпиорвполривапрва-level1-{0}'.format(k), page)

            comment = self.comments2[k]
            page = self.app.get(reverse('post-detail-alias-comment', kwargs={'alias': comment.post.drug.alias, 'comment_pk': comment.pk}))
            self.assertIn('авырлпоырваыпиорвполривапрва-level2-{0}'.format(k), page)

    def test_post_detail_pk_comment_view_works_fine_when_comment_not_found(self):
        self.assertEqual(models.Comment.objects.filter(pk=111111111111111111111111).exists(), False)
        page = self.app.get(reverse('post-detail-pk-comment', kwargs={'pk': self.drug.pk, 'comment_pk': 111111111111111111111111}))
        self.assertEqual(page.status_code, 200)


class CommentConfirmationTests(BaseTest):
    def test_comment_confirm_message_is_sent_for_published_guest_and_comment_can_be_activated(self):
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

        mail = models.Mail.objects.latest('created')
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.assertEqual(mail.mail_type, super_models.MAIL_TYPE_COMMENT_CONFIRM)
        self.assertIn(comment.get_confirm_url(), mail.body_html)
        page = self.app.get(comment.get_confirm_url())
        comment = comment.saved_version
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)

    def test_comment_comment_cant_be_activated_with_wrong_key(self):
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

        mail = models.Mail.objects.latest('created')
        comment = models.Comment.objects.latest('created')
        self.assertEqual(mail.mail_type, super_models.MAIL_TYPE_COMMENT_CONFIRM)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.assertIn(comment.get_confirm_url(), mail.body_html)
        url = settings.SITE_URL + reverse('comment-confirm', kwargs={'comment_pk': comment.pk, 'key': comment.key + 'z'})
        page = self.app.get(url)
        comment = comment.saved_version
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)


    def test_guest_comment_can_confirm_own_comment_by_link(self):
        mail_count_0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        page = self.app.post(reverse('comment-get-confirm-form-ajax'), {'pk': comment.pk})
        form = page.form
        form['email'] = email
        form['comment'] = comment.pk
        page = form.submit()
        comment = comment.saved_version
        mail_count_2 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_1 + 1, mail_count_2)


    def test_user_comment_with_approved_mail_is_approved(self):
        user = self.user
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_start, mail_count_end)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)


    def test_user_comment_with_unapproved_mail_is_unapproved_but_approves_on_user_mail_approve(self):
        user = self.user2
        mail_count_0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.email_adress2.verified = True
        self.email_adress2.save()
        comment = comment.saved_version
        self.assertEqual(comment.confirmed, True)

    def test_user_comment_with_unapproved_mail_is_unapproved_but_approves_on_comment_by_mail_approve(self):
        user = self.user2
        email = user.emailaddress_set.all()[0]
        self.assertEqual(email.verified, False)
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

        mail = models.Mail.objects.latest('created')
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.assertIn(comment.get_confirm_url(), mail.body_html)
        page = self.app.get(comment.get_confirm_url())
        comment = comment.saved_version
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)
        email = user.emailaddress_set.all()[0]
        self.assertEqual(email.verified, True)

    def test_user_with_approved_mail_approve_comments_by_click(self):
        user = self.user
        mail_count_0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = user.email
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        page = self.app.post(reverse('comment-get-confirm-form-ajax'), {'pk': comment.pk}, user=user)
        #form = page.form
        #form['email'] = email
        #form['pk'] = comment.pk
        #page = form.submit()
        comment = comment.saved_version
        mail_count_2 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_1, mail_count_2)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)

    def test_guest_comment_cant_confirm_own_comment_by_link_with_wrong_mail(self):
        mail_count_0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        page = self.app.post(reverse('comment-get-confirm-form-ajax'), {'pk': comment.pk})
        form = page.form
        form['email'] = 'sdfsdgjkshne5iu4gh@dsfsdf.ru'
        form['comment'] = comment.pk
        page = form.submit()
        comment = comment.saved_version
        mail_count_2 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_1, mail_count_2)

    def test_comment_with_email_in_auto_approve_emails_is_published_and_mail_is_not_sent_and_confirmed(self):
        mail_count_0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = settings.AUTO_APPROVE_EMAILS[0]
        form['body'] = settings.BAD_WORDS[0]
        form['email'] = email
        form['username'] = settings.BAD_WORDS[1]
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_0, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)

    def test_comment_with_email_in_auto_dont_approve_emails_is_published_and_mail_is_not_sent_and_not_confirmed(self):
        mail_count_0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = settings.AUTO_DONT_APPROVE_EMAILS[0]
        form['body'] = settings.BAD_WORDS[0]
        form['email'] = email
        form['username'] = settings.BAD_WORDS[1]
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_COMMENT_CONFIRM).count()
        self.assertEqual(mail_count_0, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)


class PublishedModelMixinTests(BaseTest):
    def test_comment_takes_publish_time_on_publish_only(self):
        comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпdsgdsfgиорвполривапрва-dsfgsdfffffffffffffffffglevelsdfgfsd',
                status=super_models.COMMENT_STATUS_PENDING_APPROVAL,
            )

        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PENDING_APPROVAL)
        self.assertEqual(comment.published, None)

        comment.status = super_models.COMMENT_STATUS_PUBLISHED
        comment.save()

        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertNotEqual(comment.published, None)
        published = comment.published

        comment.save()

        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.published, published)


    def test_drug_takes_publish_time_on_publish_only(self):
        drug = models.Drug.objects.create(
            title='title_dfgdsfgdrug',
            body='bodsfgdfgdy',

          )

        self.assertEqual(drug.status, super_models.POST_STATUS_PROJECT)
        self.assertEqual(drug.published, None)

        drug.status = super_models.POST_STATUS_PUBLISHED
        drug.save()

        self.assertEqual(drug.status, super_models.POST_STATUS_PUBLISHED)
        self.assertNotEqual(drug.published, None)
        published = drug.published

        drug.save()

        self.assertEqual(drug.status, super_models.POST_STATUS_PUBLISHED)
        self.assertEqual(drug.published, published)

class CommentMessagesTest(BaseTest):
    def setUp(self):
        super().setUp()

    def test_user_gets_email_when_his_approved_comment_is_answered(self):
        mails_count0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        drug = self.drug
        u1 = self.user
        email = u1.emailaddress_set.all()[0]
        self.assertEqual(email.verified, True)

        u2 = self.user2
        email = u2.emailaddress_set.all()[0]
        self.assertEqual(email.verified, False)

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u1)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, True)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        mails_count1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()

        self.assertEqual(mails_count0, mails_count1)

        self.renew_app()

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u2)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        form['body'] = body
        form['parent'] = comment.pk
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, False)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        mails_count2 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        self.assertEqual(mails_count1 + 1, mails_count2)



    def test_user_doesnt_get_email_when_his_unapproved_comment_is_answered(self):
        mails_count0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        drug = self.drug
        u1 = self.user
        email = u1.emailaddress_set.all()[0]
        self.assertEqual(email.verified, True)

        u2 = self.user2
        email = u2.emailaddress_set.all()[0]
        self.assertEqual(email.verified, False)

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u2)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, False)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        mails_count1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()

        self.assertEqual(mails_count0, mails_count1)

        self.renew_app()

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u1)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        form['body'] = body
        form['parent'] = comment.pk
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, True)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        mails_count2 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        self.assertEqual(mails_count1, mails_count2)

    def test_user_doesnt_get_email_when_his_approved_comment_is_answered_by_himself(self):
        mails_count0 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        drug = self.drug
        u1 = self.user
        email = u1.emailaddress_set.all()[0]
        self.assertEqual(email.verified, True)

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u1)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, True)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        mails_count1 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()

        self.assertEqual(mails_count0, mails_count1)

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u1)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        body += 'а'
        form['body'] = body
        form['parent'] = comment.pk
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, True)
        self.assertEqual(comment.status, super_models.COMMENT_STATUS_PUBLISHED)
        mails_count2 = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        self.assertEqual(mails_count1, mails_count2)

class CommentInterfaceTests(BaseTest):
    def setUp(self):
        super().setUp()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=self.user2)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        self.comment = models.Comment.objects.latest('created')
        self.comment_actions = (
            ('comment-mark', 'comment-unmark', super_models.HISTORY_TYPE_COMMENT_RATED),
            ('comment-complain', 'comment-uncomplain', super_models.HISTORY_TYPE_COMMENT_COMPLAINT)
        )

    def test_guest_and_regular_user_cannot_see_delete_button(self):
        u = self.user
        c = self.comment
        for u in (u, None):
            self.renew_app()
            page = self.app.get(c.get_absolute_url(), user=u)
            self.assertNotIn('Пометить на удаление', page)

    def test_doctor_author_guest_can_see_delete_button(self):
        u = self.user
        c = self.comment
        for role in (super_models.USER_ROLE_AUTHOR, super_models.USER_ROLE_DOCTOR, super_models.USER_ROLE_ADMIN):
            self.renew_app()
            up = u.user_profile
            up.role = role
            up.save()
            page = self.app.get(c.get_absolute_url(), user=u)
            self.assertIn('Пометить на удаление', page)


class GeneralCommentTests(BaseTest):
    def test_user_cannot_send_repeated_comment(self):
        mails_count0 = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=self.user2)
        form = page.forms['comment-form']
        body = 'Привет, это вот мой коммент'
        form['body'] = body
        page = form.submit()
        mails_count1 = models.Mail.objects.all().count()
        self.assertEqual(page.status_code, 302)
        self.assertEqual(mails_count0 + 1, mails_count1)

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=self.user2)
        form = page.forms['comment-form']
        form['body'] = body
        page = form.submit()
        mails_count2 = models.Mail.objects.all().count()
        self.assertEqual(page.status_code, 200)
        self.assertEqual(mails_count1, mails_count2)


    def test_session_key_is_changed_on_comment_update_and_udater_is_applied(self):
        u = self.user
        d = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': d.pk}), user=u)
        form = page.forms['comment-form']
        body = 'Привет, это вот мой коммент'
        form['body'] = body
        page = form.submit()
        c = models.Comment.objects.latest('created')
        session_key = c.session_key
        self.assertEqual(c.updater, None)

        self.renew_app()

        page = self.app.get(reverse('comment-update', kwargs={'pk': c.pk}), user=u)
        form = page.forms['comment-form']
        body = 'Привет, это вот мой коммент еще один'
        form['body'] = body
        page = form.submit()

        c = c.saved_version

        self.assertEqual(c.body, body)
        self.assertNotEqual(session_key, c.session_key)
        self.assertEqual(c.updater, u)



class CacheTests(BaseTest):
    def test_deleted_comment_isnt_visible_as_parent_and_child_on_post_detail(self):
        page = self.app.get(self.drug.get_absolute_url())

        parent = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='алоуоац4ай34аглвырпилвыапилоывапиавапыв',
                status=super_models.COMMENT_STATUS_PUBLISHED,
                session_key='sdkfngsdfjgndfsjgnsdfg',
            )

        comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='ваыпоуд4прышгукпргвынпргывапвыап',
                status=super_models.COMMENT_STATUS_PUBLISHED,
                parent=parent,
                session_key='sdkfngsdfjgndfsjgnsdfg',
            )

        child = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авпрволыдапывдалпрывдлапрлывадпргушкпршва',
                status=super_models.COMMENT_STATUS_PUBLISHED,
                parent=comment,
                session_key='sdkfngsdfjgndfsjgnsdfg',
            )

        page = self.app.get(self.drug.get_absolute_url())
        self.assertEqual(page.status_code, 200)
        self.assertIn(parent.body, page)
        self.assertIn(comment.body, page)
        self.assertIn(child.body, page)

        parent_body = parent.body
        comment_body = comment.body
        child_body = child.body

        comment.delete()

        page = self.app.get(self.drug.get_absolute_url())
        self.assertIn(parent_body, page)
        self.assertNotIn(comment_body, page)
        self.assertNotIn(child_body, page)

    #Not cache tests anymore, but let it be
    def test_cached_method_works_for_hist_exists_by_request(self):
        page = self.app.get(self.drug.get_absolute_url())
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        page = self.app.get(self.drug.get_absolute_url())
        self.assertEqual(comment.hist_exists_by_request(super_models.HISTORY_TYPE_COMMENT_CREATED, page.context['request']), True)
        self.renew_app()
        page = self.app.get(comment.get_absolute_url())
        self.assertEqual(comment.hist_exists_by_request(super_models.HISTORY_TYPE_COMMENT_CREATED, page.context['request']), False)

    #Not cache tests anymore, but let it be
    def test_cached_method_works_for_show_do_action_button(self):
        page = self.app.get(self.drug.get_absolute_url())
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        page = self.app.get(self.drug.get_absolute_url())
        self.assertEqual(comment.show_do_action_button(super_models.HISTORY_TYPE_COMMENT_RATED, page.context['request']), False)
        history = models.History.objects.latest('created')
        type(history).objects.filter(pk=history.pk).update(ip='123.235.345.567')
        type(comment).objects.filter(pk=comment.pk).update(ip='534.345.456.467')
        self.assertEqual(comment.show_do_action_button(super_models.HISTORY_TYPE_COMMENT_RATED, page.context['request']), False)
        self.renew_app()
        page = self.app.get(comment.get_absolute_url())
        history = models.History.objects.latest('created')
        type(history).objects.filter(pk=history.pk).update(ip='103.331.145.527')
        self.assertEqual(comment.show_do_action_button(super_models.HISTORY_TYPE_COMMENT_RATED, page.context['request']), True)

        params= {
                'action': 'comment-mark',
                'pk': comment.pk,
            }
        page = self.app.post(reverse('history-ajax-save'), params=params)
        page = self.app.get(comment.get_absolute_url())
        self.assertEqual(comment.show_do_action_button(super_models.HISTORY_TYPE_COMMENT_RATED, page.context['request']), False)

    def test_post_detail_is_cached_for_passive_guest_and_reset_on_post_save(self):
        cache.clear()
        self.renew_app()
        page = self.app.get(self.drug.get_absolute_url())
        self.assertNotEqual(page.context, None)

        page = self.app.get(self.drug.get_absolute_url())
        self.assertEqual(page.context, None)

        self.drug.save()

        page = self.app.get(self.drug.get_absolute_url())
        self.assertNotEqual(page.context, None)

        page = self.app.get(self.drug.get_absolute_url())
        self.assertEqual(page.context, None)

    def test_post_detail_is_not_cached_for_active_guest(self):
        cache.clear()
        self.renew_app()

        params= {
                'action': 'post-mark',
                'mark': 5,
                'pk': self.drug.pk,
            }
        page = self.app.post(reverse('history-ajax-save'), params=params)

        page = self.app.get(self.drug.get_absolute_url())

        self.assertNotEqual(page.context, None)

    def test_post_detail_is_not_cached_for_user(self):
        cache.clear()
        self.renew_app()

        page = self.app.get(self.drug.get_absolute_url(), user=self.user2)

        self.assertNotEqual(page.context, None)

        page = self.app.get(self.drug.get_absolute_url(), user=self.user2)

        self.assertNotEqual(page.context, None)


class AccountMailTests(BaseTest):
    def test_confirmation_mail_is_sent_on_registration_and_mail_model_is_created(self):
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_USER_REGISTRATION).count()
        page = self.app.get(reverse('signup'))
        form = page.forms['signup-form']
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        password = 'dfgjksdfgkj3244'
        form['email'] = email
        form['username'] = username
        form['password1'] = password
        form['password2'] = password
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_USER_REGISTRATION).count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

    def test_password_reset_mail_is_sent_and_mail_model_is_created(self):
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_PASSWORD_RESET).count()
        page = self.app.get(reverse('password-reset'))
        form = page.forms['password-reset-form']
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        form['email'] = self.user.email
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_PASSWORD_RESET).count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

    def test_mail_confirm_mail_is_sent_and_mail_model_is_created(self):
        user = self.user2
        self.assertEqual(user.email_confirmed, False)
        mail_count_start = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_EMAIL_CONFIRMATION).count()
        page = self.app.get(reverse('account_email'), user=user)
        form = page.forms['email-list-form']
        page = form.submit(name='action_send')
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.filter(mail_type=super_models.MAIL_TYPE_EMAIL_CONFIRMATION).count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

class PostTests(BaseTest):
    def test_marks_count_and_average_mark_works_as_expected_for_drug_detail(self):
        drug = self.drug
        self.assertEqual(drug.marks_count, 0)
        self.assertEqual(drug.average_mark, 0)
        params= {
                'action': 'post-mark',
                'mark': 5,
                'pk': drug.pk,
            }
        page = self.app.post(reverse('history-ajax-save'), params=params)
        h1 = models.History.objects.latest('created')
        self.assertEqual(h1.history_type, super_models.HISTORY_TYPE_POST_RATED)
        self.assertEqual(h1.post, drug.post_ptr)
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        self.assertIn('<span id="current-post-mark">5</span>', page)
        self.assertIn('<span id="post-marks-count">1)</span>', page)
        self.assertEqual(drug.marks_count, 1)
        self.assertEqual(drug.average_mark, 5)
        self.assertEqual(drug.post_ptr.marks_count, 1)
        self.assertEqual(drug.post_ptr.average_mark, 5)

        self.renew_app()
        params = {
                'action': 'post-mark',
                'mark': 4,
                'pk': drug.pk,
            }

        page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user)
        h2 = models.History.objects.latest('created')
        self.assertEqual(h2.history_type, super_models.HISTORY_TYPE_POST_RATED)
        self.assertEqual(h2.post, drug.post_ptr)
        self.assertNotEqual(h1.pk, h2.pk)
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        self.assertIn('<span id="post-average-mark">4,5</span>', page)
        self.assertIn('<span id="post-marks-count">2)</span>', page)
        self.assertEqual(drug.marks_count, 2)
        self.assertEqual(drug.average_mark, 4.5)
        self.assertEqual(drug.marks_count, 2)
        self.assertEqual(drug.average_mark, 4.5)
        self.assertEqual(drug.post_ptr.marks_count, 1)
        self.assertEqual(drug.post_ptr.average_mark, 5)

        params= {
                'action': 'post-unmark',
                'pk': drug.pk,
            }

        page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user)
        h3 = models.History.objects.latest('created')
        self.assertEqual(h3.history_type, super_models.HISTORY_TYPE_POST_RATED)
        self.assertEqual(h3.post, drug.post_ptr)
        self.assertEqual(h2.pk, h3.pk)
        self.assertEqual(h3.deleted, True)
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        self.assertIn('<span id="post-average-mark">5,0</span>', page)
        self.assertIn('<span id="post-marks-count">1)</span>', page)
        self.assertEqual(drug.marks_count, 1)
        self.assertEqual(drug.average_mark, 5)
        self.assertEqual(drug.post_ptr.marks_count, 1)
        self.assertEqual(drug.post_ptr.average_mark, 5)

    def test_marks_count_works_as_expected_for_blog_detail(self):
        blog = self.blog
        params= {
                'action': 'post-mark',
                'pk': blog.pk,
            }
        page = self.app.post(reverse('history-ajax-save'), params=params)
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': blog.pk}))
        self.assertIn('<span class="blog-current-mark-span">1</span>', page)
        self.assertEqual(blog.marks_count, 1)
        self.assertEqual(blog.post_ptr.marks_count, 1)

        self.renew_app()
        params = {
                'action': 'post-mark',
                'pk': blog.pk,
            }

        page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user)
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': blog.pk}))
        self.assertIn('<span class="blog-current-mark-span">2</span>', page)
        self.assertEqual(blog.marks_count, 2)
        self.assertEqual(blog.marks_count, 2)

        params= {
                'action': 'post-unmark',
                'pk': blog.pk,
            }

        page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user)
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': blog.pk}))
        self.assertIn('<span class="blog-current-mark-span">1</span>', page)
        self.assertEqual(blog.marks_count, 1)
        self.assertEqual(blog.post_ptr.marks_count, 1)


class SearchTests(BaseTest):
    def test_published_drug_is_found_by_title_body_indications(self):
        rebuild_index.Command().handle(interactive=False)

        drug = self.drug
        drug.status = super_models.POST_STATUS_PUBLISHED
        drug.title = 'аыпывапыврапврарвапрапр'
        drug.body = 'варвапрварварварвапрвапрв'
        drug.indications = 'аволдтрывалтплыовапг54нцпшдцатп'
        drug.save()

        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = drug.title
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertIn('Ничего не найдено', page)
        self.assertNotIn(drug.get_absolute_url(), page)

        update_index.Command().handle()

        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = drug.title
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertNotIn('Ничего не найдено', page)
        self.assertIn(drug.get_absolute_url(), page)


        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = drug.body
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertNotIn('Ничего не найдено', page)
        self.assertIn(drug.get_absolute_url(), page)

        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = drug.indications
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertNotIn('Ничего не найдено', page)
        self.assertIn(drug.get_absolute_url(), page)

    def test_published_comment_is_found_by_body_username(self):
        rebuild_index.Command().handle(interactive=False)

        comment = models.Comment.objects.create(
                post=self.drug,
                username='аывпывапварварвар',
                email='fdsfsd@sdgdfgdfg.ru',
                body='варвварправрвар',
                status=super_models.COMMENT_STATUS_PUBLISHED,
            )

        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = comment.body
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertIn('Ничего не найдено', page)

        update_index.Command().handle()

        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = comment.body
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertNotIn('Ничего не найдено', page)
        self.assertIn(comment.get_absolute_url(), page)

        page = self.app.get(reverse('main-page'))
        form = page.forms['search-form']
        form['q'] = comment.username
        page = form.submit()
        self.assertEqual(page.status_code, 200)
        self.assertIn(comment.get_absolute_url(), page)


"""
class ProzdoMiddlewareTests(BaseTest):
    def test_set_ip_middleware_works_as_expected(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        self.assertEqual(self.app.session.get('prozdo_key', None), None)

        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв'
        email = 'sdfgsdfgdsf@gdfgdfgd.ru'
        username = 'dfsgdfgsdfgsdfg'
        form['email'] = email
        form['username'] = username
        form['body'] = body
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.latest('created')
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        self.assertNotEqual(self.app.session.get('prozdo_key', None), None)
"""