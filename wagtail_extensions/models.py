from wagtail.contrib.settings.models import BaseSetting
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore import blocks, fields

from . import blocks as extension_blocks
from . import utils


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

    @property
    def primary_location(self):
        return utils.first_true(self.locations, lambda x: x.value.get('primary') == True)

    @property
    def primary_department(self):
        departments = self.primary_location.value.get('departments', [])
        return utils.first_true(departments, lambda x: x.get('primary') == True)
