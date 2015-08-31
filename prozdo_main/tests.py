from django_webtest import WebTest
from . import models
from django.core.urlresolvers import reverse
from django.conf import settings



class BaseTest(WebTest):
    def setUp(self):
        self.user = models.User.objects.create(username='asdgsdfhhfgdjfh', password='1234567', email='sdfgsdfg@sdfsdg.ru')
        self.user2 = models.User.objects.create(username='asssdfdsgdfg', password='1234567', email='dsgdfsgsdfg@dsfgsdg.ru')

        self.component = models.Component.objects.create(
            body='body',
            title = 'title_component',
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

    def test_comment_antispan_comment_with_errors_published_for_user(self):
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

        self.assertEqual(start_hist_count + 2, result_hist_count)

        comment = models.Comment.objects.latest('created')

        h = models.History.objects.latest('created')
        self.assertEqual(h.post, drug.post_ptr)
        self.assertEqual(h.comment, comment)
        self.assertEqual(h.mark, 4)
        self.assertEqual(comment.post_mark, 4)
        self.assertEqual(h.history_type, models.HISTORY_TYPE_POST_RATED)

        h = models.History.objects.get(post=drug.post_ptr, history_type=models.HISTORY_TYPE_COMMENT_CREATED)
        self.assertEqual(h.post, drug.post_ptr)
        self.assertEqual(h.comment, comment)
        self.assertEqual(h.mark, None)
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
