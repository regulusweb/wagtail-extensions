from wagtail.contrib.settings.models import BaseSetting
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore import fields

from . import blocks


class LinksSetting(BaseSetting):

    class Meta:
        abstract = True

    links = fields.StreamField([
        ('link', blocks.LinkBlock()),
    ])

    panels = (
        StreamFieldPanel('links'),
    )
