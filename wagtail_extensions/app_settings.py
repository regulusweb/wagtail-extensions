from django.conf import settings


GEO_WIDGET_DEFAULT_LOCATION = getattr(settings, 'GEO_WIDGET_DEFAULT_LOCATION', {'lat': -1.3, 'lng': 36.8})
GEO_WIDGET_ZOOM = getattr(settings, 'GEO_WIDGET_ZOOM', 10)

SOCIAL_MEDIA_TYPES = getattr(settings, 'SOCIAL_MEDIA_TYPES', (
    ('facebook', 'Facebook'),
    ('twitter', 'Twitter'),
    ('instagram', 'Instagram'),
    ('linkedin', 'LinkedIn'),
))
