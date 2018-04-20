import datetime
import pytest
from unittest import mock

from freezegun import freeze_time

from wagtail.core.models import Site
from wagtail_extensions.forms import ContactForm
from wagtail_extensions.mixins import ContactMixin
from wagtail_extensions.models import ContactSubmission

from tests.testproject.testapp.models import ContactDetailsTestSetting


@pytest.mark.django_db
@pytest.fixture
def contact_setting():
    setting = ContactDetailsTestSetting()
    setting.site = Site.objects.get(is_default_site=True)
    setting.save()
    return setting


@pytest.mark.django_db
def test_contact_details_primary_location_empty(contact_setting):
    assert contact_setting.primary_location == None


@pytest.mark.django_db
def test_contact_details_primary_location_found(contact_setting):
    match = {'primary': True, 'name': 'Test location'}
    contact_setting.locations = [
        ('location', {'primary': False}),
        ('location', {}),
        ('location', match),
    ]
    assert contact_setting.primary_location.value['name'] == 'Test location'


@pytest.mark.django_db
def test_contact_details_primary_department_empty(contact_setting):
    assert contact_setting.primary_department == None


@pytest.mark.django_db
def test_contact_details_primary_department_found(contact_setting):
    match = {'primary': True}
    contact_setting.locations = [
        ('location', {
            'primary': True,
            'departments': [
                {'primary': False},
                match,
                {},
            ],
        }),
    ]
    assert contact_setting.primary_department == match


@pytest.mark.django_db
def test_contact_details_primary_phone_empty(contact_setting):
    assert contact_setting.primary_phone == None


@pytest.mark.django_db
def test_contact_details_primary_phone_found(contact_setting):
    contact_setting.locations = [
        ('location', {
            'primary': True,
            'departments': [
                {'primary': True, 'phones': ['+447528712345', '+447528712346', '+447528712347']},
            ],
        })
    ]
    assert contact_setting.primary_phone == '+447528712345'


@pytest.mark.django_db
def test_contact_details_primary_opening_times_found(contact_setting):
    times = {'times': [{'label': 'My time'}]}

    contact_setting.locations = [
        ('location', {
            'primary': True,
            'opening_times': times,
        })
    ]

    assert contact_setting.primary_opening_times == times


@pytest.mark.django_db
def test_contact_details_primary_opening_times_none(contact_setting):
    assert contact_setting.primary_opening_times == None


@freeze_time("2017-06-06")
@pytest.mark.django_db
def test_contact_details_primary_opening_today_none(contact_setting):
    contact_setting.locations = [
        ('location', {
            'primary': True,
            'opening_times': {'times': [
                {'weekday': 3},
                {'date': datetime.date(2017, 6, 5)},
                {'weekday': 7},
            ]},
        })
    ]

    contact_setting.save()
    contact_setting.refresh_from_db()

    assert contact_setting.primary_opening_today == None


@freeze_time("2017-06-06")
@pytest.mark.django_db
def test_contact_details_primary_opening_today_date(contact_setting):
    match = datetime.date(2017, 6, 6)

    contact_setting.locations = [
        ('location', {
            'primary': True,
            'opening_times': {'times': [
                {'weekday': 1},
                {'date': match},
            ]},
        })
    ]

    contact_setting.save()
    contact_setting.refresh_from_db()

    assert contact_setting.primary_opening_today['date'] == match


@freeze_time("2017-06-10")
@pytest.mark.django_db
def test_contact_details_primary_opening_today_weekday(contact_setting):
    match = 5

    contact_setting.locations = [
        ('location', {
            'primary': True,
            'opening_times': {'times': [
                {'weekday': 3},
                {'date': datetime.date(2017, 6, 5)},
                {'weekday': 5},
            ]},
        })
    ]

    contact_setting.save()
    contact_setting.refresh_from_db()

    assert contact_setting.primary_opening_today['weekday'] == match


@pytest.mark.django_db
def test_contact_details_primary_opening_today_no_location(contact_setting):
    assert contact_setting.primary_opening_today == None


@freeze_time("2017-12-05")
def test_contact_details_get_opening_today_cache_key():
    out = ContactDetailsTestSetting.get_opening_today_cache_key()
    assert out == 'wagtail_extensions_opening_today_20171205'


@pytest.mark.django_db
def test_store_submission(rf):
    form_data = {
        'name': 'Alice',
        'email': 'alice@example.com',
        'message': 'Where is Bob?',
        'foobar': '',   # Honeypot field
    }
    request = rf.post('/', form_data)
    # Fake messages handler
    request._messages = mock.MagicMock()
    request.session = mock.MagicMock()
    page = ContactMixin()
    page.url = '/'
    page.serve(request)
    submission = ContactSubmission.objects.first()
    del form_data['foobar']
    assert submission.data == form_data


@pytest.mark.django_db
def test_disable_store_submission(rf):
    form_data = {
        'name': 'Alice',
        'email': 'alice@example.com',
        'message': 'Where is Bob?',
        'foobar': '',   # Honeypot field
    }
    request = rf.post('/', form_data)
    # Fake messages handler
    request._messages = mock.MagicMock()
    request.session = mock.MagicMock()
    page = ContactMixin()
    page.url = '/'
    page.store_submissions = False
    page.serve(request)
    assert ContactSubmission.objects.count() == 0


@pytest.mark.django_db
def test_submission_saves_tracker_to_session(rf):
    form_data = {
        'name': 'Alice',
        'email': 'alice@example.com',
        'message': 'Where is Bob?',
        'foobar': '',   # Honeypot field
    }
    request = rf.post('/', form_data)
    request.session = {}
    request._messages = mock.MagicMock()

    page = ContactMixin()
    page.url = '/'
    page.serve(request)
    assert 'enquiry_form_submitted' in request.session
