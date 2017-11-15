import pytest
from wagtail.wagtailcore.models import Site

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
