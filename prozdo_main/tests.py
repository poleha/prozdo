from django_webtest import WebTest
from . import models
from django.core.urlresolvers import reverse
from django.conf import settings
from allauth.account.models import EmailAddress, EmailConfirmation


class BaseTest(WebTest):
    def setUp(self):
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)

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
            self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)

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
            form['body'] = body
            page = form.submit()
            self.assertEqual(page.status_code, 302)
            comment = models.Comment.objects.all().latest('created')
            self.assertEqual(comment.body, body)
            self.assertEqual(comment.username, bad_username)
            self.assertEqual(comment.email, email)
            self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)

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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)

    def test_comment_antispan_comment_with_not_too_much_digits_in_body_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзыв1234567890123456789012345678901234567'
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)

    def test_comment_antispan_comment_with_too_much_eng_in_body_not_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзывzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)

    def test_comment_antispan_comment_with_not_too_much_eng_in_body_published_for_guest(self):
        drug = self.drug
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}))
        form = page.forms['comment-form']
        body = 'Привет, это хороший отзывzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)

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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)


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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)
        comment.status = models.COMMENT_STATUS_PUBLISHED
        comment.save()
        for k in range(10):
            models.History.save_history(post=comment.post, comment=comment, history_type=models.HISTORY_TYPE_COMMENT_RATED, ip='1.2.3.{0}'.format(k), session_key='fsdfsdfsdfsd34{0}'.format(k))

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u)
        form = page.forms['comment-form']
        username = settings.BAD_WORDS[0]
        form['email'] = email
        form['username'] = username
        form['body'] = body
        self.assertEqual(u.karm, 10)
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.body, body)
        self.assertEqual(comment.username, username)
        self.assertEqual(comment.email, email)
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)


    def test_comment_antispan_comment_with_errors_published_for_doctor(self):
        drug = self.drug
        u = self.user
        u.user_profile.role = models.USER_ROLE_DOCTOR
        u.user_profile.save()
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)



class HistoryTests(BaseTest):
    def test_comment_create_without_mark_for_drug(self):
        drug = self.drug
        user = self.user
        start_hist_count = models.History.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        result_hist_count = models.History.objects.all().count()
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
        self.assertEqual(h.history_type, models.HISTORY_TYPE_COMMENT_CREATED)


    def test_comment_create_and_save_and_post_mark_for_drug(self):
        drug = self.drug
        user = self.user
        start_hist_count = models.History.objects.all().count()


        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        form['post_mark'] = 4
        page = form.submit()

        result_hist_count = models.History.objects.all().count()

        self.assertEqual(start_hist_count + 1, result_hist_count)

        comment = models.Comment.objects.latest('created')

        h = models.History.objects.latest('created')
        self.assertEqual(h.post, drug.post_ptr)
        self.assertEqual(h.comment, comment)
        self.assertEqual(h.mark, 4)
        self.assertEqual(comment.post_mark, 4)
        self.assertEqual(h.history_type, models.HISTORY_TYPE_COMMENT_CREATED)



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
            ('comment-mark', 'comment-unmark', models.HISTORY_TYPE_COMMENT_RATED),
            ('comment-complain', 'comment-uncomplain', models.HISTORY_TYPE_COMMENT_COMPLAINT)
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
                start_hist_count = models.History.objects.all().count()
                page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user2)
                result_hist_count = models.History.objects.all().count()
                self.assertEqual(start_hist_count, result_hist_count)

    def test_user_and_guest_comment_mark_and_comment_unmark_and_comment_complain_and_comment_uncomplain(self):
        drug = self.drug
        users = (self.user, None)
        comment = self.comment

        for user in users:
            for action, cancel, history_type in self.comment_actions:
                start_hist_count = models.History.objects.all().count()

                params= {
                    'action': action,
                    'pk': comment.pk,
                }
                page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
                h_mark = models.History.objects.latest('created')
                self.assertEqual(h_mark.post, drug.post_ptr)
                self.assertEqual(h_mark.comment, comment)
                self.assertEqual(h_mark.history_type, history_type)
                result_hist_count = models.History.objects.all().count()
                self.assertEqual(start_hist_count + 1, result_hist_count)

                params= {
                    'action': cancel,
                    'pk': comment.pk,
                }
                page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
                result_hist_count = models.History.objects.all().count()
                self.assertEqual(start_hist_count, result_hist_count)

    def test_user_cant_unmark_and_uncomplain_not_his_comment(self):
        drug = self.drug
        comment = self.comment
        user = self.user
        for action, cancel, history_type in self.comment_actions:
            start_hist_count = models.History.objects.all().count()

            params= {
                'action': action,
                'pk': comment.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            h_mark = models.History.objects.latest('created')
            self.assertEqual(h_mark.post, drug.post_ptr)
            self.assertEqual(h_mark.comment, comment)
            self.assertEqual(h_mark.history_type, history_type)
            result_hist_count = models.History.objects.all().count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

            params= {
                'action': cancel,
                'pk': comment.pk,
            }
            self.renew_app()
            page = self.app.post(reverse('history-ajax-save'), params=params, user=self.user2)
            result_hist_count = models.History.objects.all().count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

    def test_guest_cant_unmark_and_uncomplain_not_his_comment(self):
        drug = self.drug
        comment = self.comment
        comment.ip = '111.222.333.444'
        comment.save()
        user = self.user
        for action, cancel, history_type in self.comment_actions:
            start_hist_count = models.History.objects.all().count()

            params= {
                'action': action,
                'pk': comment.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            h_mark = models.History.objects.latest('created')
            self.assertEqual(h_mark.post, drug.post_ptr)
            self.assertEqual(h_mark.comment, comment)
            self.assertEqual(h_mark.history_type, history_type)
            result_hist_count = models.History.objects.all().count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

            params= {
                'action': cancel,
                'pk': comment.pk,
            }
            self.renew_app()
            page = self.app.post(reverse('history-ajax-save'), params=params, user=None)
            result_hist_count = models.History.objects.all().count()
            self.assertEqual(start_hist_count + 1, result_hist_count)



    def test_user_and_guest_can_mark_and_unmark_drug(self):
        drug = self.drug

        users = (self.user, None)

        for user in users:
            self.renew_app()
            start_hist_count = models.History.objects.all().count()

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
            self.assertEqual(h.history_type, models.HISTORY_TYPE_POST_RATED)
            result_hist_count = models.History.objects.all().count()
            self.assertEqual(start_hist_count + 1, result_hist_count)

            params= {
                'action': 'post-unmark',
                'pk': drug.pk,
            }
            page = self.app.post(reverse('history-ajax-save'), params=params, user=user)
            result_hist_count = models.History.objects.all().count()
            self.assertEqual(start_hist_count, result_hist_count)


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
                status=models.COMMENT_STATUS_PUBLISHED,

            )
            comments0.append(comment)

        for k in range(settings.POST_COMMENTS_PAGE_SIZE * 2 + 1):
            comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпиорвполривапрва-level1-{0}'.format(k),
                status=models.COMMENT_STATUS_PUBLISHED,
                parent=comments0[k]

            )
            comments1.append(comment)

        for k in range(settings.POST_COMMENTS_PAGE_SIZE * 2 + 1):
            comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпиорвполривапрва-level2-{0}'.format(k),
                status=models.COMMENT_STATUS_PUBLISHED,
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



