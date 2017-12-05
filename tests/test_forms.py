from unittest.mock import Mock

from django.core import mail
from django.test import TestCase

from wagtail_extensions.forms import ContactForm


class ContactFormTestCase(TestCase):

    valid_data = {'name': 'test', 'email': 't@t.com', 'message': 'Hi'}

    def test_required_fields(self):
        form = ContactForm()
        self.assertTrue(
            all([
                form.fields['email'].required,
                form.fields['name'].required,
                form.fields['message'].required
            ])
        )

    def test_email_subject_prefix_added_to_ctx(self):
        form = ContactForm(data=self.valid_data.copy())
        form.is_valid()
        ctx = form.get_email_context()
        self.assertEqual(ctx['subject_prefix'], 'Admin')

    def test_form_valid(self):
        form = ContactForm(data=self.valid_data.copy())
        self.assertTrue(form.is_valid())

    def test_send_email(self):
        data = self.valid_data.copy()
        data['message'] = 'Hello good people'
        form = ContactForm(data=data)
        form.is_valid()  # trigger to populate cleaned_data
        reply_to = [form.cleaned_data['email']]
        form.send_email(['to@g.com'], form.subject_template, form.txt_template, reply_to)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Hello good people', mail.outbox[0].body)

    def test_go_to_with_enquiryemail(self):
        form = ContactForm()
        page = Mock()
        page.enquiry_email = 'e@e.com'
        to = form.get_to(page)
        self.assertEqual(to, ['e@e.com'])

    def test_go_to_without_enquiryemail(self):
        form = ContactForm()
        page = Mock()
        page.enquiry_email = ''
        to = form.get_to(page)
        self.assertEqual(to, ['admin@localhost.com'])

    def test_save(self):
        form = ContactForm()
        form.cleaned_data = self.valid_data.copy()
        page = Mock()
        page.enquiry_email = 'e@e.com'
        form.save(page)
        self.assertEqual(len(mail.outbox), 1)
