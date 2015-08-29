from django_webtest import WebTest
from . import models
from django.core.urlresolvers import reverse
from django.conf import settings



class BaseTest(WebTest):
    def setUp(self):
        self.user = models.User.objects.create(username='asdgsdfhhfgdjfh', password='1234567', email='sdfgsdfg@sdfsdg.ru')

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

