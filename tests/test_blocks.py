import datetime
from unittest.mock import patch

from django.core.exceptions import ValidationError
from freezegun import freeze_time
from phonenumber_field.phonenumber import PhoneNumber
import pytest
from wagtail.wagtailcore.models import Page
from wagtail_extensions.blocks import (DepartmentBlock, LinkBlock,
                                       OpeningTimeBlock, OpeningTimesBlock,
                                       PhoneBlock)


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


def test_openingtime_block_single_date_empty():
    assert OpeningTimeBlock.single_date({}) == False


def test_openingtime_block_single_date_with_date():
    assert OpeningTimeBlock.single_date({'date': 'some date'}) == True


def test_openingtime_block_single_date_public():
    assert OpeningTimeBlock.single_date({'weekday': 7}) == True


def test_openingtime_block_next_date_empty():
    assert OpeningTimeBlock.next_date({}) is None


@freeze_time("2017-12-13")
def test_openingtime_block_next_date_today():
    assert OpeningTimeBlock.next_date({'weekday': 2}) == datetime.date(2017, 12, 13)


@freeze_time("2017-12-13")
def test_openingtime_block_next_date_sunday():
    assert OpeningTimeBlock.next_date({'weekday': 6}) == datetime.date(2017, 12, 17)


@freeze_time("2017-12-13")
def test_openingtime_block_next_date_public():
    assert OpeningTimeBlock.next_date({'weekday': 7}) is None


def test_openingtimes_block_time_keyfunc_specific():
    openingtime = OpeningTimeBlock()
    value = openingtime.to_python({})
    with patch.object(openingtime, 'single_date', return_value=True):
        out = OpeningTimesBlock.time_keyfunc(value)
    assert out is value


def test_openingtimes_block_time_keyfunc_non_specific():
    value = OpeningTimeBlock().to_python({'closed': False, 'start': '5:00', 'end': '10:00'})
    out = OpeningTimesBlock.time_keyfunc(value)
    assert out == (False, datetime.time(5), datetime.time(10))


@patch('wagtail_extensions.blocks.groupby')
def test_openingtimes_block_group_times(mocked_groupby):
    value = {}
    mocked_groupby.return_value = [('first', [1, 4, 5]), ('second', [7, 10])]
    out = OpeningTimesBlock.group_times(value)

    assert out == [[1, 4, 5], [7, 10]]
    mocked_groupby.assert_called_once_with(value, OpeningTimesBlock.time_keyfunc)


def test_openingtimes_block_get_time_for_date_empty():
    assert OpeningTimesBlock.get_time_for_date(None, None) is None


def test_openingtimes_block_get_time_for_date_no_times():
    assert OpeningTimesBlock.get_time_for_date({}, datetime.date(2017, 12, 10)) is None


def test_openingtimes_block_get_time_for_date_times_date():
    match = {'date': datetime.date(2017, 12, 10)}
    value = {
        'times': [
            {'weekday': 4},
            match,
        ],
    }
    assert OpeningTimesBlock.get_time_for_date(value, datetime.date(2017, 12, 10)) == match


def test_openingtimes_block_get_time_for_date_times_weekday():
    match = {'weekday': 6}
    value = {
        'times': [
            {'weekday': 4},
            {'date': datetime.date(2017, 12, 10)},
            match,
        ],
    }
    assert OpeningTimesBlock.get_time_for_date(value, datetime.date(2017, 12, 17)) == match


def test_openingtimes_block_get_time_for_date_times_no_match():
    value = {
        'times': [
            {'weekday': 4},
            {'date': datetime.date(2017, 12, 10)},
            {'weekday': 2},
        ],
    }
    assert OpeningTimesBlock.get_time_for_date(value, datetime.date(2017, 12, 17)) is None


@freeze_time('2017-06-28')
def test_openingtimes_block_opening_today():
    openingtimes = OpeningTimesBlock
    with patch.object(openingtimes, 'get_time_for_date') as mocked_get:
        value = 'test'
        out = openingtimes.opening_today(value)
        mocked_get.assert_called_once_with(value, datetime.date(2017, 6, 28))
        assert out == mocked_get.return_value


def test_openingtimes_block_get_context():
    openingtimes = OpeningTimesBlock()
    value = {'times': [1, 5, 10]}
    with patch.object(openingtimes, 'group_times') as mocked_group,\
          patch.object(openingtimes, 'opening_today') as mocked_today:
        ctx = openingtimes.get_context(value)
        mocked_group.assert_called_once_with([1, 5, 10])
        mocked_today.assert_called_once_with(value)
        assert ctx['times'] == mocked_group.return_value
        assert ctx['today'] == mocked_today.return_value


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
