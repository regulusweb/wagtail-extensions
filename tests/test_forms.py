from unittest.mock import Mock, patch

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


@patch('wagtail_extensions.forms.ContactForm.send_email')
@patch('wagtail_extensions.forms.ContactForm.get_to')
def test_save(mocked_get_to, mocked_send_email):
    form = ContactForm()
    form.cleaned_data = cleaned_data
    page = Mock()
    page.enquiry_email = 'e@e.com'
    form.save(page)

    mocked_get_to.assert_called_once_with(page)
    mocked_send_email.assert_called_once_with(
        mocked_get_to.return_value,
        'wagtail_extensions/email/subject.txt',
        'wagtail_extensions/email/message.txt',
        ['t@t.com']
    )
