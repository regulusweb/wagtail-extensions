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
        location = self.primary_location
        if location:
            departments = location.value.get('departments', [])
            return utils.first_true(departments, lambda x: x.get('primary') == True)
        else:
            return None

    @property
    def primary_phone(self):
        department = self.primary_department
        if department:
            phones = self.primary_department.get('phones', [])
            return utils.nth(phones, 0)
        else:
            return None
