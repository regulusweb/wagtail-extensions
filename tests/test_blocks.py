from django.core.exceptions import ValidationError
from phonenumber_field.phonenumber import PhoneNumber
import pytest
from wagtail.wagtailcore.models import Page
from wagtail_extensions.blocks import DepartmentBlock, LinkBlock, PhoneBlock


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


def test_link_block_clean_neither_page_and_url():
    link = LinkBlock()
    with pytest.raises(ValidationError):
        link.clean({
            'text': 'A link',
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
