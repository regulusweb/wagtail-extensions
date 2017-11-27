from django.template import Library
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
