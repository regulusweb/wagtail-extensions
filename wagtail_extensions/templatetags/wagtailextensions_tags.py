from datetime import datetime
from urllib.parse import urlsplit

from django.template import Library, Node
from django.template.defaultfilters import escape, stringfilter
from django.utils import html, timezone

import bleach
from wagtailgeowidget.app_settings import (
    GEO_WIDGET_ZOOM,
    GOOGLE_MAPS_V3_APIKEY,
)


register = Library()


@register.inclusion_tag('wagtail_extensions/partials/map.html')
def map(location, zoom=GEO_WIDGET_ZOOM):
    return {
        'location': location,
        'zoom': zoom,
    }


@register.inclusion_tag('wagtail_extensions/partials/map_assets.html')
def map_assets():
    return {
        'api_key': GOOGLE_MAPS_V3_APIKEY,
    }


@register.filter
@stringfilter
def humanize_url(value):
    return urlsplit(value)[1]


@register.simple_tag
def humanize_date_range(start, end):
    day_fmt = '%d %b %Y'
    if start == end:
        return start.strftime(day_fmt)
    elif (start.month, start.year) == (end.month, end.year):
        start_fmt = '%d'
    else:
        start_fmt = '%d %b %Y'
    return "{} - {}".format(start.strftime(start_fmt), end.strftime(day_fmt))


@register.simple_tag
def block_method(block_value, method_name):
    method = getattr(block_value.block, method_name)
    if method:
        return method(block_value)
    else:
        return None


@register.inclusion_tag('wagtail_extensions/partials/track_form_submission.html')
def track_form_submission(request):
    submitted = request.session.get('enquiry_form_submitted', False)
    if submitted:
        # Remove the session variable
        del request.session['enquiry_form_submitted']
        try:
            submitted_time = datetime.strptime(submitted, '%Y-%m-%d %H:%M %z')
        except ValueError:
            return {'enquiry_form_submitted': False}

        if (timezone.now() - submitted_time).seconds < 60:
            return {'enquiry_form_submitted': True}

    return {'enquiry_form_submitted': False}


def page_menu_children(page, calling_page=None):
    children = page.get_children().live().in_menu()
    for child in children:
        child.active = (calling_page.url.startswith(child.url) if calling_page else False)
    return children


@register.inclusion_tag('wagtail_extensions/partials/menu.html', takes_context=True)
def menu(context, parent, calling_page=None):
    menuitems = page_menu_children(parent, calling_page)

    for menuitem in menuitems:
        menuitem.children = page_menu_children(menuitem, calling_page)

    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


@register.tag
def metablock(parser, token):
    """
    Remove newlines, excessive whitespace, and HTML tags; and escape the
    content of meta blocks.
    """
    nodelist = parser.parse(('endmetablock',))
    parser.delete_first_token()
    return MetaBlockNode(nodelist)


class MetaBlockNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        output = output.replace("\n", "")
        output = " ".join(output.split()).replace(" ,", ",").replace(" .", ".")
        output = html.strip_tags(unescape(output))
        return escape(output)


def unescape(text):
    return text.replace(
        "&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace(
        "&quot;", '"').replace("&#39;", "'")
