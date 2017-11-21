from datetime import date

from django.core.cache import cache
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

    CACHE_KEY_OPENING_TODAY = "wagtail_extensions_opening_today_{:%Y%m%d}"

    locations = fields.StreamField([
        ('location', extension_blocks.LocationBlock()),
    ])

    panels = (
        StreamFieldPanel('locations'),
    )

    class Meta:
        abstract = True

    @classmethod
    def get_opening_today_cache_key(cls, date):
        return cls.CACHE_KEY_OPENING_TODAY.format(date)

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
        today = date.today()
        cache_key = self.get_opening_today_cache_key(today)
        times = cache.get(cache_key)
        if times is not None:
            opening_times = self.primary_opening_times
            if opening_times:
                specific_times = utils.first_true(opening_times, lambda x: x.get('date') == today)
                times = specific_times or utils.first_true(opening_times, lambda x: x.get('weekday') == today.weekday())
                cache.set(cache_key, times, 60*60*24)
        return times
