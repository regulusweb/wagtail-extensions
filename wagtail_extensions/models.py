from wagtail.contrib.settings.models import BaseSetting
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore import blocks, fields

from . import blocks as extension_blocks


class LinksSetting(BaseSetting):

    class Meta:
        abstract = True

    links = fields.StreamField([
        ('link', extension_blocks.LinkBlock()),
    ])

    panels = (
        StreamFieldPanel('links'),
    )


class ContactDetailsSetting(BaseSetting):

    class Meta:
        abstract = True

    locations = fields.StreamField([
        ('location', extension_blocks.LocationBlock()),
    ])

    panels = (
        StreamFieldPanel('locations'),
    )
