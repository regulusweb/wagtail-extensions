import datetime
import pytest
from unittest.mock import patch

from django.core.exceptions import ValidationError
from freezegun import freeze_time
from phonenumber_field.phonenumber import PhoneNumber

from wagtail.core.models import Page
from wagtail_extensions.blocks import (DepartmentBlock, LinkBlock,
                                       OpeningTimeBlock, OpeningTimesBlock,
                                       PhoneBlock)


@pytest.mark.django_db
@pytest.fixture
def page():
    # Homepage is created by Wagtail's initial migrations
    # But let's create our own child page for testing with.
    homepage = Page.objects.get(url_path='/home/')
    page = Page(title='A test page', slug="test")
    homepage.add_child(instance=page)
    return page


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


def test_link_block_with_url():
    block = LinkBlock()
    value = block.to_python({
        'link': [{'type': 'url', 'value': '/hello/'}]
    })

    assert value.link_url == '/hello/'
    assert value.link_text == '/hello/'


def test_link_block_with_url_and_text():
    block = LinkBlock()
    value = block.to_python({
        'text': 'Hello World',
        'link': [{'type': 'url', 'value': '/hello/'}]
    })
    assert value.link_url == '/hello/'
    assert value.link_text == 'Hello World'


def test_link_block_with_empty_string_text():
    block = LinkBlock()
    value = block.to_python({
        'text': '',
        'link': [{'type': 'url', 'value': '/hello/'}]
    })
    assert value.link_url == '/hello/'
    assert value.link_text == '/hello/'


def test_link_block_with_missing_streamblock():
    block = LinkBlock()
    value = block.to_python({
        'text': '',
        'link': []
    })
    assert value.link_url == ''
    assert value.link_text == ''


@pytest.mark.django_db
def test_link_block_with_page(page):
    block = LinkBlock()
    value = block.to_python({
        'link': [{'type': 'page', 'value': page.pk}]
    })

    assert value.link_url == page.url
    assert value.link_text == page.title


@pytest.mark.django_db
def test_link_block_with_page_and_text(page):
    block = LinkBlock()
    value = block.to_python({
        'text': 'Hello World',
        'link': [{'type': 'page', 'value': page.pk}]
    })
    assert value.link_url == page.url
    assert value.link_text == 'Hello World'


def test_link_block_clean_for_required():
    block = LinkBlock()
    value = block.to_python({
        'text': 'Hello World',
        'link': []      # This must not be empty if the field is required
    })
    with pytest.raises(ValidationError):
        block.clean(value)


def test_link_block_clean_for_not_required():
    block = LinkBlock(required=False)
    value = block.to_python({
        'text': 'Hello World',
        'link': []      # Can be empty if the field is not required
    })
    # This should not raise an exception
    block.clean(value)


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


def test_openingtime_block_to_python_empty():
    openingtime = OpeningTimeBlock()
    openingtime.to_python({'label': '', 'date': None, 'closed': False, 'start': None, 'end': None, 'weekday': ''})
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
