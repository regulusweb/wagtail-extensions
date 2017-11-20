from datetime import date

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
        return utils.true_or_nth(self.locations, lambda x: x.value.get('primary') == True)

    @property
    def primary_department(self):
        location = self.primary_location
        if location:
            departments = location.value.get('departments', [])
            return utils.true_or_nth(departments, lambda x: x.get('primary') == True)
        return None

    @property
    def primary_phone(self):
        department = self.primary_department
        if department:
            phones = self.primary_department.get('phones', [])
            return utils.nth(phones, 0)
        return None

    @property
    def primary_opening_times(self):
        location = self.primary_location
        if location:
            return location.value.get('opening_times')
        return None

    @property
    def primary_opening_today(self):
        opening_times = self.primary_opening_times
        if opening_times:
            today = date.today()
            specific_times = utils.first_true(opening_times, lambda x: x.get('date') == today)
            return specific_times or utils.first_true(opening_times, lambda x: x.get('weekday') == today.weekday())
        return None


class SocialMediaSetting(BaseSetting):

    class Meta:
        abstract = True

    profiles = fields.StreamField([
        ('profile', extension_blocks.SocialMediaProfileBlock()),
    ])

    panels = (
        StreamFieldPanel('profiles'),
    )