class CommentConfirmationTests(BaseTest):
    def test_comment_confirm_message_is_sent_for_published_guest_and_comment_can_be_activated(self):
        mail_count_start = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.all().count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

        mail = models.Mail.objects.latest('created')
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.assertIn(comment.get_confirm_url(), mail.body_html)
        page = self.app.get(comment.get_confirm_url())
        comment = comment.saved_version
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)

    def test_comment_comment_cant_be_activated_with_wrong_key(self):
        mail_count_start = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.all().count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

        mail = models.Mail.objects.latest('created')
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.assertIn(comment.get_confirm_url(), mail.body_html)
        url = settings.SITE_URL + reverse('comment-confirm', kwargs={'comment_pk': comment.pk, 'key': comment.key + 'z'})
        page = self.app.get(url)
        comment = comment.saved_version
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)


    def test_guest_comment_can_confirm_own_comment_by_link(self):
        mail_count_0 = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        page = self.app.post(reverse('comment-get-confirm-form-ajax'), {'pk': comment.pk})
        form = page.form
        form['email'] = email
        form['comment'] = comment.pk
        page = form.submit()
        comment = comment.saved_version
        mail_count_2 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_1 + 1, mail_count_2)


    def test_user_comment_with_approved_mail_is_approved(self):
        user = self.user
        mail_count_start = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.all().count()
        self.assertEqual(mail_count_start, mail_count_end)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)


    def test_user_comment_with_unapproved_mail_is_unapproved_but_approves_on_user_mail_approve(self):
        user = self.user2
        mail_count_0 = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.email_adress2.verified = True
        self.email_adress2.save()
        comment = comment.saved_version
        self.assertEqual(comment.confirmed, True)

    def test_user_comment_with_unapproved_mail_is_unapproved_but_approves_on_comment_by_mail_approve(self):
        user = self.user2
        email = user.emailaddress_set.all()[0]
        self.assertEqual(email.verified, False)
        mail_count_start = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}), user=user)
        form = page.forms['comment-form']
        form['body'] = 'Привет, это вот мой коммент'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_end = models.Mail.objects.all().count()
        self.assertEqual(mail_count_start + 1, mail_count_end)

        mail = models.Mail.objects.latest('created')
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        self.assertIn(comment.get_confirm_url(), mail.body_html)
        page = self.app.get(comment.get_confirm_url())
        comment = comment.saved_version
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)
        email = user.emailaddress_set.all()[0]
        self.assertEqual(email.verified, True)

    def test_user_with_approved_mail_approve_comments_by_click(self):
        user = self.user
        mail_count_0 = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = user.email
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        page = self.app.post(reverse('comment-get-confirm-form-ajax'), {'pk': comment.pk}, user=user)
        #form = page.form
        #form['email'] = email
        #form['pk'] = comment.pk
        #page = form.submit()
        comment = comment.saved_version
        mail_count_2 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_1, mail_count_2)
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, True)

    def test_guest_comment_cant_confirm_own_comment_by_link_with_wrong_mail(self):
        mail_count_0 = models.Mail.objects.all().count()
        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': self.drug.pk}))
        form = page.forms['comment-form']
        email = 'dfjklsfdklsdghjkdfh@kjlgfsdgjksdfgh.com'
        form['body'] = 'Привет, это вот мой коммент'
        form['email'] = email
        form['username'] = 'Саша'
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        mail_count_1 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_0 + 1, mail_count_1)
        comment = models.Comment.objects.latest('created')
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.confirmed, False)
        page = self.app.post(reverse('comment-get-confirm-form-ajax'), {'pk': comment.pk})
        form = page.form
        form['email'] = 'sdfsdgjkshne5iu4gh@dsfsdf.ru'
        form['comment'] = comment.pk
        page = form.submit()
        comment = comment.saved_version
        mail_count_2 = models.Mail.objects.all().count()
        self.assertEqual(mail_count_1, mail_count_2)



