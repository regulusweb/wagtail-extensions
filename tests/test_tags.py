from datetime import timedelta
from django.utils import timezone

from wagtail_extensions.templatetags.wagtailextensions_tags import (
    bleachclean, track_form_submission)


def test_bleanclean_cleandata():
    cleaned = bleachclean('Hello')

    assert cleaned == 'Hello'


def test_bleanclean_strips():
    cleaned = bleachclean('<script>evil</script>')

    assert cleaned == 'evil'


def test_track_form_submission(rf):
    request = rf.get('/')
    request.session = {
        'enquiry_form_submitted': timezone.now().strftime('%Y-%m-%d %H:%M')
    }

    ctx = track_form_submission(request)

    assert ctx == {'enquiry_form_submitted': True}
    assert request.session == {}


def test_track_form_submission_expired(rf):
    request = rf.get('/')
    request.session = {
        # this was submitted too long ago to qualify
        'enquiry_form_submitted': (timezone.now() - timedelta(seconds=3600)).strftime('%Y-%m-%d %H:%M')
    }

    ctx = track_form_submission(request)

    assert ctx == {'enquiry_form_submitted': False}
    assert request.session == {}


def test_track_form_submission_no_submission(rf):
    request = rf.get('/')
    request.session = {}

    ctx = track_form_submission(request)

    assert ctx == {'enquiry_form_submitted': False}


def test_track_form_invalid_session_data(rf):
    request = rf.get('/')
    request.session = {
        # this was submitted too long ago to qualify
        'enquiry_form_submitted': 'this is not a valid timestamp'
    }

    ctx = track_form_submission(request)

    assert ctx == {'enquiry_form_submitted': False}
