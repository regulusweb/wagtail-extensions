from unittest.mock import Mock

from django.core import mail

from wagtail_extensions.forms import ContactForm


cleaned_data = {
    'email': 't@t.com',
    'message': 'Hi',
    'name': 'test',
    'subject_prefix': 'Admin'
}


def test_email_subject_prefix_added_to_ctx():
    form = ContactForm()
    form.cleaned_data = cleaned_data

    ctx = form.get_email_context()

    assert ctx['subject_prefix'] == 'Admin'


def test_go_to_with_enquiryemail():
    form = ContactForm()
    page = Mock()
    page.enquiry_email = 'e@e.com'
    to = form.get_to(page)

    assert to == ['e@e.com']


def test_go_to_without_enquiryemail():
    form = ContactForm()
    page = Mock()
    page.enquiry_email = ''
    to = form.get_to(page)

    assert to == ['admin@localhost.com']


def test_save():
    form = ContactForm()
    form.cleaned_data = cleaned_data
    page = Mock()
    page.enquiry_email = 'e@e.com'
    form.save(page)

    assert len(mail.outbox) == 1
