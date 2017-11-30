from urllib.parse import urlsplit

from django.template import Library
from django.template.defaultfilters import stringfilter

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