class PublishedModelMixinTests(BaseTest):
    def test_comment_takes_publish_time_on_publish_only(self):
        comment = models.Comment.objects.create(
                post=self.drug,
                username='gdfsgsdfgsdfg',
                email='fdsfsd@sdgdfgdfg.ru',
                body='авырлпоырваыпdsgdsfgиорвполривапрва-dsfgsdfffffffffffffffffglevelsdfgfsd',
                status=models.COMMENT_STATUS_PENDING_APPROVAL,
            )

        self.assertEqual(comment.status, models.COMMENT_STATUS_PENDING_APPROVAL)
        self.assertEqual(comment.published, None)

        comment.status = models.COMMENT_STATUS_PUBLISHED
        comment.save()

        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertNotEqual(comment.published, None)
        published = comment.published

        comment.save()

        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        self.assertEqual(comment.published, published)


    def test_drug_takes_publish_time_on_publish_only(self):
        drug = models.Drug.objects.create(
            title='title_dfgdsfgdrug',
            body='bodsfgdfgdy',

          )

        self.assertEqual(drug.status, models.POST_STATUS_PROJECT)
        self.assertEqual(drug.published, None)

        drug.status = models.POST_STATUS_PUBLISHED
        drug.save()

        self.assertEqual(drug.status, models.POST_STATUS_PUBLISHED)
        self.assertNotEqual(drug.published, None)
        published = drug.published

        drug.save()

        self.assertEqual(drug.status, models.POST_STATUS_PUBLISHED)
        self.assertEqual(drug.published, published)

class CommentMessagesTest(BaseTest):
    def setUp(self):
        super().setUp()

    def test_user_gets_email_when_his_approved_comment_is_answered(self):
        mails_count0 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        mails_count1 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()

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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        mails_count2 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        self.assertEqual(mails_count1 + 1, mails_count2)



    def test_user_doesnt_get_email_when_his_unapproved_comment_is_answered(self):
        mails_count0 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        mails_count1 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()

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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        mails_count2 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        self.assertEqual(mails_count1, mails_count2)

    def test_user_doesnt_get_email_when_his_approved_comment_is_answered_by_himself(self):
        mails_count0 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
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
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        mails_count1 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()

        self.assertEqual(mails_count0, mails_count1)

        page = self.app.get(reverse('post-detail-pk', kwargs={'pk': drug.pk}), user=u1)
        form = page.forms['comment-form']
        body = 'Привет, это хороший коммент'
        form['body'] = body
        form['parent'] = comment.pk
        page = form.submit()
        self.assertEqual(page.status_code, 302)
        comment = models.Comment.objects.all().latest('created')
        self.assertEqual(comment.confirmed, True)
        self.assertEqual(comment.status, models.COMMENT_STATUS_PUBLISHED)
        mails_count2 = models.Mail.objects.filter(mail_type=models.MAIL_TYPE_ANSWER_TO_COMMENT).count()
        self.assertEqual(mails_count1, mails_count2)
