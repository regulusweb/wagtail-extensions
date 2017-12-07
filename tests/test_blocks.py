import datetime

from django.core.exceptions import ValidationError
from freezegun import freeze_time
from phonenumber_field.phonenumber import PhoneNumber
import pytest
from wagtail.wagtailcore.models import Page
from wagtail_extensions.blocks import (DepartmentBlock, LinkBlock,
                                       OpeningTimeBlock, PhoneBlock)


def test_department_block_clean_invalid():
    department = DepartmentBlock()
    with pytest.raises(ValidationError):
        department.clean({})


def test_department_block_clean_valid_with_both():
    department = DepartmentBlock()
    department.clean({'name':'Test', 'email':'foo@foo.com', 'phones': ['+447528712345']})


def test_department_block_to_python_empty():
    department = DepartmentBlock()
    department.to_python({})


def test_department_block_to_python_strip_empty_phonenumbers():
    department = DepartmentBlock()
    value = department.get_prep_value({'phones': ['', '+447528712345', '']})
    assert value['phones'] == ['+447528712345']


@pytest.mark.django_db
def test_link_block_clean_just_page():
    link = LinkBlock()
    link.clean({'text': 'A link', 'page': 1})


def test_link_block_clean_just_url():
    link = LinkBlock()
    link.clean({'text': 'A link', 'absolute_url': 'https://foo.com'})


def test_link_block_clean_both_page_and_url():
    link = LinkBlock()
    with pytest.raises(ValidationError):
        link.clean({
            'text': 'A link',
            'page': '1',
            'absolute_url': 'https://foo.com',
        })


@pytest.mark.django_db
def test_link_block_to_python_page():
    link = LinkBlock()
    value = link.to_python({'page': 2})
    assert value['url'] == "/"


def test_link_block_to_python_absolute_url():
    link = LinkBlock()
    value = link.to_python({'absolute_url': 'http://test.com/'})
    assert value['url'] == "http://test.com/"


@pytest.mark.django_db
def test_link_block_to_python_page_and_absolute_url():
    link = LinkBlock()
    value = link.to_python({'page': 2, 'absolute_url': 'http://test.com/'})
    assert value['url'] == "/"


def test_link_block_to_python_nothing():
    link = LinkBlock()
    value = link.to_python({})
    assert 'url' not in value


def test_link_block_get_context_no_url():
    link = LinkBlock()
    ctx = link.get_context({})
    assert ctx['has_url'] == False


def test_link_block_get_context_with_url():
    link = LinkBlock()
    ctx = link.get_context({'url': 'some url'})
    assert ctx['has_url'] == True


@freeze_time("2017-01-01")
def test_openingtime_block_clean_date_in_past():
    openingtime = OpeningTimeBlock()
    with pytest.raises(ValidationError):
        openingtime.clean({'date': '2016-01-01'})


def test_openingtime_block_clean_end_before_start():
    openingtime = OpeningTimeBlock()
    with pytest.raises(ValidationError):
        openingtime.clean({'start': '20:00', 'end': '08:00', 'weekday': '1'})


def test_openingtime_block_clean_no_weekday_or_date():
    openingtime = OpeningTimeBlock()
    with pytest.raises(ValidationError):
        openingtime.clean({'start': '20:00', 'end': '08:00'})


@freeze_time("2017-01-01")
def test_openingtime_block_clean_valid():
    openingtime = OpeningTimeBlock()
    openingtime.clean({'start': '08:00', 'end': '20:00', 'date': '2017-01-01'})


def test_openingtime_block_get_context_no_weekday():
    openingtime = OpeningTimeBlock()
    openingtime.to_python({'value': {}})
    # Pass without errors


def test_openingtime_block_get_context_public():
    openingtime = OpeningTimeBlock()
    value = openingtime.to_python({'weekday': 7})
    assert value['specific'] == True


@freeze_time("2017-01-01")
def test_openingtime_block_to_python_next_date():
    openingtime = OpeningTimeBlock()
    value = openingtime.to_python({'weekday': 4})
    # The first thursday after today (frozen above)
    assert value['next_date'] == datetime.date(2017, 1, 6)


def test_openingtime_block_to_python_no_weekday():
    openingtime = OpeningTimeBlock()
    openingtime.to_python({})
    # Pass without error


def test_openingtime_block_to_python_cast_weekday():
    openingtime = OpeningTimeBlock()
    value = openingtime.to_python({'weekday': '5'})
    assert value['weekday'] == 5


def test_openingtime_block_to_python_public_label():
    openingtime = OpeningTimeBlock()
    value = openingtime.to_python({'weekday': '7'})
    assert value['label'] == OpeningTimeBlock.PUBLIC_LABEL


def test_openingtime_block_to_python_public_with_label():
    openingtime = OpeningTimeBlock()
    label = 'Easter sunday'
    value = openingtime.to_python({'weekday': '7', 'label': label})
    assert value['label'] == label


def test_phone_block_get_prep_value():
    phone = PhoneBlock()
    number = PhoneNumber.from_string('+447528712345')
    number_str = phone.get_prep_value(number)
    assert number_str == '+447528712345'


def test_phone_block_to_python():
    phone = PhoneBlock()
    number = phone.to_python('+447528712345')
    assert number == PhoneNumber.from_string('+447528712345')


def test_phone_block_to_python_empty():
    phone = PhoneBlock()
    assert phone.to_python('') == ''
