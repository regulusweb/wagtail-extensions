import pytest
from datetime import timedelta
from django.utils import timezone

from wagtail.core.models import Page
from wagtail_extensions.templatetags.wagtailextensions_tags import (
    bleachclean, page_menu_children, track_form_submission, menu)


@pytest.mark.django_db
@pytest.fixture
def page_tree():
    # Homepage is created by Wagtail's initial migrations
    # But let's create our own child page for testing with.
    root = Page.objects.get(url_path='/home/')
    page_1 = Page(title='A test page 1', slug="test_1", show_in_menus=True, live=True)
    page_2 = Page(title='A test page 2', slug="test_2", show_in_menus=True, live=True)
    page_3 = Page(title='A test page 3', slug="test_3", show_in_menus=False, live=True)
    page_4 = Page(title='A test page 4', slug="test_4", show_in_menus=True, live=False)
    page_1_1 = Page(title='A test child of page 1', slug="child_1", show_in_menus=True, live=True)
    root.add_child(instance=page_1)
    root.add_child(instance=page_2)
    root.add_child(instance=page_3)
    root.add_child(instance=page_4)
    page_1.add_child(instance=page_1_1)
    pages = [page_1, page_2, page_3, page_4, page_1_1]
    return (root, pages)


def test_bleanclean_cleandata():
    cleaned = bleachclean('Hello')

    assert cleaned == 'Hello'


def test_bleanclean_strips():
    cleaned = bleachclean('<script>evil</script>')

    assert cleaned == 'evil'


def test_track_form_submission(rf):
    request = rf.get('/')
    request.session = {
        'enquiry_form_submitted': timezone.now().strftime('%Y-%m-%d %H:%M %z')
    }

    ctx = track_form_submission(request)

    assert ctx == {'enquiry_form_submitted': True}
    assert request.session == {}


def test_track_form_submission_expired(rf):
    request = rf.get('/')
    request.session = {
        # this was submitted too long ago to qualify
        'enquiry_form_submitted': (timezone.now() - timedelta(seconds=3600)).strftime('%Y-%m-%d %H:%M %z')
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


@pytest.mark.django_db
def test_page_menu_children(page_tree):
    root, pages = page_tree
    out = page_menu_children(root, calling_page=None)
    assert len(out) == 2
    assert out[0].slug == 'test_1'
    assert out[0].active == False
    assert out[1].slug == 'test_2'
    assert out[1].active == False


@pytest.mark.django_db
def test_page_menu_children(page_tree):
    root, pages = page_tree
    out = page_menu_children(root, calling_page=pages[0])
    assert len(out) == 2
    assert out[0].active == True
    assert out[1].active == False


@pytest.mark.django_db
def test_menu_tag(page_tree, rf):
    root, pages = page_tree
    request = rf.get('test_1')
    out = menu({'request': request}, root, pages[0])
    assert out['calling_page'] == pages[0]
    assert out['request'] == request
    assert out['menuitems'][0].slug == 'test_1'
    assert out['menuitems'][0].active == True
    assert out['menuitems'][1].slug == 'test_2'
    assert len(out['menuitems'][0].children) == 1
    assert out['menuitems'][0].children[0].slug == 'child_1'
